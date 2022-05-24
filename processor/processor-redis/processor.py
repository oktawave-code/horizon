import os
from datetime import datetime
from kafka import KafkaConsumer, TopicPartition
import redis
import time

KAFKA_SERVER_ADDRESS = os.environ['KAFKA_HOSTNAME'] + ':' + os.environ['KAFKA_PORT']#'localhost:9092'
KAFKA_TOPIC = 'test'

REDIS_HOSTNAME = os.environ['REDIS_HOSTNAME']
REDIS_PORT = int(os.environ['REDIS_PORT']) # 6379

redisClient = redis.StrictRedis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=0)

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVER_ADDRESS)
for msg in consumer:
    key = time.time()
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
    print(str(key), str(body))
    redisClient.set(str(key), body)
