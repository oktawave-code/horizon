FROM registry.hn.oktawave.com/base-sgx:10 as builder

SHELL ["/bin/bash", "-c"]

RUN apt-get update -q && apt-get install -y pkg-config apt-utils
#for dev only (curl)
RUN apt-get install -y curl python3-pip python-dev libffi-dev

RUN cd /tmp && \
  git clone https://github.com/intel/intel-sgx-ssl.git && \
  cd intel-sgx-ssl/openssl_source/ && \
  git checkout b3a70bf540e74a66edd8df9eada1862a09eb81f1 && \
  wget https://www.openssl.org/source/openssl-1.1.1a.tar.gz

RUN cd /tmp/intel-sgx-ssl/Linux && \
   source /opt/intel/sgxsdk/environment && \
   make all SGX_MODE=HW && \
   make install SGX_MODE=HW

# Build Queen
FROM builder
SHELL ["/bin/bash", "-c"]

VOLUME /mnt/shared
ADD . /app

WORKDIR /app
RUN source /opt/intel/sgxsdk/environment && \
   ./reload.sh

EXPOSE 5000 

CMD source /opt/intel/sgxsdk/environment && export WORKER_SETTINGS=worker.cfg && python3 -m worker
