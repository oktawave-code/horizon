#!/usr/bin/env bash

# Info how to run local kafka: https://kafka.apache.org/quickstart

export LISTEN_PORT='11111'
#export ID_SERVER_URL='http://localhost:3000/core/connect/accesstokenvalidation?token='
export CLIENT_ID='user1'
export ROUTING='[{"filter":"/test","source":"url","topic":"test"},{"topic":"backup"},{"filter":"([a-z]+)","source":"X-Horizon-Routing","topic":"t-$1","final":true},{"filter":".+","source":"X-Topic","topic":"$0"}]'
#export KAFKA_BOOTSTRAP_SERVER='localhost:9092'
export VERBOSE=1

./collector
