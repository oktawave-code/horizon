import urllib3
import kubernetes
import time
import metrics
import re
import kubetools
import datetime

class Controller(object):

    def __init__(self, args):
        self.defs = kubetools.loadYamlFile(args.defsYaml)
        self.noAction = args.noAction
        self.minActionAge = args.minActionAge
        self.group = kubetools.getYamlValue(self.defs, '/resource/group')
        self.version = kubetools.getYamlValue(self.defs, '/resource/version')
        self.resourceName = kubetools.getYamlValue(self.defs, '/resource/names/singular')
        self.resourcePlural = kubetools.getYamlValue(self.defs, '/resource/names/plural', self.resourceName+'s')
        self.namespacePath = kubetools.getYamlValue(self.defs, '/resource/namespacePath')
        self.crdApi = kubernetes.client.CustomObjectsApi()
        self.rmApi = metrics.ResourceMetrics()
        self.cmApi = metrics.CustomMetrics()
        kubetools.logInfo('minActionAge = %s' % self.minActionAge)

    def _updateMainResource(self, obj):
        if self.noAction:
            return kubetools.getYamlValue(obj, '/metadata/resourceVersion', 0)
        name = kubetools.getYamlValue(obj, '/metadata/name')
        kubetools.logInfo(' Updating CRD %s' % name)
        try:
            res = self.crdApi.replace_cluster_custom_object(self.group, self.version, self.resourcePlural, name, obj)
        except kubernetes.client.rest.ApiException as e:
            if e.status==409: # Skip conflict, as it seems to be "noise" signal
                return None
            else:
                raise e
        newResourceVersion = kubetools.getYamlValue(res, '/metadata/resourceVersion', 0)
        kubetools.logDebug('  Got new resourceVersion: %s' % newResourceVersion)
        return newResourceVersion

    def scanAllResources(self):
        objects = self.crdApi.list_cluster_custom_object(self.group, self.version, self.resourcePlural)['items']
        for obj in objects:
            objNamespace = kubetools.getYamlValue(obj, self.namespacePath)
            failedConditions = []
            if 'conditions' in self.defs:
                for c in self.defs['conditions']:
                    cond = kubetools.findCondition(obj, c['type'])
                    if (cond is None) or (cond['status']!=c['status']):
                        failedConditions.append(c['type']+'!='+c['status'])
            if failedConditions!=[]:
                kubetools.logBold(' Skipping: %s (resourceVersion=%s, namespace=%s) - failed conditions: %s' % (kubetools.getYamlValue(obj, '/metadata/name'), kubetools.getYamlValue(obj, '/metadata/resourceVersion'), objNamespace, ', '.join(failedConditions)))
                continue
            aCond = kubetools.findCondition(obj, 'Autoscaled')
            age = None
            if aCond is not None:
                try:
                    lastUpdate = datetime.datetime.strptime(aCond['lastUpdateTime'][:19], '%Y-%m-%dT%H:%M:%S')
                    age = (datetime.datetime.now()-lastUpdate).total_seconds()
                except ValueError:
                    age = None
            kubetools.logBold(' Scanning: %s (resourceVersion=%s, namespace=%s, age=%s)' % (kubetools.getYamlValue(obj, '/metadata/name'), kubetools.getYamlValue(obj, '/metadata/resourceVersion'), objNamespace, age))
            modified = []
            for scaleDef in self.defs['scale']:
                if scaleDef['type']=='single':
                    records = [kubetools.getYamlValue(obj, scaleDef['base'])]
                    scaleDescr = scaleDef['base']+'/'+scaleDef['variable']
                elif scaleDef['type']=='list':
                    records = kubetools.getYamlValue(obj, scaleDef['base'])
                    scaleDescr = scaleDef['base']+'/*/'+scaleDef['variable']
                else:
                    raise ValueError('Unknown scale type: %s' % scaleDef['type'])
                for rec in records:
                    options = kubetools.getYamlValue(rec, scaleDef['options'])
                    if options is None:
                        kubetools.logInfo('  Variable %s = %s - no options, scaling disabled' % (scaleDescr, kubetools.getYamlValue(rec, scaleDef['variable'])))
                    elif (age is not None) and (age<self.minActionAge):
                        kubetools.logInfo('  Variable %s = %s - too early to scale' % (scaleDescr, kubetools.getYamlValue(rec, scaleDef['variable'])))
                    else:
                        if 'optionRange' in scaleDef:
                            if 'min' not in options:
                                raise ValueError('Missing "min" in options')
                            if 'max' not in options:
                                raise ValueError('Missing "max" in options')
                            kubetools.logInfo('  Variable %s = %s, options: [%s..%s], metric: %s%s' % (scaleDescr, kubetools.getYamlValue(rec, scaleDef['variable']), options['min'], options['max'], scaleDef['metric']['type'], ('/'+scaleDef['metric']['name']) if 'name' in scaleDef['metric'] else ''))
                        else:
                            kubetools.logInfo('  Variable %s = %s, options: [%s], metric: %s%s' % (scaleDescr, kubetools.getYamlValue(rec, scaleDef['variable']), ','.join(options), scaleDef['metric']['type'], ('/'+scaleDef['metric']['name']) if 'name' in scaleDef['metric'] else ''))
                        total = 0
                        if scaleDef['metric']['type']=='Resource':
                            try:
                                pods = self.rmApi.getNamespacePodMetrics(objNamespace)['items']
                            except kubernetes.client.rest.ApiException as e:
                                if e.status!=404:
                                    raise
                                kubetools.logDebug('   Kubernetes API returned 404')
                                pods = []
                            cnt = 0
                            for pod in pods:
                                mask = re.sub('\(\((.+?)\)\)', lambda match: kubetools.getYamlValue(rec, match.group(1)), scaleDef['metric']['pods'])
                                if re.match(mask, kubetools.getYamlValue(pod, 'metadata/name')):
                                    for container in pod['containers']:
                                        v = container['usage'][scaleDef['metric']['name']]
                                        kubetools.logSpam('   Value: %s' % v)
                                        total += kubetools.parseValue(v)
                                        cnt += 1
                            kubetools.logInfo('   Scanned %d pods, cumulative %s: %s' % (cnt, scaleDef['metric']['name'], total))
                        elif scaleDef['metric']['type']=='Pod':
                            try:
                                pods = self.cmApi.getNamespacePodMetrics(objNamespace, scaleDef['metric']['name'])['items']
                            except kubernetes.client.rest.ApiException as e:
                                if e.status!=404:
                                    raise
                                kubetools.logDebug('   Kubernetes API returned 404')
                                pods = []
                            cnt = 0
                            for pod in pods:
                                mask = re.sub('\(\((.+?)\)\)', lambda match: kubetools.getYamlValue(rec, match.group(1)), scaleDef['metric']['pods'])
                                if re.match(mask, kubetools.getYamlValue(pod, 'describedObject/name')):
                                    v = pod['value']
                                    kubetools.logSpam('   Value: %s' % v)
                                    total += kubetools.parseValue(v)
                                    cnt += 1
                            kubetools.logInfo('   Scanned %d pods, cumulative %s: %s' % (cnt, scaleDef['metric']['name'], total))
                        elif scaleDef['metric']['type']=='Raw':
                            try:
                                items = self.cmApi.getNamespacedRawMetrics(objNamespace, scaleDef['metric']['path'])['items']
                            except kubernetes.client.rest.ApiException as e:
                                if e.status!=404:
                                    raise
                                kubetools.logDebug('   Kubernetes API returned 404')
                                items = []
                            cnt = 0
                            for item in items:
                                v = item['value']
                                kubetools.logSpam('   Value: %s' % v)
                                total += kubetools.parseValue(v)
                                cnt += 1
                            kubetools.logInfo('   Scanned %d items, cumulative value: %s' % (cnt, total))
                        elif scaleDef['metric']['type']=='Object':
                            pass # TODO
                        elif scaleDef['metric']['type']=='External':
                            pass # TODO
                        else:
                            raise ValueError('Unknown metric type: %s' % scaleDef['metric']['type'])
                        bestOpt = None
                        if 'optionRange' in scaleDef:
                            total *= scaleDef['optionRange']['multiplier']
                            total = int(total);
                            total = max(total, scaleDef['optionRange']['min']);
                            total = min(total, scaleDef['optionRange']['max']);
                            bestOpt = str(total);
                        else:
                            for opt in reversed(scaleDef['optionDefs']):
                                if opt['name'] in options:
                                    if (bestOpt is None) or (total<=opt['maxValue']):
                                        bestOpt = opt['name']
                        kubetools.logDebug('   Best option: %s' % bestOpt)
                        if bestOpt!=str(kubetools.getYamlValue(rec, scaleDef['variable'])):
                            kubetools.logBold('    Changing %s from %s to %s' % (scaleDescr, kubetools.getYamlValue(rec, scaleDef['variable']), bestOpt))
                            kubetools.setYamlValue(rec, scaleDef['variable'], bestOpt)
                            modified.append(scaleDef['name'])
            if modified!=[]:
                kubetools.setConditionRec(obj, 'Autoscaled', "True", 'Modified', message='Modified variables: '+(', '.join(modified)))
                self._updateMainResource(obj)

    def scalerLoop(self, loopFrequency=30):
        kubetools.logBold('Testing resources: %s/%s %s' % (self.group, self.version, self.resourcePlural))
        while True:
            t0 = time.time()
            self.scanAllResources()
            dt = time.time()-t0
            if dt<loopFrequency:
                kubetools.logDebug('  Sleeping')
                time.sleep(loopFrequency-dt)
