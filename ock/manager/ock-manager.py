import requests
import configparser
import json
import os
import sys
sys.path.append(os.path.abspath('..'))
from ntools.ockjwt import OckToken, OckEToken, OckRandom

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

    if len(sys.argv) <= 2:
        print("Usage: python3 ock-manager.py system action")


    setup = "okta"
    if len(sys.argv) > 1:
        setup = sys.argv[1]

    ACTION = "status"
    if len(sys.argv) > 2:
        ACTION = sys.argv[2]

    token = "tok"
    if len(sys.argv) > 3:
        token = sys.argv[3]

    QUEEN_ADDRESS = config[setup]["server"]
    oktaToken = config[setup]["oktaToken"]

    if ACTION in ["status", "files", "clear", "init", "test"]:
        try:
            #remote attestation step 1 (calling /ra)

            #print('\n\tWelcome to OCK::manager')
            print("\nSelected configuration:\t" + setup)
            print("Connecting to:\t" + QUEEN_ADDRESS + "\n")
            data = '{"key":"abc"}'
            #print("Sending:")
            #print(data)
            headers = {'Content-Type': 'application/json'}
            headers['Server'] = 'dev'
            tok = "Bearer " + token
            headers['Authorization'] = tok
            r = requests.post(QUEEN_ADDRESS + "/mng/" + ACTION, data=data, headers=headers)

            #remote attestation step 2 (calling /rb)
            print("Receiving")
            print(r.text)
            #x = r.json()

            print(r)
            #SECRET_KEY = jwk.JWK(**x)
            #Etoken = jwt.JWT(header={"alg":"HS256"}, claims={"myPublicKey":"Later"})
            #Etoken.make_signed_token(SECRET_KEY)
            #r = requests.post(QUEEN_ADDRESS + "/ock/ra/2", data=Etoken.serialize())
            #remote attestation step 3 (channel established)
            #now:
            # #1: obtain key to decrypt key files
            # #2: o btain key to sign jwt requests
            #print(r.text)
            #x = r.json()
            #if x["connected"] == "yes":
            #    app.config['INITIALIZED'] = True
            #else:
            #    raise QueenDeadError("no response from queen: ", QUEEN_ADDRESS)

        except:
            print("No answer from queen")
            raise
    else:
        if ACTION == "keyGen":
            #NEW_KEY = jwk.JWK(generate='oct', size=256)
            jsonKey = {"k":"nwe0-ngZBo9Z5DT2eWqbq2tc0w4HBrVSCAYPXVIGW-A","kty":"oct"}
            #NEW_KEY = jwk.JWK(**jsonKey)
            #print(NEW_KEY.export())
            #print(NEW_KEY)

            r = OckToken(jsonKey)
            r.setPlaintext('{"k1":"5d16dceaea3efc6467fd63c9ae3c30f82a2e271cc9873c28ccfc79f21b7384a", "k2":"4bd5877df9cab2109fc54e7d40295c18aef4e51be139ca2ea17cb7e659eab2"}')

            encryptedToken = r.serialize()

            w = OckToken(jsonKey)
            x = w.decode(encryptedToken)
            info = json.loads(x)
            keys = json.loads(info["info"])
            print(keys["k1"])

            print(str(info))

        if ACTION == "keyLoad":
            #r = OckEToken()
            enc = OckEToken.encrypt("credentials/public.pem", '{"k1":"5d16dceaea3efc6467fd63c9ae3c30f82a2e271cc9873c28ccfc79f21b7384a", "k2":"4bd5877df9cab2109fc54e7d40295c18aef4e51be139ca2ea17cb7e659eab2"}')

            print(enc)

            dec = OckEToken.decrypt("credentials/private.pem", enc)

            x = json.loads(dec)

            print(x["k1"])

        if ACTION == "create":

            dirName = OckRandom.randomString(8)
            configPath = "/mnt/shared/config-" + dirName
            os.mkdir(configPath)
            ######################################

