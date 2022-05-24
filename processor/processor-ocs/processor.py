import os
from datetime import datetime
from kafka import KafkaConsumer, TopicPartition
import time
from keystoneauth1 import session
from swiftclient import authv1, Connection, client

KAFKA_SERVER_ADDRESS = os.environ['KAFKA_HOSTNAME'] + ':' + os.environ['KAFKA_PORT']#'localhost:9092'
KAFKA_TOPIC = 'test'

auth = authv1.PasswordPlugin(
    auth_url='http://localhost:9400',
    username='user',
    password='pass'
)

keystone_session = session.Session(auth=auth)
swift_conn = Connection(session=keystone_session)
swift_conn.put_container(container='horizon')

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
    swift_conn.put_object(container='horizon', obj='test-'+ str(key) + '.txt', contents=str(body))
