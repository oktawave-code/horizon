FROM ubuntu

RUN apt-get update -q && apt-get install -y \
 build-essential ocaml ocamlbuild automake autoconf libtool wget python \
 libssl-dev libcurl4-openssl-dev protobuf-compiler libprotobuf-dev debhelper cmake \
 git patch python python3 python3-pip

COPY ./patches /patches


RUN export THREADS=`grep -c MHz /proc/cpuinfo` && \
 mkdir -p /opt/intel && \
 cd /tmp && \
 git clone https://github.com/intel/linux-sgx.git && \
 cd / && \
 for patch in /patches/*; do patch --prefix=/patches/ -p0 --force "--input=$patch" || exit 1; done && \
 rm -rf /patches && \
 cd /tmp/linux-sgx && \
 ./download_prebuilt.sh && \
 make -j $THREADS sdk_install_pkg && \
 cd /opt/intel && \
 yes yes | /tmp/linux-sgx/linux/installer/bin/sgx_linux_x64_sdk_*.bin && \
 cd /tmp/linux-sgx && \
 make -j $THREADS psw_install_pkg && \
 cd /opt/intel && \
 /tmp/linux-sgx/linux/installer/bin/sgx_linux_x64_psw_*.bin && \
 rm -rf /tmp/linux-sgx

RUN echo "source /opt/intel/sgxsdk/environment" >> /root/.bashrc
