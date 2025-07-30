import os
import sys
import inspect

# 方便别人引用, 不要删除
from intelliw.config.dataset_config import set_dataset_config


class FrameworkMode:
    """
    算法框架流程
    """
    Import = "import"
    Train = "train"
    Infer = "infer"
    Batch = "batch"
    DistTrain = "distributedtrain"


FLAME_PROF_MODE = False
FRAMEWORK_MODE = ''  # import/train/infer/batch

# SSL
INTELLIW_SSL_FILEPATH = ""

# 运行模式 SCAFFOLDING 脚手架，SERVER 服务端
RUNNING_MODE = 'SERVER'
REGISTER_CLUSTER_ADDRESS = ''  # 服务的ip➕端口  json: ['','']
# 校验镜像环境
CHECK_CERTIFIED_IMAGE = False

# basic
TENANT_ID = ''
# 实例 id，代表当前运行实例
INSTANCE_ID = ''
# 推理任务 id
INFER_ID = ''
# 任务 id，推理任务时与 INFER_ID 相同
SERVICE_ID = ''
# 是否专属化
IS_SPECIALIZATION = 0

INFER_CACHE = False
INFER_CACHE_TTL = 10

# 数据集相关
DATASET_BY_ID_ADDRESS = ""  # 通过url可以获取数据集所需的所有环境信息
SOURCE_TYPE = 0  # 0/6/7/8  # 0-空数据  6-表格数据 7-图像数据 8-文本数据
DATASET_INFO = ''
# cv: 0-自有 1-labelme 2-voc 3-coco  nlp: 20-txt 21-csv 22-json
INPUT_DATA_SOURCE_TRAIN_TYPE = 22
""" 数据集信息, json list
空 0:
表格 6:
    远程csv  1
    智能分析  2
    本地csv  3
    数据工场  5
    语义模型  9
图像 7:
    图片数据源 4
文本 8:
    nlp语料 21

CSV_PATH = ''
DATA_SOURCE_ADDRESS = ''
INPUT_ADDR = ''
INPUT_GETROW_ADDR = ''
INPUT_MODEL_ID = ''
INPUT_DATA_SOURCE_ID = ''
INPUT_DATA_SOURCE_TRAIN_TYPE = 2 cv: 0-自有 1-labelme 2-voc 3-coco  nlp: 20-txt 21-csv 22-json
"""

# 数据输出 输出数据源类型，0 空，2 智能分析, 5 数据工场
OUTPUT_DATASET_INFO = '{"sourceType":0}'

# 数据读取
DATA_SOURCE_READ_SIZE = 5000
DATA_SOURCE_READ_LIMIT = sys.maxsize
TRAIN_DATASET_RATIO = 0.8  # 训练集比例
VALID_DATASET_RATIO = 0.2  # 验证集比例
TEST_DATASET_RATIO = 0.0  # 测试集比例
DATA_SPLIT_MODE = 1  # 数据集划分模式, -1 不分割, 0 顺序划分，1 全局随机划分，2 根据目标列随机划分
DATA_RANDOM_SEED = 1024 #数据集分割seed，当 DATA_SPLIT_MODE=1，2 时候生效

# cv数据存储文件名
CV_IMG_FILEPATH = "tmp_local_cv_image_data/"
CV_IMG_TRAIN_FILEPATH = os.path.join(CV_IMG_FILEPATH, "train/")
CV_IMG_VAL_FILEPATH = os.path.join(CV_IMG_FILEPATH, "val/")
CV_IMG_TEST_FILEPATH = os.path.join(CV_IMG_FILEPATH, "test/")
CV_IMG_ANNOTATION_FILEPATH = os.path.join(CV_IMG_FILEPATH, "annotations/")

# nlp语料存储文件名
# nlp数据格式，接口获取数据为：文件、行 或 为 本地数据（file/row/local）
NLP_CORPORA_INPUT_TYPE = 'local'
NLP_CORPORA_FILEPATH = "tmp_local_nlp_corpora_data/"
NLP_CORPORA_TRAIN_FILEPATH = os.path.join(NLP_CORPORA_FILEPATH, "train/")
NLP_CORPORA_VAL_FILEPATH = os.path.join(NLP_CORPORA_FILEPATH, "val/")
NLP_CORPORA_TEST_FILEPATH = os.path.join(NLP_CORPORA_FILEPATH, "test/")

