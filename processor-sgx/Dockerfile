FROM registry.hn.oktawave.com/base-sgx:4

ADD . /app

WORKDIR /app/sgxpass
RUN make
# RUN make SGX_MODE=SIM # for simulation mode

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/app/docker-entrypoint.sh"]
