import base64

import requests
import configparser
import json
import os
import sys
sys.path.append(os.path.abspath('..'))

print("OCK tester")
"""
1. Create AES master key
2. Create key alias
3. Tries to encrypt and decrypt a messsage
"""

if (__name__ == '__main__'):
    config = configparser.ConfigParser()
    configFileName = "config/ock.cfg"
    if os.path.isfile(configFileName):
        print("Config file found")
    else:
        print("Config file is missing!")
        print("\nCreate file: config/ock.cfg with required fields e.g.,\n")
        print("\t[ock]")
        print("\tserver = https://ock.hn.oktawave.com")
        sys.exit("\nConfig file not found")

    config.read(configFileName)

    #QUEEN_ADDRESS =  "http://localhost:4000"
    import sys
    #for x in sys.argv:
    #    print x
    setup = "okta"
    if len(sys.argv) > 1:
        setup = sys.argv[1]

    token = "40525cbe28ed0ace17b093bec365d315"
    if len(sys.argv) > 2:
        token = sys.argv[2]

    headers = {'Content-Type': 'application/json'}
    QUEEN_ADDRESS = config[setup]["server"]
    oktaToken = config[setup]["oktaToken"]

    print("Testing: " + QUEEN_ADDRESS)

    # preparing create key call
    server_address = QUEEN_ADDRESS + "/ock/keys"
    print("\n1. Creating a new key: ")
    headers = {'Authorization': 'Bearer ' + token}
    data = "{\"OktaToken\":\"" + oktaToken + "\"}"

    print("Sending headers: " + str(headers))
    print("Sending data: " + data)
    rKey = requests.post(server_address, data=data, headers=headers)
    if rKey.status_code >= 300:
        raise Exception(rKey.text)

    print("Receiving headers: " + str(headers))
    print("Receiving: " + rKey.text)
    rKeyJson = json.loads(rKey.text)
    keyId = rKeyJson["KeyId"]
    keyToken = rKeyJson["Token"]

    # preparing create alias call
    server_address = QUEEN_ADDRESS + "/ock/aliases"
    data = "{\"KeyId\":\"" + keyId + "\", \"Token\":\"" + keyToken + "\", \"KeyAlias\":\"secret\", \"Policies\":{\"AllowedIp\": \"*\", \"ExpirationDate\": \"Never\", \"Action\": [\"ock:Encrypt\", \"ock:Info\", \"ock:Decrypt\"]}}"
    print("\n2. Creating a new alias:")

    print("Sending: " + data)
    rAlias = requests.post(server_address, data=data, headers=headers)
    print("Receiving: " + rAlias.text)
    rAliasJson = json.loads(rAlias.text)
    AliasId = rAliasJson["KeyId"]
    AliasToken = rAliasJson["Token"]


    # preparing encrypt call
    server_address = QUEEN_ADDRESS + "/ock/encrypt"
    plaintext = "Text to encrypt"
    ptEncoded = base64.b64encode(plaintext.encode())
    data = "{\"KeyId\":\"" + AliasId + "\", \"Token\":\"" + AliasToken + "\", \"Plaintext\":\"" + str(ptEncoded, "utf-8") + "\"}"
    #pt = str("VGV4dCB0byBlbmNyeXB0")
    #data = "{\"KeyId\":\"" + AliasId + "\", \"Token\":\"" + AliasToken + "\", \"Plaintext\":\"" + pt + "\"}"
    print("\n3. Encrypting a message: " + plaintext)

    print("Sending: " + data)
    rEnc = requests.post(server_address, data=data, headers=headers)
    print("Receiving: " + rEnc.text)
    rEncJson = json.loads(rEnc.text)
    CiphertextBlob = rEncJson["CiphertextBlob"]


    # preparing decrypt call
    server_address = QUEEN_ADDRESS + "/ock/decrypt"
    data = "{\"KeyId\":\"" + AliasId + "\", \"Token\":\"" + AliasToken + "\", \"CiphertextBlob\":\"" + CiphertextBlob + "\"}"
    print("\n4. Decrypting : " + CiphertextBlob)

    print("Sending: " + data)
    rDec = requests.post(server_address, data=data, headers=headers)
    print("Receiving: " + rDec.text)
    rDecJson = json.loads(rDec.text)
    Plaintext = str(base64.b64decode(rDecJson["Plaintext"]), "utf-8")
    print(Plaintext)

    if Plaintext == plaintext:
        print("AES encryption works correctly")
    else:
        print("Something went wrong")


