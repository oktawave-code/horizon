import requests


def authorizeWithIDServer(auth_header, serverUrl):
    print("authorize")
    print(auth_header)
    if auth_header:
        auth_token = auth_header[0].split(" ")[1]
        print("obtained token: " + auth_token)
        """ Now we query the ID server to verify
            if provided auth_token is valid
        """
        #@TODO: move ID server address to config
        #@TODO: change it to a real one (now Dev version is used)
        AuthQuery = serverUrl + auth_token
        r = requests.get(AuthQuery)
        print(r.json())
        reply = r.json()
        if "aud" in reply:
            client_id = reply["client_id"]
            ad_username = reply["ad_username"]
            return {'message' : 'OK', 'code' : 200, 'client_id' : client_id, 'ad_username' : ad_username}
        else:
            return {'message' : reply["Message"], 'code' : 401}

    else:
        return {'message' : "To access this method you need to send a valid authorization token", 'code' : 401}
