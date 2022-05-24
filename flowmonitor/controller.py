import os
import sys
import urllib3
import kubernetes
import re
import kubetools
import metrics
import math

class MetricError(ValueError):

    def __init__(self, *args):
        self.args = args

class Controller(object):

    def __init__(self, args):
        self.defs = kubetools.loadYamlFile(args.defsYaml)
        self.group = kubetools.getYamlValue(self.defs, '/resource/group')
        self.version = kubetools.getYamlValue(self.defs, '/resource/version')
        self.resourceName = kubetools.getYamlValue(self.defs, '/resource/names/singular')
        self.resourcePlural = kubetools.getYamlValue(self.defs, '/resource/names/plural', self.resourceName+'s')
        self.crdApi = kubernetes.client.CustomObjectsApi()
        self.cmApi = metrics.CustomMetrics()

    def getVal(self, valueDef, obj, recIndex, rec, vars={}):
        if valueDef['type']=='direct':
            v = kubetools.getYamlValue(obj, valueDef['path'])
            if v is None:
                raise MetricError('No value: %s' % valueDef['path'])
            return v
        elif valueDef['type']=='index':
            return recIndex
        elif valueDef['type']=='field':
            v = kubetools.getYamlValue(rec, valueDef['subpath'])
            if v is None:
                raise MetricError('No value: %s' % valueDef['subpath'])
            return v
        elif valueDef['type']=='const':
            return valueDef['value']
        elif valueDef['type']=='custom-metric':
            path = re.sub('\(\((.+?)\)\)', lambda match: vars[match.group(1)], valueDef['path'])
            try:
                m = self.cmApi.getRawMetrics(path)
            except kubernetes.client.rest.ApiException as e:
                raise MetricError('Api exception: %s %s' % (e.status, path))
            if ('items' not in m) or (len(m['items'])==0):
                raise MetricError('No items in api reply: %s' % path)
            return m['items'][0]['value']
        elif valueDef['type']=='calc':
            vars = {}
            env = {i:getattr(math, i) for i in dir(math) if not i.startswith('_')}
            for v in valueDef['vars']:
                vars[v['name']] = self.getVal(v, obj, recIndex, rec, vars)
                try:
                    env[v['name']] = kubetools.parseValue(vars[v['name']])
                except ValueError:
                    pass # non parsable values (strings, etc) will not be accessible for eval
            kubetools.logDebug('Eval: %s' % valueDef['formula'])
            try:
                v = eval(valueDef['formula'], env)
            except TypeError as e:
                raise MetricError('Type error: %s' % str(e))
            except ZeroDivisionError as e:
                raise MetricError('Zero division: %s' % str(e))
            return v
        raise ValueError('Unknown value type: %s' % valueDef['type'])

    def getStats(self):
        objects = self.crdApi.list_cluster_custom_object(self.group, self.version, self.resourcePlural)['items']
        stats = []
        for obj in objects: # for each monitored object
            objName = kubetools.getYamlValue(obj, '/metadata/name', '?')
            for recordDef in self.defs['records']: # for each metric to report
                if 'base' not in recordDef:
                    base = ''
                else:
                    base = recordDef['base']
                records = kubetools.getYamlValue(obj, base)
                if recordDef['type']=='single':
                    if isinstance(records, list):
                        raise ValueError('Record type set to single, but value is a list: %s' % recordDef['metric'])
                    if records is None:
                        records = []
                    else:
                        records = [records]
                elif recordDef['type']=='list':
                    if records is None:
                        records = []
                    if not isinstance(records, list):
                        raise ValueError('Record type set to list, but value is not a list: %s' % recordDef['metric'])
                else:
                    raise ValueError('Unknown record type: %s' % recordDef['type'])
                for recIndex, rec in enumerate(records): # for each record in monitored object
                    try:
                        v = self.getVal(recordDef['value'], obj, recIndex, rec)
                        try:
                            v = kubetools.parseValue(v)
                        except ValueError:
                            raise MetricError('Value error: %s' % v)
                        entry = {
                            'metric': recordDef['metric'],
                            'labels': {},
                            'value': v,
                        }
                        for labelDef in recordDef['labels']:
                            entry['labels'][labelDef['name']] = self.getVal(labelDef, obj, recIndex, rec)
                    except MetricError as e:
                        kubetools.logInfo('Metric problem (%s): %s ' % (objName, str(e)))
                    else:
                        stats.append(entry)
        return stats
