# OCK

Oktawave Cloud Keys - is an implementation of cryptographic services working as a HSM(Hardware Sevcurity Module) based on an scientific research([link](/assets/GraFPE.pdf), [link](/assets/RiffleScrambler.pdf)).

Functionality
- cryptographic keys management
- data enryption and decryption
- cryptographic keys access management
- hash calculation
- digital signatures and signature verification


# Running

0. Build SGX and server requirements
```bash
$ cd server && pip3 install -r requirements.txt && cd -
$ cd hsm && make SGX_MODE={SIM, HW} && cd -
```
1. Source sgx-sdk environment variables:
```bash
$ source /opt/intel/sgxsdk/environment
```
2. From root directory run http server
```bash
$ python3 -m server
```

# General Overview

Queen consists of two main components:
1. Intel SGX (C++) "Enclave"
2. Http server (Python Flask) "Server"

## Server

Runs on port `5000` by default and practically it's only job is to forward body of http-request into Enclave in raw form.

Should resemble the interface specified in `swagger.yml` - Developers should try to keep the interface and actual implementation synchronised.

## Enclave
Details inside `hsm/readme.md`

Currently it does the following:
1. Reads input as json and calls operation (from operation_id) - `hsm/Enclave/enclave`
2. Extracts parameters from json and calls `worker` function - `hsm/Enclave/ock/worker_wrapper`
3. Worker performs requested operation itself - `hsm/Enclave/ock/worker`
4. Result is packed into json - `hsm/Enclave/ock/worker_wrapper`
5. Returns json outside with (http) status code - `hsm/Enclave/enclave`
6. If exception is raised (on failures of operations) inside Enclave, exception message is packed into return json and returned.



### Failure of end-to-end communication security

#### TaLoS
We tried to fully seal the communication channel from user to Enclave but it failed. "Hacking" of Nginx with TaLoS worked but was very unstable:
- Bigger requests crashed nginx (because of buffer overflow due to increse in size - `len(out_packet) = len(in_packet) + IV_LEN + TAG_LEN`)
- Some of TLS requests crashed the server due to unimplemented methods on TaLoS side.

The solution would be to either substitute TaLoS with custom solution or fix the buffer problem but it seemed be much to much of a hack.

#### Simplest but costly substitute solution
Using envelope encryption with enclave's public key will result in ciphertext that are decryptable only inside safe enclave.

The problem is, that RSA + AES on frontend is costly and obfuscates the interface by quite a lot. Thats why we tries TaLoS which was much cleaner solution.
