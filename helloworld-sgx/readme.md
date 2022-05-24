# Example Intel-SGX docker container build

Code is taken from `sgxsdk/SampleCode/SampleEnclave`.

## Application Structure
Application consists of two main parts: Trusted and Untrusted.
Untrusted is a standard C++ code that is meant to perform tasks that does not operate on sensitive data (encryption keys, secrets etc) e.g. Input / Output.
Trusted is executed inside SGX Enclave that assures execution security and secure storage of sensitive data.

In this example trusted part is compiled into `enclave.signed.so` shared library, while untrusted into `app`.
On runtime `app` links to `enclave.signed.so` to create secure enclave.
The interface between those two is specified in `*.edl` file.

## Development using simulation mode
Development of intel-sgx application can be conducted using simulation mode (`SGX_MODE=SIM`) without greater difficulties.
So there is no need to have a machine with SGX support for development environment, while only for production one is required.

## Exemplary build
### Dockerfile
```Dockerfile
FROM registry.hn.oktawave.com/intel-sgx/base as builder

SHELL ["/bin/bash", "-c"]

ADD . /build

WORKDIR /build
RUN source "/opt/intel/sgxsdk/environment" && \
    make SGX_MODE=HW


FROM registry.hn.oktawave.com/intel-sgx/base as builder

SHELL ["/bin/bash", "-c"]

WORKDIR /app
COPY --from=builder /build/app /app/app
COPY --from=builder /build/enclave.signed.so /app/enclave.signed.so

CMD source "/opt/intel/sgxsdk/environment" && ./app

```

### Build
```bash
$ docker build -t test/helloworld-sgx .
```

### Run
```bash
$ docker run test/helloworld-sgx
```
