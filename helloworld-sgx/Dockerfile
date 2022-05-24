# FROM registry.hn.oktawave.com/intel-sgx/base as builder
FROM registry.hn.oktawave.com/base-sgx:4 as builder

SHELL ["/bin/bash", "-c"]

ADD . /build

WORKDIR /build
RUN source "/opt/intel/sgxsdk/environment" && \
    make SGX_MODE=SIM

FROM registry.hn.oktawave.com/base-sgx:4

SHELL ["/bin/bash", "-c"]

WORKDIR /app
COPY --from=builder /build/app /app/app
COPY --from=builder /build/enclave.signed.so /app/enclave.signed.so

CMD source "/opt/intel/sgxsdk/environment" && ./app
