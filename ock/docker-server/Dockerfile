FROM registry.hn.oktawave.com/base-sgx:10 as builder

SHELL ["/bin/bash", "-c"]

RUN apt-get update -q && apt-get install -y pkg-config apt-utils
#for dev only (curl)
RUN apt-get install -y curl python3-pip python-dev libffi-dev
RUN pip3 install --upgrade pip

RUN cd /tmp && \
  git clone https://github.com/intel/intel-sgx-ssl.git && \
  cd intel-sgx-ssl/openssl_source/ && \
  git checkout 7f322fa882fbb79b70e2c65c1f88b6c117e314d6 && \
  wget https://www.openssl.org/source/openssl-1.1.1c.tar.gz

RUN cd /tmp/intel-sgx-ssl/Linux && \
   source /opt/intel/sgxsdk/environment && \
   make all SGX_MODE=HW && \
   make install SGX_MODE=HW

# Build Queen
FROM builder
SHELL ["/bin/bash", "-c"]

ADD . /app

VOLUME /mnt/shared
WORKDIR /app
RUN source /opt/intel/sgxsdk/environment && \
   ./reload.sh

EXPOSE 6000

CMD source /opt/intel/sgxsdk/environment && python3 -m server
