import os
import sys
import traceback
import argparse
import intelliw.utils.iuap_request as requests
from intelliw.datasets.datasets import get_dataset
from intelliw.core.infer import Infer
from intelliw.core.trainer import Trainer
from intelliw.core.custom import Custom
from intelliw.utils.logger import get_logger
from intelliw.utils.gen_model_cfg import generate_model_config_from_algorithm_config as __generate
from intelliw.config import config as iwconfig, dataset_config

report_addr = None
logger = get_logger(level='DEBUG')

#########################################################
#                请按照需求填写以下配置                     #
#########################################################
# (必须)设置算法文件位置（algorithms.py根目录）
PACKAGE_PATH = "./"

algorithm_yaml_path = os.path.join(PACKAGE_PATH, 'algorithm.yaml')
model_yaml_path = os.path.join(PACKAGE_PATH, 'model.yaml')
iwconfig.RUNNING_MODE = 'SCAFFOLDING'


# 训练测试(通过算法框架调用train)
def debug_train():
    '''(debug_train时必填)
    设置训练测试数据
    example:
        DATASET_ID = "asdasdasdasdas"   数据集id,获取途径 AI工作坊数据集管理中获取id, 不使用传入None
        TRAIN_CSV_PATH = "localcsvpath" or ["localcsvpath1", "localcsvpath2"]  本地训练csv, 如果写了DATASET_ID, 优先DATASET_ID
        DATASET_RATIO = [0.7, 0.2, 0.1] 训练/验证/测试 数据集比例, 值在0-1之间
        iwconfig.DATA_SPLIT_MODE = 0    数据集划分模式, 0 顺序划分,1 随机划分, 2 根据特征列进行划分(需要在algorithm.yaml的超参中增加targetCol,来指明特征列下标)

        TRAIN_NLP_CORPORA = "/home/xxx/xxx/"   本地训练nlp语料文件夹, 如果写了DATASET_ID, 优先DATASET_ID

        # cv标注类型: 0-自有 1-labelme 2-voc 3-coco
        # nlp语料文件类型: 20-txt 21-csv 22-json
        iwconfig.INPUT_DATA_SOURCE_TRAIN_TYPE = 1

    '''
    DATASET_ID = None

    # csv
    TRAIN_CSV_PATH = None

    # nlp
    TRAIN_NLP_CORPORA = None  # 需要是文件夹

    # cv标注类型: 0-自有 1-labelme 2-voc 3-coco
    # nlp语料文件类型: 20-txt 21-csv 22-json
    iwconfig.INPUT_DATA_SOURCE_TRAIN_TYPE = 22

    DATASET_RATIO = [0.7, 0.2, 0.1]
    iwconfig.DATA_SPLIT_MODE = 1  # 0-顺序划分 1-随机划分
    iwconfig.DATA_RANDOM_SEED = 1024 # 

    dataset_config.set_dataset_config(DATASET_ID, DATASET_RATIO,
                                      TRAIN_CSV_PATH, TRAIN_NLP_CORPORA)

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        trainer = Trainer(PACKAGE_PATH)
        train_data = get_dataset(iwconfig.DATASET_INFO)
        trainer.train(train_data)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# 推理测试
def debug_infer():
    '''(debug_infer时必填)
    设置推理训练数据
    example: INFER_DATA = {"data":[1,2,3]}
    '''
    INFER_DATA = None
    try:
        import asyncio
        __generate(algorithm_yaml_path, model_yaml_path)
        infer = Infer(PACKAGE_PATH)
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(infer.infer(INFER_DATA))
        print(result)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# 多api测试
def debug_router():
    '''(debug_router时必填)
    设置多api
    example:
        INFER_DATA = {"data":base64}
        ROUTER_FUNC = api_test
    '''
    INFER_DATA = None
    ROUTER_FUNC = None

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        infer = Infer(PACKAGE_PATH)
        instance = infer.pipeline.instance
        result = getattr(instance, ROUTER_FUNC)(INFER_DATA)
        print(result)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# http服务测试
def debug_infer_http_server():
    # (debug_infer_http_server时必填)设置http服务测试
    SERVER_PORT = 8888

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        sys.argv = ["api.main", "-p", PACKAGE_PATH, "--port", str(SERVER_PORT)]
        from intelliw.interface.iwapi import iwmain
        iwmain.api_service.run()
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute apiService and stack:\n{}".format(str(stack_info)))


# http接口测试
def debug_server_available():
    '''(debug_server_available时必填)
    http接口测试
    example：
        URL = "http://xxx.xxx.xxx/predict"
        METHOD = "get/post"
        INFER_DATA = {"data":base64}
    '''
    URL = "https://127.0.0.1:8888/predict"
    # METHOD = "post"
    INFER_DATA = None

    # resp = requests.request(METHOD, URL, json=INFER_DATA, timeout=60)
    resp = requests.post_json(url=URL, json=INFER_DATA, timeout=60)
    if resp.status != 200:
        resp.raise_for_status()
    print(resp.body)


def debug_custom():
    # 任务类型
    FRAMEWORK_MODE = "infer"  # importalg/importmodel/infer/train

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        custom = Custom(PACKAGE_PATH, procedure_type=FRAMEWORK_MODE)
        custom.run()
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))

func_dict = {
    'train': debug_train,
    'infer': debug_infer,
    'router': debug_router,
    'infer_http_server': debug_infer_http_server,
    'server_available': debug_server_available,
    'custem': debug_custom,
}

def run(args):
    job_type = args.job_type
    if job_type not in func_dict:
        logger.error("job type %s not found", job_type)
    else:
        func_dict[job_type]()


if __name__ == '__main__':
    if PACKAGE_PATH is None:
        raise FileNotFoundError("请在debug_controller.py中设置PACKAGE_PATH")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-j", "--job_type", default="infer", type=str, help="job type")
    args = parser.parse_args()

    try:
        run(args)
        # debug_train()
        # debug_infer()
        # debug_router()
        # debug_infer_http_server()
        # debug_server_available()
        # debug_custom
    except (ImportError, TypeError) as e:
        print(
            "\033[1;31;40m如果为debug文件错误， 请通过命令 `intelliw init_debug` 更新debug文件\033[0m")
        traceback.print_exc()
