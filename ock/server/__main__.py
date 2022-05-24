import configparser

import requests
from flask import Flask, jsonify, send_from_directory
from flask import request
from jwcrypto import jwt
import hashlib
import json
import os
from os import walk
import sys
#from server.ockjwt import OckRandom, OckEToken, OckToken
sys.path.append(os.path.abspath('..'))
from ntools.ockjwt import OckRandom
from ntools.authorization import authorizeWithIDServer


app = Flask(__name__, static_url_path="", static_folder="/app/swagger-editor")
app.config['INITIALIZED'] = False

from server.sgx import SGXConnection
C = SGXConnection('hsm/app')
C.create_enclave('hsm/enclave.signed.so')

config = configparser.ConfigParser()
configFileName = "config/config.cfg"
if os.path.isfile(configFileName):
    print("Config file found")
else:
    print("Config file is missing!")
    sys.exit("\nConfig file not found")

config.read(configFileName)

mode = config['DEFAULT']['mode']
IDServer = config['IDServer'][mode]

id_server_url = config["IDServer"][mode]



@app.route('/status', methods=['GET', 'POST'])
def status():
    print("Headers: Status check")
    if app.config['INITIALIZED'] == False:
        try:
            print("Not initialized")
            print("Headers: not initialized")
            #initialize()
        except:
            print("Beauty is sleeping")
            print("Headers: beauty is slipping")
    ret = str(request.headers)
    return ret


@app.route('/mng/test', methods=['POST'])
def test():
    print("Headers: I'm queen")
    data = request.get_data()
    #ret = request.headers
    ip = request.remote_addr
    print( data, len(data))
    print("Headers start: ")
    print(request.headers)
    print("Headers stop")
    data = "SOME RANDOM DATAx"
    if request.headers.getlist("X-Real-IP"):
        print("Headers:" + request.headers["X-Real-IP"])
    if request.headers.getlist("X-Forwarded-For"):
        print("Headers:" + request.headers["X-Forwarded-For"])
    if request.headers.getlist("X-Forwarded-Host"):
        print("Headers:", request.headers["X-Forwarded-Host"])
    if request.headers.getlist("X-Forwarded-Port"):
        print("Headers:", request.headers["X-Forwarded-Port"])
    if request.headers.getlist("X-Forwarded-Proto"):
        print("Headers:", request.headers["X-Forwarded-Proto"])

    mypath = "/mnt/shared"
    print("Listing directory: " + mypath)
    f = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        f.extend(filenames)
        #print("-> " + dirpath + " / " + filenames)
        break
    x = "Files:" + str(f) + "\n"
    #print("Headers:", request.headers["X-Real-IP"])
    #print("Headers:", request.headers["X-Forwarded-For"])
    #print("Headers:", request.headers["X-Forwarded-Host"])
    #print("Headers:", request.headers["X-Forwarded-Port"])
    #print("Headers:", request.headers["X-Forwarded-Proto"])

    #authToken = requests.args.get('token')
    #request.headers.getlist("Authorization")
    serverType = request.headers['Server'] #dev/prod
    if serverType in {'dev', 'prod'}:
        serverUrl = config["IDServer"][serverType]
    else:
        serverUrl = config["IDServer"]['dev']

    print("IDserver: " + serverType)
    print("IDserverUrl: " + serverUrl)

    print(request.headers.getlist("Authorization"))
    result = authorizeWithIDServer(request.headers.getlist("Authorization"), serverUrl)
    print(str(result))
    if result["code"] > 200:
        return result["message"], result["code"], {'Content-Type': 'application/json'}
    else:
        return result


# ret, status_code = C.invoke('create_key', data, ip)

    #return data
    ret = str(request.headers)

    #for x in ret
     #   print x

    #str = ",".join(ret)
    status_code = 200


    return ret + x
    #str += "]"
    #return print("%s",ret), status_code, {'Content-Type': 'application/json'}




