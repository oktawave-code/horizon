#!/bin/bash
if [ ! -c /dev/isgx ]; then
    echo "/dev/isgx is not available! Won't start Intel AESM service."
else
    echo "/dev/isgx available! Starting Intel AESM service!"
    /opt/intel/sgxpsw/aesm/aesm_service &
    python3 processor.py 
    sleep 1
fi

exec "$@"
