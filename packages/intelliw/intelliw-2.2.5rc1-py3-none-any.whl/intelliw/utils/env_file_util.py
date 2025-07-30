import os
import logging


logger = logging.getLogger('env_file')


def read_env_file():
    try:
        env_file = os.environ.get('ENV_FILE')
        if not env_file:
            logger.warning("未找到ENV_FILE配置变量, 返回")
            return
        # 判断文件列表中的文件都存在 否则返回错误信息
        if not os.path.exists(env_file):
            logger.warning(f"未找到配置文件 {env_file}, 返回")
            return

        with open(env_file, 'r') as f:
            for line in f.readlines():
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    except Exception as e:
        logger.error("ENV_FILE配置文件读取失败", e)