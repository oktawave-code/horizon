import os
import sys
import pprint
import urllib3
import kubernetes
import inspect
import re
import datetime
import time
import json
import kubetools
import resourcescanner

class Controller(object):

    def __init__(self, args):
        self.group, self.version, self.resourceName, self.resourcePlural = kubetools.findCrd(args.crdName)
        self.defaultNamespace = args.namespace
        self.namespacePath = args.namespacePath
        self.noAction = args.noAction
        self._initScanner(args)

    def _initScanner(self, args):
        if args.tracebackLabel is None:
            self.scanner = None
            return
        self.tracebackLabel = args.tracebackLabel
        self.scanner = resourcescanner.ResourceScanner()
        apis = self.scanner.getAllAPIs(preferredOnly=True);
        kindsMap = {}
        for api in apis:
            kinds = self.scanner.getAllAPIKinds(api, onlyTopLevel=True, excludedKinds=args.excludedKinds.split(','))
            for kind, resource in kinds:
                if kind not in kindsMap:
                    kindsMap[kind] = []
                kindsMap[kind].append((api, resource))
        kubetools.logInfo('Cached %d kinds' % (len(kindsMap)))
        self.allKindsMap = kindsMap

    def _scanResources(self, parentName):
        """
        Return list of tuples: (kind, name)
        """
        if self.scanner is None:
            return None
        list = []
        for kind in self.allKindsMap:
            resources = self.scanner.getAllResources(self.allKindsMap[kind][0][0], self.allKindsMap[kind][0][1], queryParams=[('labelSelector', self.tracebackLabel+'='+parentName)])
            for r in resources:
                list.append((kind, r['metadata']['name']))
        return list

    def _scanPods(self):
        if self.scanner is None:
            return None
        return self.scanner.getAllResources('api/v1', 'pods')

    def _getApiByVersion(self, apiVersion):
        parts = apiVersion.split('/')
        if len(parts)==1:
            parts = ['core']+parts
        parts[1] = parts[1].capitalize()
        if re.search('k8s.io', parts[0]):
            np = parts[0].replace('.k8s.io', '').split('.')
            parts[0] = ''.join([w.capitalize() for w in np])
        else:
            parts[0] = parts[0].split('.')[0].capitalize()
        return ''.join([w for w in parts])+'Api'

    def _dynamicApiCall(self, methodNamePrefix, namespace, metadata, yamlBody=None, labelSelector=None):
        apiName = self._getApiByVersion(metadata['apiVersion'])
        api = getattr(kubernetes.client, apiName)() # Will throw AttributeError if unknown apiVersion was given
        kindName = re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', metadata['kind'])).lower()
        methodName = methodNamePrefix+'_'+kindName
        try:
            method = getattr(api, methodName)
        except AttributeError:
            methodName = methodNamePrefix+'_namespaced_'+kindName
            method = getattr(api, methodName) # Will throw AttributeError if unknown kind was given
        methodArgs = inspect.getargspec(method).args
        args = {}
        if yamlBody is not None:
            if 'body' in methodArgs:
                args['body'] = yamlBody
            else:
                kubetools.logDebug('  Skipping body - patch for bugged kubernetes api?')
        if 'namespace' in methodArgs:
            args['namespace'] = namespace
        if 'name' in methodArgs:
            args['name'] = metadata['metadata']['name']
        if  labelSelector is not None:
            args['label_selector'] = labelSelector
        if kubetools.logLevel>=kubetools.LOG_SPAM:
            kubetools.logSpam('   Calling %s.%s(%s)' % (apiName, methodName, json.dumps(args, sort_keys=True)))
        else:
            kubetools.logDebug('   Calling %s.%s(...)' % (apiName, methodName))
        if self.noAction and methodNamePrefix not in ['read', 'list']:
            return None
        return method(**args)

    def _getMainResource(self, crdApi, name, retries=3):
        for i in xrange(retries):
            try:
                obj = crdApi.get_cluster_custom_object(self.group, self.version, self.resourcePlural, name)
                return obj
            except kubernetes.client.rest.ApiException as e:
                if e.status==404:
                    return None # Not found, no need to retry
                kubetools.logInfo('   Failed to get resource: %s' % str(e))
        kubetools.logInfo('  Failed to get resource, giving up')
        return None # Nothing can be done

    def _updateMainResource(self, crdApi, obj):
        """
        return newResourceVersion if resource was modified (None on conflict, if it is ignored)
        """
        objResVersion = kubetools.getYamlValue(obj, '/metadata/resourceVersion', 0)
        if self.noAction:
            return objResVersion
        name = kubetools.getYamlValue(obj, '/metadata/name')
        kubetools.logInfo(' Updating CRD %s' % name)
        try:
            res = crdApi.replace_cluster_custom_object(self.group, self.version, self.resourcePlural, name, obj)
        except kubernetes.client.rest.ApiException as e:
            if e.status==409:
                newObj = self._getMainResource(crdApi, name)
                if (newObj is None) or (objResVersion==kubetools.getYamlValue(newObj, '/metadata/resourceVersion', 0)):
                    if newObj is None:
                        kubetools.logDebug('  Can not reget')
                    else:
                        kubetools.logDebug('  resourceVersion not changed after reget: %s' % objResVersion)
                    kubetools.logDebug('  Retrying update')
                    try:
                        res = crdApi.replace_cluster_custom_object(self.group, self.version, self.resourcePlural, name, obj)
                    except kubernetes.client.rest.ApiException as e:
                        if e.status==409:
                            kubetools.logDebug('  Still in conflict, giving up: %s' % str(e))
                            return None
                        else:
                            raise e
                else:
                    kubetools.logDebug('  resourceVersion changed: %s => %s, giving up' % (objResVersion, kubetools.getYamlValue(newObj, '/metadata/resourceVersion', 0)))
                    return None
            else:
                raise e
        newResourceVersion = kubetools.getYamlValue(res, '/metadata/resourceVersion', 0)
        kubetools.logDebug('  Got new resourceVersion: %s' % newResourceVersion)
        return newResourceVersion

    def aggregateStatus(self, masterYaml, allPods):
        if self.namespacePath=='':
            namespace = self.defaultNamespace
        else:
            namespace = kubetools.getYamlValue(masterYaml, self.namespacePath, self.defaultNamespace)
        podsInfo = []
        if allPods is not None:
            nsPods = [pod for pod in allPods if kubetools.getYamlValue(pod, 'metadata/namespace')==namespace]
            conditionsToCheck = ['PodScheduled', 'Ready', 'Initialized', 'Unschedulable', 'ContainersReady']
            for pod in nsPods:
                pInfo = {
                    'name': kubetools.getYamlValue(pod, 'metadata/name'),
                    'phase': kubetools.getYamlValue(pod, 'status/phase'),
                }
                for cond in conditionsToCheck:
                    condRec = kubetools.findCondition(pod, cond)
                    if condRec is None:
                        pInfo[cond] = {
                            'status': 'Unknown',
                            'reason': '',
                            'message': '',
                        }
                    else:
                        pInfo[cond] = {
                            'status': condRec['status'],
                            'reason': condRec['reason'] if 'reason' in condRec else '',
                            'message': condRec['message'] if 'message' in condRec else '',
                        }
                podsInfo.append(pInfo)
        resourcesList = kubetools.getYamlValue(masterYaml, 'status/alteredResources')
        if resourcesList is None:
            return (False, 'NoAlteredResourcesLists', 'Resource not ready for watching', podsInfo)
        resourcesList = list(set([(rApi, rKind, rName) for rApi, rKind, rName in resourcesList])) # remove duplicates
        foundResourcesList = self._scanResources(kubetools.getYamlValue(masterYaml, 'metadata/name'))
        for rApi, rKind, rName in resourcesList:
            if foundResourcesList is not None:
                try:
                    foundResourcesList.remove((rKind, rName))
                except ValueError:
                    kubetools.logDebug('   Resource not found in scan list: %s / %s -> False' % (rKind, rName))
                    return (False, 'MissingResource', 'Resource %s not deployed' % rName, podsInfo)
            try:
                resource = self._dynamicApiCall('read', namespace, {
                    'apiVersion': rApi,
                    'kind': rKind,
                    'metadata': {
                        'name': rName,
                    }
                })
            except kubernetes.client.rest.ApiException:
                kubetools.logDebug('   Missing resource -> False')
                return (False, 'MissingResource', 'Resource %s not deployed' % rName, podsInfo)
            if rKind in ['ReplicationController', 'ReplicaSet', 'StatefulSet']:
                if kubetools.getYamlValue(resource, '/status/ready_replicas', 0)<kubetools.getYamlValue(resource, '/status/replicas', 1):
                    kubetools.logDebug('   Not enough replicas -> False')
                    return (False, 'NotEnoughReplicas', 'Resource %s has not enough replicas' % rName, podsInfo)
            elif rKind in ['Deployment']:
                condition = kubetools.findCondition(resource, 'Available')
                if condition is None:
                    kubetools.logDebug('   No available condition -> None')
                    return ('UnknownAvailability', 'Resource %s has no "Available" condition' % rName, podsInfo)
                else:
                    if condition.status=='False':
                        kubetools.logDebug('   Available status is False -> False')
                        return (False, 'NotAvailable', 'Resource %s is not available' % rName, podsInfo)
                    elif condition.status!='True':
                        kubetools.logDebug('   Available status neither True or False -> None')
                        return ('InvalidAvailability', 'Resource %s has invalid "Available" condition status' % rName, podsInfo)
        if (foundResourcesList is not None) and (len(foundResourcesList)>0):
            for rKind, rName in foundResourcesList:
                kubetools.logDebug('   Resource lost: %s / %s' % (rKind, rName))
            return (True, 'LostResourcesFound', 'Found %s resources not referenced in alteredResources' % len(foundResourcesList), podsInfo)
        return (True, 'NoProblemsDetected', '', podsInfo)

    def updateAllStatuses(self, crdApi):
        allPods = self._scanPods();
        objects = crdApi.list_cluster_custom_object(self.group, self.version, self.resourcePlural)['items']
        kubetools.logInfo('Performing scan of %d resources' % len(objects))
        if allPods is not None:
            kubetools.logInfo(' Cached %d pods from entire cluster' % len(allPods))
        for obj in objects:
            cond = kubetools.findCondition(obj, 'Processed')
            if (cond is None) or (cond['status']!='True'):
                kubetools.logInfo(' Skipping not processed resource: %s (resourceVersion=%s)' % (kubetools.getYamlValue(obj, '/metadata/name'), kubetools.getYamlValue(obj, '/metadata/resourceVersion')))
            else:
                kubetools.logInfo(' Verifying status for: %s (resourceVersion=%s)' % (kubetools.getYamlValue(obj, '/metadata/name'), kubetools.getYamlValue(obj, '/metadata/resourceVersion')))
                try:
                    status, reason, message, podsInfo = self.aggregateStatus(obj, allPods) # This call may take some time
                except Exception as e:
                    raise
                    kubetools.logBold(' Error: %s' % str(e))
                    status = False
                    reason = 'ControllerError'
                    message = str(e)
                    podsInfo = None
                status = 'Unknown' if status==None else str(status)
                newObj = self._getMainResource(crdApi, kubetools.getYamlValue(obj, '/metadata/name')) # This IS needed to quickly step over all intermediate updates
                if newObj is None:
                    kubetools.logBold(' Object dissapeared, ignoring update')
                else:
                    changed = kubetools.setConditionRec(obj, 'Available', status, reason, message=message)
                    if podsInfo is not None:
                        lCurrent = [json.dumps(pi, separators=(',', ':'), sort_keys=True) for pi in podsInfo]
                        lNew = [json.dumps(pi, separators=(',', ':'), sort_keys=True) for pi in kubetools.getYamlValue(obj, 'status/podsInfo', [])]
                        diff = set(lCurrent).symmetric_difference(lNew)
                        if len(diff)>0:
                            kubetools.logInfo('  Found %d differences in pod states' % len(diff))
                            obj['status']['podsInfo'] = podsInfo
                            changed = True
                    if changed:
                        if self._updateMainResource(crdApi, obj) is None:
                            kubetools.logBold(' Condition update conflict, aborting update (should autoheal in next cycle)')

    def watcherLoop(self, loopFrequency=30):
        crdApi = kubernetes.client.CustomObjectsApi()
        kubetools.logBold('Testing resources: %s/%s %s' % (self.group, self.version, self.resourcePlural))
        while True:
            t0 = time.time()
            self.updateAllStatuses(crdApi)
            dt = time.time()-t0
            kubetools.logDebug(' Testing loop took %d seconds' % dt)
            if dt<loopFrequency:
                kubetools.logInfo(' Sleeping %d' % (loopFrequency-dt))
                time.sleep(loopFrequency-dt)
