import json
import time

from intelliw.utils.kafka import get_client, handle_message
import os

os.environ['kafka.cluster.hosts'] = '172.20.32.80:9092,172.20.32.82:9092,172.20.32.83:9092'


def test_get_client_with_args(group_id):
    """
    测试通过直接传参获取 Kafka 配置
    """
    return get_client(
        brokers='localhost:9092',
        group_id=group_id,
        username='custom_user',
        password='custom_pass',
        producer_config={'acks': 'all'},
        consumer_config={'auto.offset.reset': 'earliest',
                         'enable.auto.commit': True,
                         'max.poll.interval.ms': 8000000,
                         'heartbeat.interval.ms': 3000,
                         'session.timeout.ms': 30000}
    )


def test_get_client_with_env(group_id):
    """
    测试通过直接传参获取 Kafka 配置
    """
    return get_client(
        group_id="test.tenders.2",
        consumer_config={'auto.offset.reset': 'earliest',
                         'enable.auto.commit': True,
                         'max.poll.interval.ms': 8000000,
                         'heartbeat.interval.ms': 3000,
                         'session.timeout.ms': 30000
                         }
    )


class MyConsumer:
    def __init__(self):
        # 初始化代码
        pass

    def return_func(self, k, v):
        return True
        # data = json.loads(v)
        # id = data['data'][0]['id']
        # if id == "2118076642662809607":
        #     return True
        # return False

    def handle_message(self, k, v):
        # 使用 self 访问实例属性
        data = json.loads(v)
        ts = data['data'][0]['done_ts'] / 1000
        id = data['data'][0]['id']
        chunk_info = data['data'][0]['chunk_info']
        timeArray = time.localtime(ts)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print(f"Received message with key: {k}, {otherStyleTime}, {id}, {chunk_info}")

    def run(self):
        # client = test_get_client_with_args('consumer1')
        client = get_client(
            group_id="mm.test.doc.10.bge",
            consumer_config={'auto.offset.reset': 'earliest',
                             'max.poll.interval.ms': 8000000,
                             'heartbeat.interval.ms': 3000,
                             'session.timeout.ms': 30000
                             }
        )
        # b = get_client()
        # print('start producing...')
        client.produce_message(topic='test-topic', value={'nihao': '1'})
        # client.produce_messages_in_batch(topic='test-topic', messages=[(f'key{i}', f'value{i}') for i in range(100)])

        # print('start consuming...')
        client.consume_messages(topics=["iuap_aip_service_topic_file_process"], handle_func=self.handle_message,
                                return_by_func=self.return_func)
        client.consume_messages_with_threads(topics=['iuap_aip_service_topic_file_process'], handle_func=self.handle_message, num_threads=10)


if __name__ == '__main__':
    myc = MyConsumer()
    myc.run()
