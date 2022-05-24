import numbers
import json
import yaml
import re

# base types:
INT = 'int'
STR = 'str'
OBJ = 'obj'

def _validator_int(val):
    try:
        val = int(val)
    except ValueError:
        raise ValueError('Not a number')
    except TypeError:
        raise ValueError('Not a number')
    return val

def _validator_str(val):
    if detectType(val)==OBJ:
        raise ValueError('Can not convert to a string')
    return str(val)

def _validator_obj(val):
    if detectType(val)!=OBJ:
        raise ValueError('Not an object')
    return val

def _validator_json(val):
    if detectType(val)!=OBJ:
        raise ValueError('Not an object')
    return json.dumps(val, separators=(',', ':'))

def _validator_yaml(val):
    if detectType(val)!=OBJ:
        raise ValueError('Not an object')
    return yaml.safe_dump(val, default_flow_style=False)

def _validator_nonempty(val):
    v =_validator_str(val)
    if v=='':
        raise ValueError('Empty string is not valid')
    return v

def _validator_name(val):
    v =_validator_nonempty(val)
    if not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$', v):
        raise ValueError('Not a valid name')
    return v

def _validator_image(val):
    v =_validator_nonempty(val)
    if not re.match(r'^(?:(?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?::(?![.-])[a-zA-Z0-9_.-]{1,128})?$', v):
        raise ValueError('Not a valid image name')
    return v

def _getValidator(type):
    try:
        validator = globals()['_validator_%s' % type]
    except KeyError:
        raise Exception('Unknown type: %s' % type)
    return validator

def isString(val):
    return isinstance(val, ((str, unicode) if str is bytes else (str, bytes)))

def detectType(val):
    if isinstance(val, numbers.Integral):
        return INT
    if isString(val):
        return STR
    return OBJ

def castToType(val, type):
    v = _getValidator(type)
    return v(val)

def getBaseType(type):
    # TODO: Use some generic inheritance instaed of this ugly patch
    if type=='json':
        return STR
    if type=='yaml':
        return STR
    if type=='nonempty':
        return STR
    if type=='name':
        return STR
    if type=='image':
        return STR
    return type

def defaultVal(type):
    type = getBaseType(type)
    if type==INT:
        return 0
    elif type==STR:
        return ''
    return {}
