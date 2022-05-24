#!/usr/bin/env bash

cd server && pip3 install -r requirements.txt && cd -
# cd hsm && make SGX_MODE=HW && cd -
# cd hsm && make SGX_MODE=HW && cd -
#rm -rf *.pem
#rm -rf *.pub
#rm -rf *.policy