@app.route('/test', methods=['GET'])
def test1():
    print("Headers start:")
    print(request.headers)
    print("HEaders stop")
    data = "SOME RANDOM DATAx"
    if request.headers.getlist("X-Real-IP"):
        print("Headers:" + request.headers["X-Real-IP"])
    if request.headers.getlist("X-Forwarded-For"):
        print("Headers:" + request.headers["X-Forwarded-For"])
    if request.headers.getlist("X-Forwarded-Host"):
        print("Headers:", request.headers["X-Forwarded-Host"])
    if request.headers.getlist("X-Forwarded-Port"):
        print("Headers:", request.headers["X-Forwarded-Port"])
    if request.headers.getlist("X-Forwarded-Proto"):
        print("Headers:", request.headers["X-Forwarded-Proto"])
    #headersList = request.headers.
    #print("-".join(headersList))
    #print( data, len(data))
    print("a to co: ", len("a to co"))
    print(dict(request.headers), len(dict(request.headers)))
    # print("Headers:", request.headers["X-Real-IP"])

    #authToken = requests.args.get('token')
    serverType = requests.args.get('server') #dev/prod
    serverUrl = config["IDServer"][serverType]

    result = authorizeWithIDServer(request.headers.getlist("Authorization"), serverUrl)
    if result["code"] > 200:
        return result["message"], result["code"], {'Content-Type': 'application/json'}

    auth_token = ''
    # ret, status_code = C.invoke('create_key', data, ip)

    return data

#@TODO: this is for testing only.
#try:
#    os.remove("/mnt/shared/secret.keys")
#except OSError:
#    pass

@app.route("/config/<path:path>")
def send_static_config(path):
        return send_from_directory("/app/swagger-editor/config", path)

@app.route("/dist/<path:path>")
def send_static_dist(path):
    return send_from_directory("/app/swagger-editor/dist", path)

@app.route("/images/<path:path>")
def send_static_images(path):
    return send_from_directory("/app/swagger-editor/images", path)

@app.route("/scripts/<path:path>")
def send_static_scripts(path):
    return send_from_directory("/app/swagger-editor/scripts", path)

@app.route("/spec-files/<path:path>")
def send_static_spec_files(path):
    return send_from_directory("/app/swagger-editor/spec-files", path)

@app.route("/styles/<path:path>")
def send_static_styles(path):
    return send_from_directory("/app/swagger-editor/styles", path)

@app.route("/index.html")
@app.route("/index")
@app.route("/ock")
@app.route("/api")
@app.route("/mng")
@app.route("/")
def rooti():
    return app.send_static_file("index.html")


@app.route('/ock/keys', methods=['POST'])
def create_key():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        result = authorizeWithIDServer(request.headers.getlist("Authorization"), id_server_url)
        if result["code"] > 200:
            return result["message"], result["code"], {'Content-Type': 'application/json'}
        else:
            ret, status_code = C.invoke('create_key', data, ip)
            return ret, status_code, {'Content-Type': 'application/json'}

    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/import', methods=['POST'])
