from flask import Flask, jsonify
from flask import request
from jwcrypto import jwt, jwk
import requests, os, time
    #, os, time

app = Flask(__name__)
#app.config.from_object('yourapplication.default.settings')
app.config.from_envvar('WORKER_SETTINGS')
QUEEN_ADDRESS = os.environ.get("QUEEN_ADDRESS")
SECRET_KEY = os.environ.get("SECRET_KEY")

class Error(Exception):
    """Unspecified worker error"""
    pass

class QueenDeadError(Error):
    """Queen is currently not alive

    Attributes:
        expr -- input expression where error occured
        msg -- explanation
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg



def initialize():
    if app.config['INITIALIZED'] == False:
        try:
            #remote attestation step 1 (calling /ra)

            print('Initializing worker instance')
            data = '{"key":"abc"}'
            print("Sending:")
            print(data)
            headers = {'Content-Type': 'application/json'}
            r = requests.post(app.config['QUEEN_ADDRESS'] + "/ock/ra/1", data=data, headers=headers)

            #remote attestation step 2 (calling /rb)
            print("Receiving")
            x = r.json()
            print(x)
            SECRET_KEY = jwk.JWK(**x)
            Etoken = jwt.JWT(header={"alg":"HS256"}, claims={"myPublicKey":"Later"})
            Etoken.make_signed_token(SECRET_KEY)
            r = requests.post(app.config['QUEEN_ADDRESS'] + "/ock/ra/2", data=Etoken.serialize())
            #remote attestation step 3 (channel established)
            #now:
            # #1: obtain key to decrypt key files
            # #2: o btain key to sign jwt requests
            #print(r.text)
            x = r.json()
            if x["connected"] == "yes":
                app.config['INITIALIZED'] = True
            else:
                raise QueenDeadError("no response from queen: ", QUEEN_ADDRESS)
        except:
            print("No answer from queen")
            raise


#while app.config['INITIALIZED'] == False:
#    try:
#        initialize()
#    except:
#        print("Beauty is sleeping")
#    time.sleep(5)



from server.sgx import SGXConnection
C = SGXConnection('hsm/app')
C.create_enclave('hsm/enclave.signed.so')

@app.route('/status', methods=['GET', 'POST'])
def status():
    print("Headers: Status check")
    if app.config['INITIALIZED'] == False:
        try:
            print("Not initialized")
            print("Headers: not initialized")
            initialize()
        except:
            print("Beauty is sleeping")
            print("Headers: beauty is slipping")
    ret = str(request.headers)
    return ret


@app.route('/test', methods=['POST'])
def test():
    print("Headers: I'm worker")
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
    #print("Headers:", request.headers["X-Real-IP"])
    #print("Headers:", request.headers["X-Forwarded-For"])
    #print("Headers:", request.headers["X-Forwarded-Host"])
    #print("Headers:", request.headers["X-Forwarded-Port"])
    #print("Headers:", request.headers["X-Forwarded-Proto"])
    # ret, status_code = C.invoke('create_key', data, ip)
    #return data
    ret = str(request.headers)
    #for x in ret
    #   print x
    #str = ",".join(ret)
    status_code = 200
    return ret
    #str += "]"
    #return print("%s",ret), status_code, {'Content-Type': 'application/json'}


@app.route('/init', methods=['POST'])
def init():
    print('Config loaded: %s', QUEEN_ADDRESS)
    print('This is worker. Calling Queen')
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr
    headers = {'X-Real-IP': ip}
    r = requests.post(app.config['QUEEN_ADDRESS'] + '/test', headers=headers)
    print('app config start:')
    print(app.config)
    print('app config end')
    initialize()
    return r.text, r.status_code,  {'Content-Type': 'application/json'}




@app.route('/ock/keys', methods=['POST'])
def create_key():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr
    headers = {'X-Real-IP': ip}
    endpoint = app.config['QUEEN_ADDRESS'] + '/ock/keys'
    r = requests.post(endpoint, headers=headers, data=data)

    return r.text, r.status_code,  {'Content-Type': 'application/json'}


@app.route('/ock/import', methods=['POST'])
def import_key():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr
    headers = {'X-Real-IP': ip}
    endpoint = app.config['QUEEN_ADDRESS'] + '/ock/import_key'
    r = requests.post(endpoint, headers=headers, data=data)
    return r.text, r.status_code,  {'Content-Type': 'application/json'}


@app.route('/ock/aliases', methods=['POST'])
def create_alias():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr
    headers = {'X-Real-IP': ip}
    endpoint = app.config['QUEEN_ADDRESS'] + '/ock/aliases'
    r = requests.post(endpoint, headers=headers, data=data)
    return r.text, r.status_code,  {'Content-Type': 'application/json'}


@app.route('/ock/encrypt', methods=['POST'])
def encrypt():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('encrypt', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/decrypt', methods=['POST'])
def decrypt():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('decrypt', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/sign', methods=['POST'])
def sign():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('sign', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/verify', methods=['POST'])
def verify():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('verify', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/digest', methods=['POST'])
def digest():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('digest', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/random', methods=['POST'])
def random():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('random', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}


@app.route('/ock/manage', methods=['POST'])
def manage():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr
    headers = {'X-Real-IP': ip}
    endpoint = app.config['QUEEN_ADDRESS'] + '/ock/manage'
    r = requests.post(endpoint, headers=headers, data=data)
    return r.text, r.status_code,  {'Content-Type': 'application/json'}


@app.route('/ock/shared_secret', methods=['POST'])
def shared_secret():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])
    ret, status_code = C.invoke('shared_secret', data, ip)
    return ret, status_code, {'Content-Type': 'application/json'}

@app.route('/ock/public_key', methods=['POST'])
def public_key():
    if app.config['INITIALIZED'] == False:
        initialize()
    data = request.get_data()
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    print( data, len(data))
    # print("Headers:", request.headers["X-Real-IP"])

    ret, status_code = C.invoke('public_key', data, ip)

    return ret, status_code, {'Content-Type': 'application/json'}

@app.route('/attest/get_epid', methods=['POST'])
def getEPID():
    if request.headers.getlist("X-Real-IP"):
        ip = request.headers["X-Real-IP"]
    else:
        ip = request.remote_addr

    data = request.get_data()
    ret, status_code = C.ra('epid',  data, ip)
    #ret, status_code = C.invoke('epid', data, ip)
    return ret, status_code, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
