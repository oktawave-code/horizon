#!/usr/bin/env bash

EMITTER_SUFFIX=es COLLECTOR_SUFFIX=cs HFE_IMAGE=himg EMITTER_IMAGE=eimg ELASTIC_IMAGE=eimg VERBOSE_COLLECTOR=yes SKIP_META=yes KAFKA_IMAGE=kimg COLLECTOR_IMAGE=img FLINK_IMAGE=fimg ID_SERVER_URL=ids ./main.py flows --tracebackLabel=parent --noAction -vvv $*