def import_key():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        print(request)

        ret, status_code = C.invoke('import_key', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/aliases', methods=['POST'])
def create_alias():
    if app.config['INITIALIZED'] == True:
        #remoteAddr = request.remote_addr
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        #data["remoteAddr"] = remoteAddr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('create_alias', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/encrypt', methods=['POST'])
def encrypt():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('encrypt', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/decrypt', methods=['POST'])
def decrypt():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('decrypt', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/sign', methods=['POST'])
def sign():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('sign', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/verify', methods=['POST'])
def verify():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('verify', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/digest', methods=['POST'])
def digest():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('digest', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/random', methods=['POST'])
def random():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('random', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/manage', methods=['POST'])
def manage():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('manage', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}


@app.route('/ock/shared_secret', methods=['POST'])
def shared_secret():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('shared_secret', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}

@app.route('/ock/public_key', methods=['POST'])
def public_key():
    if app.config['INITIALIZED'] == True:
        data = request.get_data()
        if request.headers.getlist("X-Real-IP"):
            ip = request.headers.getlist("X-Real-IP")[0]
        else:
            ip = request.remote_addr
        print( data, len(data))
        # print("Headers:", request.headers["X-Real-IP"])

        ret, status_code = C.invoke('public_key', data, ip)

        return ret, status_code, {'Content-Type': 'application/json'}
    else:
        return jsonify("OCK not initialized"), 500, {'Content-Type': 'application/json'}

""" SETUP: connecting workers

Methods /ock/ra, /ock/rb, /ock/rc are responsible for letting new workers
to connect to Queen service. During this three-phase protocol the following
properties are achieved:
1) a secure authenticated channel between a worker and the queen is established
2) mutual RemoteAttestation (RA) between parties is performed
3) in the case of successful RA
"""
@app.route('/ock/ra/1', methods=['POST'])
def workerConnectA():
    data = request.get_data()
    x = request.json
    #print(data)
    #x = json.loads(data)
    print(x)
    key = x['key']
    print(key, len(key))
    #NEW_KEY = jwk.JWK(generate='oct', size=256)
    data = NEW_KEY.export()
    print(data)
    #return data
    return data

@app.route('/ock/ra/2', methods=['POST'])
def workerConnectB():
    data = request.get_data()
    print("Data:")
    print(data)
    ST = jwt.JWT(key=NEW_KEY, jwt=data.decode())
    print("Decoded:")
    print(ST.claims)
    return jsonify(connected="yes")


@app.route('/mng/init', methods=['POST'])
def mngInit():
    if app.config['INITIALIZED'] == False:
        #generate config dir
        dirName = OckRandom.randomString(8)
        app.config['configPath'] = "/mnt/shared/config-" + dirName
        app.config['INITIALIZED'] = True
    return jsonify("Initialization successful")



@app.route('/mng/files', methods=['POST'])
def mngFiles():
    data = request.get_data()
    print("Data:")
    print(data)
    mypath = "/mnt/shared"
    print("Listing of directory: " + mypath)
    f = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        f.extend(filenames)
        #print("-> " + dirpath + " / " + filenames)
        break
    return jsonify(f)

@app.route('/mng/status', methods=['POST'])
def mngStatus():
    if app.config['INITIALIZED'] == False:

        print("OCK is not initialized")
        fx = []
        fx.append("OCK not initialized")
        #checking if all required directories exist
        requiredDirs = ["/mnt/shared", "/mnt/shared/policies"]
        for requiredDir in requiredDirs:
            if not os.path.exists(requiredDir):
                #os.makedirs(requiredDir)
                fx.append("Directory missing: " + requiredDir)

        #checking if there is connection to ID servers





        return jsonify(fx), 500, {'Content-Type': 'application/json'}
    else:
        print("initialized")
        x = "OCK initialized"
        fx = []
        files = ["./server/__main__.py", "./hsm/enclave.signed.so"]
        for filename in files:
            sha256_hash = hashlib.sha256()
            with open(filename,"rb") as f:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(byte_block)
                fx.extend([filename , str(sha256_hash.hexdigest())])



    return jsonify(fx)


#@app.route('/mng/clear', methods=['POST'])
#def mngKeys():
#    try:
#        os.remove("/mnt/shared/secret.keys")
#        os.remove("/mnt/shared/global_eid.txt")
#    except OSError:
#        pass
#    data = request.get_data()
#    print("Data:")
#    print(data)
#    mypath = "/mnt/shared"

#    print("Listing directory: " + mypath)
#    f = []
#    for (dirpath, dirnames, filenames) in walk(mypath):
#        f.extend(filenames)
#        #print("-> " + dirpath + " / " + filenames)
#        break
#    return jsonify(f)


if __name__ == '__main__':
    port = 6000
    if len(sys.argv) > 1:
        port = sys.argv[1]
    app.run(host="0.0.0.0", port=port)
