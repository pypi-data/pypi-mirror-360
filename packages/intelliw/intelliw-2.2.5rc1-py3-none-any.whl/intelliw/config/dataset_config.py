import json
import os
from typing import Tuple

from intelliw.config import config


def set_dataset_config(dataset_id: str = None, dataset_ratio: list = None,
                       local_csv: Tuple[str, list] = None,
                       local_corpus: str = None):
    """通过ai工作坊接口设置数据集所需的环境变量

    Args:
        dataset_id (str): 数据集id, 从ai工作坊页面上获取
        dataset_ratio(list): 数据机训练集，验证集，测试集比例， 0.7:0.3:0.1
        local_csv(str, list): 本地csv文件位置，支持多数据集合
        local_corpus(str): 本地nlp语料文件位置

    所需环境变量:
        SOURCE_TYPE = 3
        INPUT_MODEL_ID = ''
        INPUT_DATA_SOURCE_ID = ''
        INPUT_DATA_SOURCE_TRAIN_TYPE = 2
        DATA_SOURCE_ADDRESS = ''

        if SOURCE_TYPE = 1
            NEED: DATA_SOURCE_ADDRESS
        if SOURCE_TYPE = 2
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_MODEL_ID
        if SOURCE_TYPE = 4
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_DATA_SOURCE_ID, INPUT_DATA_SOURCE_TRAIN_TYPE
        if SOURCE_TYPE = 5
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_DATA_SOURCE_ID
        if SOURCE_TYPE = 21
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_DATA_SOURCE_ID,
                  INPUT_DATA_SOURCE_TRAIN_TYPE, NLP_CORPORA_INPUT_TYPE
    """

    if dataset_ratio is None:
        dataset_ratio = [0.7, 0.3, 0]

    if not any([local_csv, local_corpus, dataset_id]):
        config.SOURCE_TYPE = 0
        return
    config.SOURCE_TYPE = -1

    if not isinstance(local_csv, (list, str)):
        local_csv = None

    if local_csv:
        _csv_file_check = all(os.path.exists(c) for c in local_csv) if isinstance(
            local_csv, list) else os.path.exists(local_csv)
    else:
        _csv_file_check = False
    _nlp_corpus_check = os.path.exists(local_corpus) if local_corpus else False

    if not any([dataset_id, _csv_file_check, _nlp_corpus_check]):
        raise ValueError(
            "数据集错误,请通过--csv设置本地csv文件 或 -C设置本地nlp语料文件夹, 或者--dataset设置在线数据集")

    config.TRAIN_DATASET_RATIO = dataset_ratio[0]
    config.VALID_DATASET_RATIO = dataset_ratio[1]
    config.TEST_DATASET_RATIO = dataset_ratio[2]

    dataset_list = []
    if not dataset_id:
        if local_csv:
            if isinstance(local_csv, str):
                dataset_list = [{"SOURCE_TYPE": 3, "CSV_PATH": local_csv}]
            elif isinstance(local_csv, list):
                dataset_list = [{"SOURCE_TYPE": 3, "CSV_PATH": c}
                                for c in local_csv]
        elif local_corpus:
            dataset_info = {"SOURCE_TYPE": 21, "NLP_CORPORA_PATH": local_corpus,
                            "NLP_CORPORA_INPUT_TYPE": "local", "INPUT_DATA_SOURCE_ID": "",
                            "INPUT_DATA_SOURCE_TRAIN_TYPE": config.INPUT_DATA_SOURCE_TRAIN_TYPE}
            dataset_list.append(dataset_info)
    else:
        config.update_by_env()
        from intelliw.utils import iuap_request
        # Shit, shit
        if os.environ.get('useGpaas') == 'true':
            dataset_url = f"{os.environ.get('domain.url')}{os.environ.get('DATASET_BY_ID_ADDRESS')}"
        else:
            dataset_url = os.environ.get('DATASET_BY_ID_ADDRESS')
        for i in dataset_id.split(","):
            dataset_info = {}
            resp = iuap_request.get(dataset_url, params={"dataSetId": i})
            resp.raise_for_status()
            body = resp.json
            if body['status'] == 0:
                raise ConnectionAbortedError(
                    f"get dataset info response: {body}")
            result = body['data']
            source = result["SOURCE_TYPE"]
            if result.get("TENANT_ID"):
                dataset_info["TENANT_ID"] = result.get("TENANT_ID")
                config.TENANT_ID = result.get("TENANT_ID")
            if source == 1:
                dataset_info["DATA_SOURCE_ADDRESS"] = result["DATA_SOURCE_ADDRESS"]
            else:
                dataset_info["INPUT_ADDR"] = result["INPUT_ADDR"]
                dataset_info["INPUT_GETROW_ADDR"] = result["INPUT_GETROW_ADDR"]
                if source == 2:
                    mid = result["INPUT_MODEL_ID"]
                    dataset_info["INPUT_GETROW_ADDR"] = result["INPUT_GETROW_ADDR"]
                    dataset_info["INPUT_MODEL_ID"] = mid
                elif source == 4:
                    dataset_info["INPUT_DATA_SOURCE_ID"] = result["INPUT_DATA_SOURCE_ID"]
                elif source == 5:
                    dataset_info["INPUT_DATA_SOURCE_ID"] = result["INPUT_DATA_SOURCE_ID"]
                    dataset_info["INPUT_DATA_META_ADDR"] = result["INPUT_DATA_META_ADDR"]
                elif source == 9:
                    dataset_info["INPUT_ADDR"] = result["INPUT_ADDR"]
                    dataset_info["INPUT_MODEL_ID"] = result["INPUT_MODEL_ID"]
                    dataset_info["USER_ID"] = os.environ.get("USER_ID")
                elif source == 21:
                    dataset_info["INPUT_DATA_SOURCE_ID"] = result["INPUT_DATA_SOURCE_ID"]
                    dataset_info["NLP_CORPORA_INPUT_TYPE"] = result["NLP_CORPORA_INPUT_TYPE"]
                elif source == 24:
                    dataset_info["INPUT_DATA_SOURCE_ID"] = result["INPUT_DATA_SOURCE_ID"]
                    dataset_info["FINE_TUNING_SET_TYPE"] = dataset_info["FINE_TUNING_SET_TYPE"]
            dataset_info["SOURCE_TYPE"] = source
            dataset_list.append(dataset_info)
    config.DATASET_INFO = json.dumps(dataset_list, ensure_ascii=False)
