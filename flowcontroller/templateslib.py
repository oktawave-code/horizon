import os
import yaml
import json
import hashlib
import collections
import re
import typejuggler
import kubetools

TAG_START = '(('
TAG_END = '))'
ENV_PREFIX = '@ENV['
ENV_SUFFIX = ']'
MAP_PREFIX = '@MAP['
MAP_SUFFIX = ']'

def _makeAbsolutePath(base, path):
    if not path.startswith('/'):
        path = base+'/'+path
    return path

class TemplateValueError(ValueError):

    def __init__(self, *args):
        self.args = args


class TemplatesLib(object):

    def __init__(self, yamlsPath, resourceName, tracebackLabel=None):
        self.yamlsPath = yamlsPath
        self.resourceName = resourceName
        self.tracebackLabel = tracebackLabel
        self.reloadFiles()

    def reloadFiles(self):
        fNames = [os.path.join(self.yamlsPath, fn) for fn in os.listdir(self.yamlsPath) if os.path.isfile(os.path.join(self.yamlsPath, fn)) and (fn.endswith('.yml') or fn.endswith('.yaml'))]
        fNames.sort() # make order deterministic
        self.files = []
        hashChain = ''
        for fn in fNames:
            yamlBody = kubetools.loadYamlFile(fn)
            self.files.append(yamlBody)
            hashChain += hashlib.md5(json.dumps(yamlBody, sort_keys=True)).hexdigest()
        self.hash = hashlib.md5(hashChain).hexdigest()
        self.envMap = self.getAllEnvReferences()
        self.envMapHash = hashlib.md5(json.dumps(self.envMap, sort_keys=True)).hexdigest()

    def stripAnnotations(self, yaml):
        a = kubetools.getYamlValue(yaml, 'metadata/annotations')
        if a is None:
            return
        if self.resourceName+'Def' in a:
            del a[self.resourceName+'Def']

    def _checkCondition(self, yaml, base, condition):
        """
        Condition format:
            "*" <path>               - key existence check
            "*" <path> "=" <value>   - key must exists and must have specified value
            <path> "=" <value>       - key may be missing or must have specified value
            "*" <path> "==" <value>  - key must exists and must have specified value
            <path> "==" <value>      - key may be missing or must have specified value
            "*" <path> "!=" <value>  - key must exists and must NOT have specified value
            <path> "!=" <value>      - key may be missing or must NOT have specified value
        """
        if condition is None:
            return True
        cSplit = condition.split('=', 1)
        if len(cSplit)==2:
            cPath = cSplit[0]
            if cPath[-1]=='!':
                cPath = cPath[:-1]
                cTest = '!='
            else:
                if cSplit[1][0]=='=':
                    cSplit[1] = cSplit[1][1:]
                cTest = '='
            cVal = cSplit[1].strip()
        else:
            cPath = condition
            cTest = '*'
            cVal = ''
        if cPath.startswith('*'):
            cMustHave = True
            cPath = cPath[1:]
        else:
            cMustHave = False
        val = kubetools.getYamlValue(yaml, _makeAbsolutePath(base, cPath))
        if val is None:
            return not cMustHave
        if isinstance(val, bool):
            cVal = str(cVal).upper() in ['TRUE', 'T', 'Y', 'YES', '1', 'ON']
        if cTest=='*':
            return val is not None
        if cTest=='=':
            return val==cVal
        if cTest=='!=':
            return val!=cVal
        return False # can't happen anyway

    def _addLabels(self, yaml, labels):
        if 'labels' not in yaml['metadata']:
            yaml['metadata']['labels'] = {}
        for l in labels:
            if l is not None:
                yaml['metadata']['labels'][l] = labels[l]

    def applyTemplate(self, masterYaml, templateYaml):
        base = kubetools.getYamlValue(templateYaml, 'metadata/annotations/'+self.resourceName+'Def/base', '/')
        type = kubetools.getYamlValue(templateYaml, 'metadata/annotations/'+self.resourceName+'Def/type', 'always')
        condition = kubetools.getYamlValue(templateYaml, 'metadata/annotations/'+self.resourceName+'Def/condition')
        yamlId = kubetools.getYamlValue(templateYaml, '/kind', 'UnknownKind')+'/'+kubetools.getYamlValue(templateYaml, '/metadata/name', 'NoName')
        if type=='map':
            return []
        elif (type=='single') and (kubetools.getYamlValue(masterYaml, base)!=None):
            if not self._checkCondition(masterYaml, base, condition):
                return []
            parsed = self._applyTemplateBranch(masterYaml, templateYaml, base, yamlId)
            self._addLabels(parsed, {
                self.tracebackLabel: kubetools.getYamlValue(masterYaml, 'metadata/name'),
            })
            return [parsed]
        elif type=='always':
            if not self._checkCondition(masterYaml, base, condition):
                return []
            parsed = self._applyTemplateBranch(masterYaml, templateYaml, base, yamlId)
            self._addLabels(parsed, {
                self.tracebackLabel: kubetools.getYamlValue(masterYaml, 'metadata/name'),
            })
            return [parsed]
        elif (type=='list') and (kubetools.getYamlValue(masterYaml, base)!=None):
            groupLabel = kubetools.getYamlValue(templateYaml, 'metadata/annotations/'+self.resourceName+'Def/groupLabel')
            items = kubetools.getYamlValue(masterYaml, base)
            result = []
            for k, _ in enumerate(items):
                itemBase = base+'/'+str(k)
                if self._checkCondition(masterYaml, itemBase, condition):
                    parsed = self._applyTemplateBranch(masterYaml, templateYaml, itemBase, yamlId)
                    self._addLabels(parsed, {
                        self.tracebackLabel: kubetools.getYamlValue(masterYaml, 'metadata/name'),
                        'groupLabel': groupLabel,
                    })
                    result.append(parsed)
            return result
        return []

    def _splitTag(self, tag):
        """
        Return tuple: (path, type, default)
        """
        parts = tag.rpartition(':')
        if parts[1]=='':
            return (tag, None, None)
        if not parts[2].startswith('?'):
            return (parts[0], parts[2], None)
        return (parts[0], parts[2][1:], typejuggler.defaultVal(parts[2][1:]))

    def _findMapTemplate(self, mapName):
        for templateYaml in self.files:
            if kubetools.getYamlValue(templateYaml, 'metadata/annotations/'+self.resourceName+'Def/mapName')==mapName:
                return templateYaml
        raise TemplateValueError('Missing map: %s' % mapName)

    def _resolveValue(self, masterYaml, base, tagStr, yamlId, forceType=None):
        valueDef, dstType, default = self._splitTag(tagStr)
        errLocation = 'path %s, used in %s' % (_makeAbsolutePath(base, valueDef), yamlId)
        if valueDef.startswith(ENV_PREFIX) and valueDef.endswith(ENV_SUFFIX):
            if ENV_SUFFIX=='': # this would optimize lovely in compiled language
                envName = valueDef[len(ENV_PREFIX):]
            else:
                envName = valueDef[len(ENV_PREFIX):-len(ENV_SUFFIX)]
            try:
                val = os.environ[envName]
            except KeyError as e:
                raise TemplateValueError('Undefined env: %s (%s)' % (envName, errLocation))
        elif valueDef.startswith(MAP_PREFIX):
            ref = valueDef[len(MAP_PREFIX):].split(MAP_SUFFIX, 1)
            mapName = ref[0]
            path = ref[1]
            path = re.sub(r'\[(.+?)\]', lambda match: str(kubetools.getYamlValue(masterYaml, _makeAbsolutePath(base, match.group(1)))), path)
            val = kubetools.getYamlValue(self._findMapTemplate(mapName), path)
            errLocation += ' '+path
        else:
            val = kubetools.getYamlValue(masterYaml, _makeAbsolutePath(base, valueDef))
        if val is None:
            if default is None:
                raise TemplateValueError('Missing value: %s (%s)' % (tagStr, errLocation))
            val = default
        if dstType is None:
            dstType = typejuggler.detectType(val)
        if forceType is not None:
            if forceType!=typejuggler.getBaseType(dstType):
                dstType = forceType
        try:
            val = typejuggler.castToType(val, dstType)
        except ValueError as e:
            raise TemplateValueError('%s: %s "%s" (%s)' % (str(e), tagStr, val, errLocation))
        return val

    def _substituteStrTags(self, masterYaml, templateStr, base, yamlId):
        """
        Substitute ((token)) strings in templateStr.
        Tokens CAN NOT be nested.
        """
        if templateStr.startswith(TAG_START) and templateStr.endswith(TAG_END) and (templateStr[1:-1].find(TAG_END)==-1):
            # entire string is a single reference - inherit type
            return self._resolveValue(masterYaml, base, templateStr[len(TAG_START):-len(TAG_END)], yamlId)
        # a string with possible references inside - force str conversion
        srcLen = len(templateStr)
        pos = 0
        indent = 0
        result = ''
        while pos<srcLen:
            if templateStr[pos:pos+len(TAG_START)]==TAG_START:
                closePos = templateStr.find(TAG_END, pos+len(TAG_START))
                if closePos!=-1:
                    tag = templateStr[pos+len(TAG_START):closePos]
                    _, type, _ = self._splitTag(tag)
                    expanded = self._resolveValue(masterYaml, base, tag, yamlId, forceType=typejuggler.STR)
                    if type=='yaml': # ugly special case
                        if expanded.strip() in ['[]', '{}']: # even uglier special case of special case
                            result += '  '+expanded.strip()
                            indent += len('  '+expanded.strip())
                        else:
                            result += expanded.replace('\n', '\n'+(' '*indent)).rstrip()
                    else:
                        result += expanded
                        indent += len(expanded)
                    pos = closePos+len(TAG_END)
                    continue
            result += templateStr[pos]
            if templateStr[pos] in ['\r', '\n']:
                indent = 0
            else:
                indent += 1
            pos += 1
        return result

    def _applyTemplateBranch(self, masterYaml, templateYaml, base, yamlId):
        if isinstance(templateYaml, collections.Mapping):
            iterator = lambda mapping: getattr(mapping, 'iterator', mapping.items)()
            clone = {}
        elif isinstance(templateYaml, (collections.Sequence, collections.Set)) and not typejuggler.isString(templateYaml):
            iterator = enumerate
            clone = [None]*len(templateYaml)
        else:
            if not typejuggler.isString(templateYaml):
                return templateYaml
            return self._substituteStrTags(masterYaml, templateYaml, base, yamlId)
        for k, v in iterator(templateYaml):
            clone[k] = self._applyTemplateBranch(masterYaml, v, base, yamlId)
        return clone

    def _reorder(self, yamls):
        partitioned = {}
        for y in yamls:
            priority = kubetools.getYamlValue(y, 'metadata/annotations/'+self.resourceName+'Def/priority', 10)
            if priority not in partitioned:
                partitioned[priority] = []
            partitioned[priority].append(y)
        partitioned = partitioned.items()
        partitioned.sort(key=lambda elem: elem[0])
        result = []
        for p in partitioned:
            result += p[1]
        return result

    def applyAllTemplates(self, masterYaml):
        result = []
        for templateYaml in self.files:
            result += self.applyTemplate(masterYaml, templateYaml)
        return self._reorder(result)

    def _getAllEnvReferencesBranch(self, templateYaml, result):
        if isinstance(templateYaml, collections.Mapping):
            iterator = lambda mapping: getattr(mapping, 'iterator', mapping.items)()
        elif isinstance(templateYaml, (collections.Sequence, collections.Set)) and not typejuggler.isString(templateYaml):
            iterator = enumerate
        else:
            if not typejuggler.isString(templateYaml):
                return
            return re.sub(r'\(\('+re.escape(ENV_PREFIX)+'(.+?)'+re.escape(ENV_SUFFIX)+r'\)\)', lambda match: result.add(match.group(1)), templateYaml) # TODO: This is oversimplified - it won't notice envs with type suffix, or used as subindexes
        for _, v in iterator(templateYaml):
            self._getAllEnvReferencesBranch(v, result)

    def getAllEnvReferences(self):
        envList = set()
        for templateYaml in self.files:
            self._getAllEnvReferencesBranch(templateYaml, envList)
        result = {}
        for en in envList:
            try:
                result[en] = os.environ[en]
            except KeyError:
                raise TemplateValueError('Missing required ENV variable: %s' % en)
        return result
