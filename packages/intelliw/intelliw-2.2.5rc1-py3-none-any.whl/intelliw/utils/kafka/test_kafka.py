
import json
import time

from intelliw.utils.kafka import get_client, handle_message
import os

hosts = '192.168.15.218:9092'

# producer_config={'acks': 'all'},
consumer_config={'auto.offset.reset': 'earliest',
                         'enable.auto.commit': True,
                         'max.poll.interval.ms': 8000000,
                         'heartbeat.interval.ms': 3000,
                         'session.timeout.ms': 30000}
security_protocol: str = 'SASL_PLAINTEXT'
sasl_mechanism: str = 'PLAIN'
def test_kafka():
    kafka_client = get_client(brokers=hosts, 
                              group_id='yy-test-group-id',
                              consumer_config=consumer_config,
                              security_protocol=security_protocol,
                              sasl_mechanism=sasl_mechanism,
                              )
    kafka_client.produce_message(topic='test-topic', value={'nihao': '1'})
    kafka_client.consume_messages(topics=['test-topic'], handle_func=handle_message)
test_kafka()