import datetime
import yaml
import os
import sys
import kubernetes

UNITS = [
    ('m', 0.001),
    ('K', 1000),
    ('Ki', 1024),
    ('M', 1000*1000),
    ('Mi', 1024*1024),
    ('G', 1000*1000*1000),
    ('Gi', 1024*1024*1024),
    ('T', 1000*1000*1000*1000),
    ('Ti', 1024*1024*1024*1024),
    ('P', 1000*1000*1000*1000*1000),
    ('Pi', 1024*1024*1024*1024*1024),
    ('E', 1000*1000*1000*1000*1000*1000),
    ('Ei', 1024*1024*1024*1024*1024*1024),
]

def parseValue(val):
    val = str(val)
    for unit in UNITS:
        if val.endswith(unit[0]):
            return float(val[:-len(unit[0])])*unit[1]
    return float(val)

LOG_SPAM = 4
LOG_DEBUG = 3
LOG_INFO = 2
LOG_BOLD = 1

logLevel = LOG_INFO

def _log(level, str):
    if level<=logLevel:
        print(str)
        sys.stdout.flush()

def logBold(str):
    _log(LOG_BOLD, str)

def logInfo(str):
    _log(LOG_INFO, str)

def logDebug(str):
    _log(LOG_DEBUG, str)

def logSpam(str):
    _log(LOG_SPAM, str)

def loadKubernetesConfig():
    if 'KUBERNETES_PORT' in os.environ:
        logBold('Loading incluster configuration')
        kubernetes.config.load_incluster_config()
    else:
        configFile = os.path.join(os.environ['HOME'], '.kube/config')
        logBold('Loading configuration from %s' % configFile)
        kubernetes.config.load_kube_config(configFile)

def loadYamlFile(fName):
    with open(fName, 'r') as f:
        yamlBody = yaml.load(f, Loader=yaml.loader.Loader)
    return yamlBody

def getYamlValue(yamlBody, path, default=None):
    if yamlBody is None:
        return default
    path = path.split('/')
    while True:
        try:
            dir = path.pop(0)
        except IndexError:
            return yamlBody
        if dir!='':
            try:
                try:
                    yamlBody = yamlBody[dir]
                except TypeError:
                    try:
                        yamlBody = yamlBody[int(dir)]
                    except:
                        yamlBody = getattr(yamlBody, dir)
            except KeyError:
                return default
            except AttributeError:
                return default

def setYamlValue(yamlBody, path, val):
    path = [d for d in path.split('/') if d!='']
    while True:
        dir = path.pop(0)
        if path==[]:
            yamlBody[dir] = val
            return
        try:
            try:
                yamlBody = yamlBody[dir]
            except TypeError:
                try:
                    yamlBody = yamlBody[int(dir)]
                except:
                    yamlBody = getattr(yamlBody, dir)
        except KeyError:
            yamlBody[dir] = {}
            yamlBody = yamlBody[dir]

def findCondition(resource, type):
    conditions = getYamlValue(resource, '/status/conditions') # AppsV1beta1DeploymentStatus objects use None as empty set
    if conditions is None:
        return None
    for c in conditions:
        if getYamlValue(c, 'type')==type:
            return c
    return None

def setConditionRec(resource, type, status, reason, message='', extraFields=None):
    """
    Return true if status was changed
    """
    if 'status' not in resource:
        resource['status'] = {}
    if ('conditions' not in resource['status']) or (resource['status']['conditions']==None):
        resource['status']['conditions'] = []
    t = datetime.datetime.now().isoformat()
    rec = findCondition(resource, type)
    changed = False
    if rec is not None:
        if status!=getYamlValue(rec, 'status', 'Unknown'):
            logInfo(' Condition status change for "%s"/%s: %s => %s' % (resource['metadata']['name'], type, getYamlValue(rec, 'status', 'Unknown'), status))
            changed = True
            rec['lastTransitionTime'] = t
        elif reason!=getYamlValue(rec, 'reason', ''):
            logInfo(' Condition reason change for "%s"/%s: (status=%s) %s => %s' % (resource['metadata']['name'], type, status, getYamlValue(rec, 'reason', ''), reason))
            changed = True
            rec['lastTransitionTime'] = t
        elif message!=getYamlValue(rec, 'message', ''):
            logInfo(' Condition message change for "%s"/%s: (status=%s, reason=%s) => %s' % (resource['metadata']['name'], type, status, reason, message))
            changed = True
            rec['lastTransitionTime'] = t
        else:
            logDebug(' Condition unchanged for "%s"/%s: status=%s, reason=%s' % (resource['metadata']['name'], type, status, reason))
    else:
        logInfo(' Condition status creation for "%s"/%s: status=%s, reason=%s' % (resource['metadata']['name'], type, status, reason))
        changed = True
        rec = {}
        rec['type'] = type
        rec['lastTransitionTime'] = t
        resource['status']['conditions'].append(rec)
    rec['lastUpdateTime'] = t
    rec['status'] = status
    rec['reason'] = reason
    rec['message'] = message
    if extraFields is not None:
        for f in extraFields:
            rec[f] = extraFields[f]
    return changed

def findCrd(name):
    apiClient = kubernetes.client.ApiClient()
    (data) = apiClient.call_api('/apis/apiextensions.k8s.io/v1beta1/customresourcedefinitions',
           'GET',
            {}, # path_params
            [], # query_params
            {}, # header_params
            body=None,
            post_params=[],
            files={},
            response_type='object',
            auth_settings=['BearerToken'],
            async_req=False,
            _return_http_data_only=True)
    import pprint
    for crd in data['items']:
        if (getYamlValue(crd, '/metadata/name')==name) or (getYamlValue(crd, '/spec/names/plural')==name) or (getYamlValue(crd, '/spec/names/singular')==name):
            group = getYamlValue(crd, '/spec/group')
            version = getYamlValue(crd, '/spec/version')
            resourceName = getYamlValue(crd, '/spec/names/singular')
            resourcePlural = getYamlValue(crd, '/spec/names/plural', resourceName+'s')
            return (group, version, resourceName, resourcePlural)
    logBold('Missing crd "%s"' % name)
    raise Exception('Custom resource "%s" not found. It must be created prior to running this controller' % name)
