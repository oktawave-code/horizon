

from ctypes import *

l = CDLL('./sgxpass/app')
p = './sgxpass/enclave.signed.so'

eid = c_ulonglong()
i = l.create_enclave(p.encode(), byref(eid))
if i != 0:
    raise ValueError("Enclave creation error. Code: " + str(i))


def sgx_pass_through(byte_array: bytes):
    ret = l.pass_through(eid, byte_array, len(byte_array))

    if ret != 0:
        raise Exception("SGX exec error: {}".format(hex(ret)))
