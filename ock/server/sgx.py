from ctypes import *
from typing import Tuple
import ctypes


class SGXError(Exception):
    def __init__(self, message):
        super().__init__(hex(message))


class OperationError(Exception):
    def __init__(self, message):
        super().__init__(hex(message))


class SGXConnection:
    def __init__(self, shared_lib):
        self.lib = CDLL(shared_lib)
        self.eid = c_ulonglong()
        print("SGXConnection created")

    def create_enclave(self, enclave_lib):
        """ Create SGX enclave via passing path to enclave.signed.so lib """

        sgx_code = self.lib.create_enclave(
            enclave_lib.encode(),
            byref(self.eid)
        )

        if sgx_code != 0:
            raise SGXError(sgx_code)


    def destroy_enclave(self):
        """ Destroy SGX enclave """

        sgx_code = self.lib.destroy_enclave()




    def call(self, function: str, *args):
        """ Call sgx library function """
        status = c_int()

        lib_fun = getattr(self.lib, function)
        sgx_code = lib_fun(self.eid, byref(status), *args)

        if sgx_code != 0:
            print("Trying to reconnect to the enclave")
            self.destroy_enclave()
            eidFile = open("/mnt/shared/global_eid.txt", "r")
            geid = int(eidFile.readline())
            print("geid read from file: " + str(geid))
            print("geid remembered: " + str(self.eid))

            self.create_enclave('hsm/enclave.signed.so')

            print("calling function again")
            sgx_code = lib_fun(self.eid, byref(status), *args)

            if sgx_code != 0:
                raise SGXError(sgx_code)

        return status.value
        #
        # if status.value != 200:
        #     raise OperationError(status.value)


    def invoke(self, function: str, body: bytes, ip: str):
        """ Pass body into sgx function """
        # TODO: dynamically assign buffer size
        output = bytes(8192)
        output_length = c_ulonglong()
        operation = {
            "create_key": 1,
            "create_alias": 2,
            "encrypt": 3,
            "decrypt": 4,
            "sign": 5,
            "verify": 6,
            "digest": 7,
            "random": 8,
            "manage": 9,
            "shared_secret": 10,
            "public_key": 11,
            "import_key": 12,
            "get_epid": 101,
        }[function]

        status_code = self.call("invoke", operation, body, len(body), ip.encode('utf-8'), output, byref(output_length))

        return output[:output_length.value], status_code

    def ra(self, function: str, body: bytes, ip: str):
        print("RA called")
        output = bytes(8192)
        output_length = c_ulonglong()
        operation = {
            "epid" : 1,
        }[function]

        status_code = self.call("epid",  operation, body, len(body), ip.encode('utf-8'), output, byref(output_length))
        if status_code == 0:
            print("epid 0")
        else:
            print("epid: " + status_code)
            status_code = 200
        return output[:output_length.value], status_code
