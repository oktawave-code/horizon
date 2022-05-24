#!/usr/bin/env bash

(sleep 1; curl localhost:7777/metrics) &
./main.py -vv -p 7777
