import os
import sys
import pprint
import urllib3
import kubernetes
import inspect
import re
import time
import json
import templateslib
import kubetools
import resourcescanner

VERSION = '1.0.1'

def mergeTrees(a, b, override=False):
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergeTrees(a[key], b[key], override=override)
            elif a[key]!=b[key]:
                if override:
                    a[key] = b[key]
                else:
                    raise Exception('Tree merge conflict: %s vs %s' % (a[key], b[key]))
        else:
            a[key] = b[key]
    return a


class Controller(object):

    def __init__(self, args):
        self.lastActivity = time.time()
        self.group, self.version, self.resourceName, self.resourcePlural = kubetools.findCrd(args.crdName)
        if args.resourceName!='':
            self.resourceName = args.resourceName
        self.defaultNamespace = args.namespace
        self.namespacePath = args.namespacePath
        self.noAction = args.noAction
        self.templates = templateslib.TemplatesLib(args.yamlPath, self.resourceName, tracebackLabel=args.tracebackLabel)
        self.loopTimeout = args.loopTimeout
        self._initScanner(args)

    def _initScanner(self, args):
        if args.tracebackLabel is None:
            self.scanner = None
            return
        self.tracebackLabel = args.tracebackLabel
        self.scanner = resourcescanner.ResourceScanner()
        apis = self.scanner.getAllAPIs(preferredOnly=True)
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
        Return list of tuples: (api, kind, name) or None if scanner is off
        """
        if self.scanner is None:
            return None
        list = []
        for kind in self.allKindsMap:
            resources = self.scanner.getAllResources(self.allKindsMap[kind][0][0], self.allKindsMap[kind][0][1], queryParams=[('labelSelector', self.tracebackLabel+'='+parentName)])
            for r in resources:
                api = self.allKindsMap[kind][0][0]
                if api.startswith('api/') or api.startswith('apis/'):
                    api = api.split('/', 1)[1]
                list.append((api, kind, r['metadata']['name']))
        return list

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

    def _rememberResource(self, resourcesList, resource):
        info = (
            kubetools.getYamlValue(resource, '/apiVersion'),
            kubetools.getYamlValue(resource, '/kind'),
            kubetools.getYamlValue(resource, '/metadata/name'),
        )
        if info not in resourcesList:
            resourcesList.append(info)

    def _forgetResource(self, resourcesList, resource):
        info = (
            kubetools.getYamlValue(resource, '/apiVersion'),
            kubetools.getYamlValue(resource, '/kind'),
            kubetools.getYamlValue(resource, '/metadata/name'),
        )
        while True:
            try:
                resourcesList.remove(info)
            except ValueError:
                return

    def update(self, masterYaml):
        result = {
            'conditionPatch': {
                'creates': 0,
                'updates': 0,
                'deletes': 0,
            },
            'statusPatch': {
                'alteredResources': [],
            },
        }
        if self.namespacePath=='':
            namespace = self.defaultNamespace
        else:
            namespace = kubetools.getYamlValue(masterYaml, self.namespacePath, self.defaultNamespace)
        yamls = self.templates.applyAllTemplates(masterYaml)
        for y in yamls:
            # Apply status patches
            patch = kubetools.getYamlValue(y, '/metadata/annotations/'+self.resourceName+'Def/statusPatch')
            if patch is not None:
                mergeTrees(result['statusPatch'], patch)
            self.templates.stripAnnotations(y)
            # Check if resource is already created
            try:
                self._dynamicApiCall('read', namespace, y)
            except kubernetes.client.rest.ApiException:
                # Not found - create it
                kubetools.logInfo(' * Creating %s %s...' % (y['kind'], kubetools.getYamlValue(y, '/metadata/name')))
                result['conditionPatch']['creates'] += 1
                self._rememberResource(result['statusPatch']['alteredResources'], y)
                self._dynamicApiCall('create', namespace, y, yamlBody=y)
                continue
            # Found - update it
            if y['kind'] in ['Deployment', 'StatefulSet', 'ConfigMap', 'Ingress', 'HorizontalPodAutoscaler']: #TODO: better diff
                kubetools.logInfo(' * Updating %s %s...' % (y['kind'], kubetools.getYamlValue(y, '/metadata/name')))
                result['conditionPatch']['updates'] += 1
                self._rememberResource(result['statusPatch']['alteredResources'], y)
                self._dynamicApiCall('replace', namespace, y, yamlBody=y)
            else:
                self._rememberResource(result['statusPatch']['alteredResources'], y)
                kubetools.logInfo(' * Skipping %s %s...' % (y['kind'], kubetools.getYamlValue(y, '/metadata/name')))
        # Verify resources already in cluster, delete what's left
        foundResourcesList = self._scanResources(kubetools.getYamlValue(masterYaml, 'metadata/name'))
        if foundResourcesList is not None:
            # Remove (*, kind, name) from foundResourcesList for each (*, kind, name) in alteredResources
            for rApi, rKind, rName in result['statusPatch']['alteredResources']:
                foundResourcesList = [(rA, rK, rN) for rA, rK, rN in foundResourcesList if (rK!=rKind) or (rN!=rName)]
            # Delete resources listed in foundResourcesList
            for rApi, rKind, rName in foundResourcesList:
                result['conditionPatch']['deletes'] += 1
                self._deleteResource(namespace, {
                    'kind': rKind,
                    'apiVersion': rApi,
                    'metadata': {'name': rName},
                })
        return result

    def _deleteResource(self, namespace, resource):
        kubetools.logInfo(' * Deleting %s %s (%s)...' % (resource['kind'], kubetools.getYamlValue(resource, '/metadata/name'), resource['apiVersion']))
        try:
            self._dynamicApiCall('delete', namespace, resource, yamlBody={})
        except kubernetes.client.rest.ApiException as e:
            kubetools.logInfo('   Ignoring: %s %s' % (e.status, e.reason)) # Conflict may happen here, when trying to delete already terminating resource

    def delete(self, masterYaml):
        if self.namespacePath=='':
            namespace = self.defaultNamespace
        else:
            namespace = kubetools.getYamlValue(masterYaml, self.namespacePath, self.defaultNamespace)
        foundResourcesList = self._scanResources(kubetools.getYamlValue(masterYaml, 'metadata/name'))
        if foundResourcesList is None:
            foundResourcesList = []
        for rApi, rKind, rName in kubetools.getYamlValue(masterYaml, 'status/alteredResources', []):
            for rA, rK, rN in foundResourcesList:
                if (rK==rKind) and (rN==rName):
                    break
            else:
                kubetools.logInfo('  Resource was in alteredResources list but not in etcd scan. Adding to deletion list: %s/%s %s' % (rApi, rKind, rName))
                foundResourcesList.append((rApi, rKind, rName))
        for rApi, rKind, rName in foundResourcesList:
            self._deleteResource(namespace, {
                'kind': rKind,
                'apiVersion': rApi,
                'metadata': {'name': rName},
            })

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
                    kubetools.logInfo('  Retrying update')
                    try:
                        res = crdApi.replace_cluster_custom_object(self.group, self.version, self.resourcePlural, name, obj)
                    except kubernetes.client.rest.ApiException as e:
                        if e.status==409:
                            kubetools.logInfo('  Still in conflict, giving up: %s' % str(e))
                            return None
                        else:
                            raise e
                else:
                    kubetools.logInfo('  resourceVersion changed: %s => %s, giving up' % (objResVersion, kubetools.getYamlValue(newObj, '/metadata/resourceVersion', 0)))
                    return None
            else:
                raise e
        newResourceVersion = kubetools.getYamlValue(res, '/metadata/resourceVersion', 0)
        kubetools.logInfo('  Got new resourceVersion: %s' % newResourceVersion)
        return newResourceVersion

    def controllerLoop(self):
        crdApi = kubernetes.client.CustomObjectsApi()
        eventResourceVersion = ''
        kubetools.logBold('Controller version: %s (yamls hash=%s)' % (VERSION, self.templates.hash))
        kubetools.logBold('Used environment: (hash=%s)' % self.templates.envMapHash)
        for e in self.templates.envMap:
            kubetools.logInfo(' %s: "%s"' % (e, self.templates.envMap[e]))
        kubetools.logBold('Monitoring resources: %s/%s %s' % (self.group, self.version, self.resourcePlural))
        while True:
            self.lastActivity = time.time()
            try:
                kubetools.logInfo('Waiting for events')
                stream = kubernetes.watch.Watch().stream(crdApi.list_cluster_custom_object, self.group, self.version, self.resourcePlural, resource_version=eventResourceVersion, timeout_seconds=self.loopTimeout)
                for event in stream:
                    kubetools.logDebug(' Processing event')
                    self.lastActivity = time.time()
                    operation = event['type']
                    if operation!='ERROR':
                        name = kubetools.getYamlValue(event, '/object/metadata/name')
                        if name is None:
                            kubetools.logInfo('Invalid event: %s' % event)
                        eventResourceVersion = kubetools.getYamlValue(event, '/object/metadata/resourceVersion')
                        obj = self._getMainResource(crdApi, name) # This IS needed to quickly step over all intermediate updates
                        resourceVersion = kubetools.getYamlValue(obj, '/metadata/resourceVersion')
                    if operation=='DELETED':
                        kubetools.logBold('Deleting %s (eventResourceVersion=%s)' % (name, eventResourceVersion))
                        if obj is None:
                            try:
                                self.delete(event['object'])
                                kubetools.logInfo(' Deleted')
                            except templateslib.TemplateValueError as e:
                                kubetools.logBold(' Error: %s' % str(e))
                        else:
                            kubetools.logInfo(' Still present, skipping (resourceVersion=%s, eventResourceVersion=%s)' % (resourceVersion, eventResourceVersion))
                    elif (operation=='ADDED') or (operation=='MODIFIED'):
                        kubetools.logBold('Modifying %s (op=%s, resourceVersion=%s, eventResourceVersion=%s)' % (name, operation, resourceVersion, eventResourceVersion))
                        if obj is None:
                            kubetools.logInfo(' Resource is gone, skipping') # They killed Kenny!
                        else:
                            lastSpec = kubetools.getYamlValue(obj, '/metadata/annotations/lastSpec', '')
                            newSpec = json.dumps(obj['spec'], sort_keys=True)
                            diff = []
                            if lastSpec!=newSpec:
                                diff.append('spec')
                            if kubetools.getYamlValue(obj, '/metadata/annotations/controllerVer', '')!=VERSION:
                                diff.append('controllerVer')
                            if kubetools.getYamlValue(obj, '/metadata/annotations/controllerHash', '')!=self.templates.hash:
                                diff.append('controllerHash')
                            if kubetools.getYamlValue(obj, '/metadata/annotations/controllerEnvHash', '')!=self.templates.envMapHash:
                                diff.append('envHash')
                            processedCond = kubetools.findCondition(obj, 'Processed')
                            if (processedCond is not None) and (processedCond['status']!='True'):
                                diff.append('processing')
                                kubetools.logInfo(' Unexpected Processed condition state, triggering update: %s/%s "%s"' % (processedCond['status'], processedCond['reason'], processedCond['message']))
                            if diff==[]:
                                kubetools.logInfo(' No change detected, skipping')
                            else:
                                kubetools.logDebug(' Diff: %s' % (','.join(diff)))
                                kubetools.setConditionRec(obj, 'Processed', 'False', 'InProgress')
                                newResourceVersion = self._updateMainResource(crdApi, obj)
                                if newResourceVersion is None:
                                    kubetools.logBold(' Condition update conflict, aborting (no actions taken, will retry in next loop, we\'re safe)') # This is a race condition over a very short moment. Not worth fighting for
                                else:
                                    try:
                                        updateResult = self.update(obj) # This call can take some time to complete
                                        updateResult['reason'] = None
                                        updateResult['message'] = ''
                                    except kubernetes.client.rest.ApiException as e:
                                        updateResult = {
                                            'reason': 'InternalError',
                                            'message': str(e),
                                            'conditionPatch': {},
                                            'statusPatch': {},
                                        }
                                    except templateslib.TemplateValueError as e:
                                        updateResult = {
                                            'reason': 'Error',
                                            'message': str(e),
                                            'conditionPatch': {},
                                            'statusPatch': {},
                                        }
                                    if updateResult['reason'] is not None:
                                        kubetools.logBold(' Exception: %s / %s' % (updateResult['reason'], updateResult['message']))
                                    # Reget the object to update resourceVersion
                                    obj = self._getMainResource(crdApi, name)
                                    if obj is None:
                                        kubetools.logBold(' Can not reget object. Aborting status update - alteredResources desync possible') # TODO: alteredResources may desync here
                                    else:
                                        if newResourceVersion!=kubetools.getYamlValue(obj, '/metadata/resourceVersion', '?'):
                                            kubetools.logDebug('  Avoided resourceVersion race: expected=%s, got=%s' % (newResourceVersion, kubetools.getYamlValue(obj, '/metadata/resourceVersion', '?')))
                                        if 'annotations' not in obj['metadata']:
                                            obj['metadata']['annotations'] = {}
                                        obj['metadata']['annotations']['lastSpec'] = newSpec
                                        obj['metadata']['annotations']['controllerVer'] = VERSION
                                        obj['metadata']['annotations']['controllerHash'] = self.templates.hash
                                        obj['metadata']['annotations']['controllerEnvHash'] = self.templates.envMapHash
                                        if 'status' not in obj:
                                            obj['status'] = {}
                                        mergeTrees(obj['status'], updateResult['statusPatch'], override=True)
                                        kubetools.setConditionRec(obj, 'Processed', 'True', 'NoProblemsDetected' if updateResult['reason'] is None else updateResult['reason'], message=updateResult['message'], extraFields=updateResult["conditionPatch"])
                                        newResourceVersion = self._updateMainResource(crdApi, obj)
                                        if newResourceVersion is None:
                                            kubetools.logBold(' Condition update conflict, aborting update - alteredResources desync possible')
                    else: # 'ERROR'
                        kubetools.logInfo('Ignoring event %s %s "%s"' % (operation, obj['reason'] if 'reason' in obj else '[no reason]', obj['message'] if 'message' in obj else '[no message]'))
                        eventResourceVersion = ''
            except urllib3.exceptions.ProtocolError:
                kubetools.logInfo('Ignored urllib3.exceptions.ProtocolError')
            except Exception as e:
                kubetools.logBold('=== Exception: %s' % str(e))
                raise
            kubetools.logInfo('Restarting loop (eventResourceVersion=%s)' % (eventResourceVersion))

    def checkForProblems(self):
        lag = int(time.time() - self.lastActivity)
        if lag<self.loopTimeout+60:
            return None
        return 'Stalled for %s seconds' % lag

    def directCreate(self, fName):
        obj = kubetools.loadYamlFile(fName)
        try:
            updateResult = self.update(obj)
        except templateslib.TemplateValueError as e:
            kubetools.logBold('Error: %s' % str(e))
        else:
            kubetools.logDebug(pprint.pformat(updateResult))

    def directDelete(self, fName):
        obj = kubetools.loadYamlFile(fName)
        try:
            self.delete(obj)
        except templateslib.TemplateValueError as e:
            kubetools.logBold('Error: %s' % str(e))
