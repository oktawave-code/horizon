# Enclave - Intel SGX (C++)

Enclave consists of two parts - trusted and untrusted.

Untrusted is simply a code that has no intel-sgx protection and in strict sense is not secure.

Trusted is part that is executed inside the trusted intel-sgx enclave and everything that is inside (variables) is assured by intel to stay safe and be impossible to read by unauthorised party.

## `Application`
Is built as shared library that forwards data into `enclave.signed.so` - trusted sgx code.
For more (but little) information check `Application/App.cpp`

## `Enclave`
Is built as signed shared library - `enclave.signed.so` and represents the SGX code.
Main entry point `Enclave/enclave.cpp`
Definition of the interface `Enclave/enclave.edl`
Private key for signing `enclave.so` into `enclave.signed.so` via sgx-sdk (check makefile) - `enclave_private.pem`
Private key should be 3076 RSA key with 3 as public key.

## Main Control Flow

1. `Application` (built as `app`) is shared library with main interface
  1. `App.cpp` is main entrypoint of `app` library
2. `Enclave` (built as `enclave.signed.so`) is sgx secure shared library.
  1. `enclave.cpp` - main entry point that implements interface of `enclave.edl`
  2. `ock/worker_wrapper.cpp` - reads and parses input json into variables
  3. `ock/worker.cpp` - performs the operation itself (checks for permissions etc.)
  4. `ock/worker_wrapper.cpp` - Writes worker output into json format (`std::string`) with return code (`int`).
  5. `enclave.cpp` - returns result and return code to the caller

## Solution with TaLoS
At the time when TaLoS was employed right after 2.1. body was decrypted and after 2.4 encrypted.
If RSA_EVP should be used the same can be applied.


## Modules

### `base64`
Is just a base64 module found in the internet and integrated to our use.

### `json`
Another json module (found on github ), unfortunatly had to be written in pure C because C++ solutions used streams which are not supported inside enclaves.

Huge wrapper is written inside `ock/json_parser.cpp` and I hope that functionality of this module will suffice and usage of raw module will not be required. It was a nightmare at some point but now it's fine.

### `ock`

#### `types`
Defines key types used across the whole `ock` module.
Defines:
- `Key` - `ock:[number]:[family]:[alias]`
- `Token` - `1234-....`

**NOTE:** Get to know those files!

#### `worker_wrapper`
A kind of I/O wrapper module - reads and writes into json, in the middle calls `worker` functions.

#### `worker`
Main logic function. Performs requested operations. Checks for permissions, generates keys etc.

#### `policies`
Policies manager. Sets and verifies permissions (alias's at this moment of time)

#### `kdf`
Derives or generates keys for encryption / decryption / signatures.
Keys that are generated (RSA / DH) are stored in the file system under `[number].pem` and `[number].pub`. AES is derived on-the-fly.

Submodules:
- `aes` - `AES-GCM`
- `dh` - standard (non-EC) version
- `ecdsa` - not yet implemented
- `rsa` - `RSA_NO_PADDING`, `RSA_EVP`, `RSA_SIGNATURE`

#### `debug`
Just simple module that allows to print something into console
`debug()` has the same form as standard `printf()` function, so you can use `%s`, `%d` etc.


## `Makefile`
This one is the beast. Generates `app` and `enclave.signed.so`
What might be of interest is in line `131` - files included for enclave compilation. Note that folders are included by wildcards for easier notation.