# 大模型数据存储文件名
# 大模型数据格式，接口获取数据为：行row
LARGE_MODEL_INPUT_TYPE = 'row'
LARGE_MODEL_FILEPATH = "tmp_local_large_model_data/"
LARGE_MODEL_TRAIN_FILEPATH = os.path.join(LARGE_MODEL_FILEPATH, "train/")
LARGE_MODEL_VAL_FILEPATH = os.path.join(LARGE_MODEL_FILEPATH, "val/")
LARGE_MODEL_TEST_FILEPATH = os.path.join(LARGE_MODEL_FILEPATH, "test/")

# 推理服务
TOKEN = ''  # API 响应 token
API_EXTRAINFO = True  # API 响应包含 extra info
INFER_MULTI_PROCESS = False  # 是否多进程
INFER_MULTI_THREAD_COUNT = 0  # 自定义线程数
INFER_MULTI_PROCESS_COUNT = 0  # 自定义进程数
INFER_MAX_TASK_RATIO = 3  # 最大任务数是几倍的线程数

MAINPID = ''

# 云存储相关
STORAGE_SERVICE_PATH = ''
STORAGE_SERVICE_URL = ''
FILE_UP_TYPE = ""  # 对应的类型 AliOss/Minio

# AuthSDK
ACCESS_KEY = ''
ACCESS_SECRET = ''
GENERATOR_YHT_URL = ''
TEMPORARY_USER_COOKIE = ''

# eureka
START_EUREKA = False
EUREKA_ZONE = 'test'  # online/pre/test/daily
EUREKA_SERVER = ''  # eureka服务地址
EUREKA_APP_NAME = ''  # 注册服务名称
EUREKA_PROVIDER_ID = ''  # 注册服务租户

# 分布式
DIST_IS_MASTER = False

# Spark
SPARK_MODE = False
SPARK_MASTER_URL = ''

# checkpoint
CHECKPOINT_MODE = False
CHECKPOINT_SAVE_MAX = 100

# resources
CPU_COUNT = ""


def is_server_mode():
    """
    online or local
    """
    return 'SERVER' == RUNNING_MODE


def str2bool(string: str) -> bool:
    """
    Convert a string to a boolean value.
    """
    return string.lower() == 'true'


def update_by_env():
    """
    Update module variables based on environment variable values.

    This function iterates over all variables defined in the current module (__name__)
    and checks if there is a corresponding environment variable with the same name.
    If so, it updates the variable's value to the one defined in the environment variable.

    Raises:
        KeyError: if an expected environment variable is not set.

    Returns:
        None
    """
    domain = os.environ.get('domain.url')
    useGpaas = str2bool(os.environ.get('useGpaas', 'false'))
    for k, v in globals().items():
        if not k.startswith('__') and not inspect.isfunction(v) and not inspect.ismodule(v):
            env_val = os.environ.get(k, os.environ.get(k.upper()))
            if env_val is not None and env_val != '':
                if isinstance(v, bool):
                    env_val = str2bool(env_val)
                    globals()[k] = env_val
                else:
                    try:
                        env_val = type(v)(env_val)
                        globals()[k] = env_val
                    except ValueError:
                        pass
            elif env_val == '' and isinstance(v, str):
                globals()[k] = env_val
            
            # 恶心的规则
            if useGpaas:
                if k == "access.key":
                    globals()["ACCESS_KEY"] = env_val
                if k == "access.secret":
                    globals()["ACCESS_SECRET"] = env_val
                if k == "useIPv6":
                    globals()["USE_IPV6"] = env_val
                if k == "STORAGE_SERVICE_URL":
                    globals()[k] = f"{domain}env_val"
                if k == "GENERATOR_YHT_URL":
                    globals()[k] = f"{domain}env_val"
                if k == "REPORT_ADDR":
                    globals()[k] = f"{domain}env_val"
                if k == "DATASET_BY_ID_ADDRESS":
                    globals()[k] = f"{domain}env_val"
        if useGpaas:
            # ACCESS_SECRET, ACCESS_SECRET 为空，使用 access.key, access.secret 
            if globals().get("ACCESS_KEY") is None and os.environ.get("access.key") is not None \
                and globals().get("ACCESS_SECRET") is None and os.environ.get("access.secret") is not None:
                globals()["ACCESS_KEY"] = os.environ.get("access.key")
                globals()["ACCESS_SECRET"] = os.environ.get("access.secret")

            # ACCESS_SECRET, ACCESS_SECRET 为空，使用 cf_clientAccessKey, cf_clientAccessSecret
            if globals().get("ACCESS_KEY") is None and os.environ.get("cf_clientAccessKey") is not None \
                and globals().get("ACCESS_SECRET") is None and os.environ.get("cf_clientAccessSecret") is not None:
                globals()["ACCESS_KEY"] = os.environ.get("cf_clientAccessKey")
                globals()["ACCESS_SECRET"] = os.environ.get("cf_clientAccessSecret")

