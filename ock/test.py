
import requests
import time

# ignore ssl
# requests.packages.urllib3.disable_warnings()
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url = "http://localhost:5000/ock"


def create_key(args):
    r = requests.post(base_url + "/keys", json=args)
    return r.json()

def create_alias(args):
    r = requests.post(base_url + "/aliases", json=args)
    return r.json()

def encrypt_alias(args):
    r = requests.post(base_url + "/encrypt", json=args)
    return r.json()

def decrypt_alias(args):
    r = requests.post(base_url + "/decrypt", json=args)
    return r.json()

for i in range(10):
    c = create_key({"OktaToken": "This is a valid token", "Type": "RSA"})
    print(i, " : ", c)
    c.update({"KeyAlias": "orangutan-" + str(i)})
    d = create_alias(c)
    print(i, " : ", d)
    d.update({"Plaintext": "QWRhbQ==", "Mode": "RSA-EVP"})
    e = encrypt_alias(d)
    print(i, " : ", e)
    e.update({"Token": d["Token"]  ,"Mode": "RSA-EVP"})
    f = decrypt_alias(e)
    print(i, " : ", f)

    print()
