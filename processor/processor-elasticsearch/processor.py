import os
from datetime import datetime
from kafka import KafkaConsumer, TopicPartition
from elasticsearch import Elasticsearch

KAFKA_SERVER_ADDRESS = os.environ['KAFKA_HOSTNAME'] + ':' + os.environ['KAFKA_PORT']#'localhost:9092'
KAFKA_TOPIC = 'test'

ELASTICSEARCH_ADDRESS = os.environ['ELASTICSEARCH_HOSTNAME'] #'localhost'
ELASTISCEARCH_PORT = int(os.environ['ELASTICSEARCH_PORT']) #9200
ELASTICSEARCH_INDEX = 'test'
ELASTICSEARCH_DOCUMENT = 'doc'

es = Elasticsearch([
    {'host': ELASTICSEARCH_ADDRESS, 'port': ELASTISCEARCH_PORT}
])

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVER_ADDRESS)
for msg in consumer:
    body = {
        'metadata': {
            'date': datetime.now(),
            'status': 'processed'
        },
        'data': {
            'originalValue': str(msg.value),
            'processedValue': str(msg.value).upper()
        }
    }
    print str(body)
    es.index(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCUMENT, body=body)
