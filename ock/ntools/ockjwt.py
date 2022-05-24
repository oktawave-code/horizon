from jwcrypto import jwt, jwk, jwe
import random, string

class OckToken:

    def __init__(self, key):
        self.alg = "HS256"
        self.enc = "A256CBC-HS512"
        self.key = jwt.JWK(**key)

    def setPlaintext(self, plaintext):
        self.Token = jwt.JWT(header={"alg": "HS256"}, claims={"info": plaintext})
        self.Token.make_signed_token(self.key)
        #self.Token.serialize()

    def serialize(self):
        self.EToken = jwt.JWT(header={"alg": "A256KW", "enc": self.enc}, claims=self.Token.serialize())
        #tokenSerialized = self.Token.serialize()
        #self.EToken = jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=tokenSerialized)
        self.EToken.make_encrypted_token(self.key)
        serialized = self.EToken.serialize()
        return serialized


    def setKey(self, key):
        self.key = jwk.JWK(**key)

    def decode(self, e):
        ET = jwt.JWT(key=self.key, jwt=e)
        ST = jwt.JWT(key=self.key, jwt=ET.claims)
        return ST.claims

class OckEToken:

    @staticmethod
    def encrypt(pubKeyFile, payload):
        with open(pubKeyFile, "rb") as pemfile:
            publicKey = jwk.JWK.from_pem(pemfile.read())
        #publicKey = jwk.JWK.import_from_pem(self,)
        #publicKey = jwk.JWK.import_from_pem(self, data=self.privkeystr.encode('UTF-8'))


        #payload = "my encrypted message"
        protected_header = {
            "alg": "RSA-OAEP-256",
            "enc": "A256CBC-HS512",
            "typ": "JWE",
            "kid": publicKey.thumbprint(),
        }
        print(protected_header)
        jwetoken = jwe.JWE(payload.encode('utf-8'),
                       recipient=publicKey,
                       protected=protected_header
                       )
        enc = jwetoken.serialize()
        return enc

    @staticmethod
    def decrypt(privKeyFile, encrypted):
        with open(privKeyFile, "rb") as pemfile:
            privateKey = jwk.JWK.from_pem(pemfile.read())

        jwetoken = jwe.JWE()
        jwetoken.deserialize(encrypted, key=privateKey)
        return jwetoken.payload


class OckRandom:
    @staticmethod
    def randomString(N):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
