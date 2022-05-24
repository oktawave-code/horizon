import os
import base64
from datetime import datetime
from kafka import KafkaConsumer, TopicPartition
from elasticsearch import Elasticsearch

# wrapper to SGX
from sgxpass.sgx_connector import sgx_pass_through

KAFKA_SERVER_ADDRESS = os.environ['COLLECTOR_SERVER_ADDRESS'] + ':' + os.environ['COLLECTOR_SERVER_PORT']#'localhost:9092'
KAFKA_TOPIC = os.environ['COLLECTOR_TOPIC'] #'test'

ELASTICSEARCH_ADDRESS = os.environ['EMITTER_SERVER_ADDRESS'] #'localhost'
ELASTISCEARCH_PORT = int(os.environ['EMITTER_SERVER_PORT']) #9200
ELASTICSEARCH_INDEX = os.environ['EMITTER_INDEX'] #'test'
ELASTICSEARCH_DOCUMENT = os.environ['EMITTER_DOCUMENT'] #'doc'

es = Elasticsearch([
    {'host': ELASTICSEARCH_ADDRESS, 'port': ELASTISCEARCH_PORT}
])

def value_to_bytes(value):
    ## Implement conversion to python3 bytes
    return None

def bytes_to_es(byte_array: bytes):
    return None

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVER_ADDRESS)
for msg in consumer:
    print(str(msg.value))

    # PASS TO SGX
    msg_bytes = base64.b64decode(msg.value)
    # SGX exec
    sgx_pass_through(msg_bytes)
    msg_sgx = base64.b64encode(msg_bytes)
    # msg_sgx holds data ran through sgx

    body = {
        'metadata': {
            'date': datetime.now(),
            'status': 'processed'
        },
        'data': {
            'originalValue': str(msg.value),
            'processedSgxValue': str(msg_sgx),
        }
    }

    es.index(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCUMENT, body=body)
