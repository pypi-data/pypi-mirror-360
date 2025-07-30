import gc
import time
import json
import traceback
from concurrent.futures import ThreadPoolExecutor

try:
    from confluent_kafka import Producer, Consumer, KafkaError
except ImportError:
    raise ImportError("\033[31mIf use kafka, you need: pip install confluent_kafka>=2.5.3 \033[0m")
import threading
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class KafkaClient:

    def __init__(self, brokers: str, group_id: str = None, username: str = None, password: str = None,
                 producer_config: dict = None, consumer_config: dict = None, security_protocol: str = 'SASL_PLAINTEXT',
                 sasl_mechanism: str = 'PLAIN', key_serializer=None, value_serializer=None):
        """
        Kafka 通用客户端初始化
        :param brokers: Kafka 集群的地址 (例如 'localhost:9092')
        :param group_id: 消费者使用的分组ID，生产者可忽略
        :param username: SASL 验证用的用户名
        :param password: SASL 验证用的密码
        :param producer_config: 自定义的生产者配置字典
        :param consumer_config: 自定义的消费者配置字典
        :param security_protocol: 安全协议，例如 'SASL_SSL' 或 'SASL_PLAINTEXT'
        :param sasl_mechanism: SASL 认证机制，'PLAIN' 适用于用户名和密码的认证方式
        :param key_serializer: 用于序列化 key 的函数
        :param value_serializer: 用于序列化 value 的函数
        """
        self.brokers = brokers
        self.group_id = group_id
        self.username = username
        self.password = password
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism
        self.producer_config = producer_config or {}
        self.consumer_config = consumer_config or {}
        self.key_serializer = key_serializer or self.default_serializer
        self.value_serializer = value_serializer or self.default_serializer

        self.producer = None

        logger.info(
            f"Kafka Client initialized with brokers: {brokers}, "
            f"producer_config: {self.producer_config}, "
            f"consumer_config: {self.consumer_config}")

    @staticmethod
    def default_serializer(data):
        if isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, (dict, list, tuple)):
            return json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif isinstance(data, (int, float, bool)):
            return str(data).encode('utf-8')
        return data

    def _get_security_config(self):
        if self.username and self.password:
            return {
                'sasl.mechanism': self.sasl_mechanism,
                'security.protocol': self.security_protocol,
                'sasl.username': self.username,
                'sasl.password': self.password,
            }
        return {}

    def create_producer(self):
        """创建 Kafka 生产者，优先使用用户传入配置"""
        default_producer_conf = {
            'bootstrap.servers': self.brokers,
            'linger.ms': 10,  # 批量发送时等待时间
            'batch.num.messages': 1000,  # 批量发送的最大消息数
            'queue.buffering.max.ms': 1000,  # 最大缓冲时间
            'message.timeout.ms': 30000,  # 消息超时配置
            'retries': 5,  # 消息发送失败重试次数
        }
        security_conf = self._get_security_config()
        config = {**default_producer_conf, **security_conf, **self.producer_config}
        return Producer(config)

    def create_consumer(self, topics: list):
        """创建 Kafka 消费者，优先使用用户传入配置"""
        default_consumer_conf = {
            'bootstrap.servers': self.brokers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',  # 从最早的偏移量开始消费
            'enable.auto.commit': False,  # 手动提交偏移量
        }
        security_conf = self._get_security_config()  # 获取 SASL 安全配置
        config = {**default_consumer_conf, **security_conf, **self.consumer_config}
        consumer = Consumer(config)
        consumer.subscribe(topics)
        return consumer

    def produce_message(self, topic: str, key: str = None, value: str = None, raise_error=False):
        """发送 Kafka 消息"""
        assert not (value is None and key is None), 'Need at least one: key or value'

        serialized_key = self.key_serializer(key)
        serialized_value = self.value_serializer(value)

        assert type(serialized_key) in (bytes, bytearray, memoryview, type(None))
        assert type(serialized_value) in (bytes, bytearray, memoryview, type(None))

        if self.producer is None:
            self.producer = self.create_producer()

        try:
            self.producer.produce(topic, key=serialized_key, value=serialized_value, callback=delivery_callback)
            [self.producer.poll(0.05) for _ in range(3)]
        except Exception as e:
            logger.error(f"Error producing message to topic '{topic}', key: {serialized_key}, error: {e}")
            if raise_error:
                raise  # 直接抛出原异常，保留异常信息
        finally:
            self.producer.flush()

    def produce_messages_in_batch(self, topic: str, messages: list, poll_interval: float = 0.1):
        """
        批量发送 Kafka 消息
        :param topic: Kafka topic
        :param messages: 消息列表，包含 (key, value) 元组
        :param poll_interval: 每隔多少秒调用一次 poll() 以确保消息发送
        """
        if self.producer is None:
            self.producer = self.create_producer()

        try:
            for key, value in messages:
                self.producer.produce(topic, key=key, value=value, callback=delivery_callback)
                self.producer.poll(0)  # 定期调用以处理异步消息

            while True:
                remaining_messages = self.producer.flush(0)
                if remaining_messages == 0:
                    break
                time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Error producing message batch: {e}")

    def consume_messages(self, topics: list, handle_func, timeout=1.0, return_by_empty=False, return_by_count=0,
                         return_by_func=None):
        """
        消费 Kafka 消息
        :param topics: Kafka topic list
        :param handle_func: message 后处理方法，
            方法需要有两个参数，例如：
             - def handle_message(key, value)
             - def delivery_callback(err, msg)
            第一个参数代表consumer的 message.key(), 第二个参数为consumer的 message.value()
        :param timeout: 获取消息超时时长
        :param return_by_empty: 当获取消息 None 时结束
        :param return_by_count 当获取消息数量等于count时结束, 0为不限制
        :param return_by_func  参数传入一个方法，方法参数与handle_func相同，返回类型需要为 bool 型，当返回为 True 时，消费停止
        """

        consumer = self.create_consumer(topics)

        try:
            count = 0
            while True:
                msg = consumer.poll(timeout)
                if msg is None:
                    # 当获取消息 None 时结束
                    if return_by_empty:
                        return None
                    continue
                if msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        logger.error(f"Kafka error: {msg.error()}")
                    continue
                handle_func(msg.key(), msg.value())  # 处理消息
                consumer.commit()  # 手动提交偏移量
                count += 1

                # 当获取消息数量等于count时结束
                if return_by_count and count >= return_by_count:
                    return None
                if return_by_func and return_by_func(msg.key(), msg.value()) is True:
                    return None

                # 定期调用垃圾回收
                if count % 10 == 0:
                    gc.collect()

        except Exception as e:
            logger.error(f"Error consuming messages: {e}, {traceback.format_exc()}")
        finally:
            consumer.close()

        return None

    def consume_messages_with_threads(self, topics: list, handle_func, num_threads=5, timeout=1.0):
        def consumer_task():
            self.consume_messages(topics, handle_func, timeout)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(consumer_task) for _ in range(num_threads)]
            for future in futures:
                future.result()  # 等待所有线程完成任务


def delivery_callback(err, msg):
    if err:
        logger.error(f"Message failed delivery: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def handle_message(key, value):
    logger.info(f"Received message with key: {key}, value: {value}")
