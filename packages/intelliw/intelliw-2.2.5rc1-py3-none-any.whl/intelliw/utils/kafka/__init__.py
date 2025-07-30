"""
Author: Hexu
Date: 2022-05-05 12:07:16
LastEditors: Hexu
LastEditTime: 2024/9/23 09:56
FileName: __init__.py
Description: 
"""
import os

from intelliw.utils.kafka.client import KafkaClient, handle_message, delivery_callback

from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


def _get_args(brokers: str, username: str, password: str):
    """
    获取 Kafka 连接参数，优先使用传入参数，若未提供则从环境变量中获取
    """
    args = {
        'brokers': brokers or os.environ.get('kafka.cluster.hosts', ''),
    }

    if not args['brokers']:
        raise KeyError('Brokers information is missing')

    kafka_auth_enable = os.environ.get('kafka.authentication.enable', '')

    # 如果启用了认证，则获取用户名和密码
    if kafka_auth_enable.lower() == 'true':
        args['username'] = username or os.environ.get('kafka.username', '')
        args['password'] = password or os.environ.get('kafka.password', '')

    return args


def get_client(brokers: str = None, group_id: str = None, username: str = None, password: str = None,
               producer_config: dict = None, consumer_config: dict = None,
               security_protocol: str = 'SASL_PLAINTEXT', sasl_mechanism: str = 'PLAIN',
               key_serializer=None, value_serializer=None):
    """
    创建 Kafka 客户端实例
    :param brokers: Kafka 集群地址
    :param group_id: 消费者分组 ID
    :param username: SASL 验证用的用户名
    :param password: SASL 验证用的密码
    :param producer_config: 生产者配置
    :param consumer_config: 消费者配置
    :param security_protocol: 安全协议，默认为 SASL_PLAINTEXT
    :param sasl_mechanism: SASL 认证机制，默认为 PLAIN
    :param key_serializer: 用于序列化 key 的函数
    :param value_serializer: 用于序列化 value 的函数
    :return: KafkaClient 实例或 None（如果获取参数失败）
    """

    try:
        args = _get_args(brokers, username, password)

        kafka_client = KafkaClient(
            brokers=args['brokers'],
            group_id=group_id,
            username=args.get('username'),
            password=args.get('password'),
            producer_config=producer_config,
            consumer_config=consumer_config,
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            key_serializer=key_serializer,
            value_serializer=value_serializer
        )
        return kafka_client

    except KeyError as e:
        logger.error(f"Kafka args error: {e}")
        return None
