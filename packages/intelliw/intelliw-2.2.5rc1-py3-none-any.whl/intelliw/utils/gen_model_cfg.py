from intelliw.config.cfg_parser import load_config
import yaml
import os
from functools import wraps


def verify_and_generate_model_cfg(func):
    @wraps(func)
    def verify(*args):
        if not os.path.exists(args[1]):
            if not os.path.exists(args[0]):
                raise ValueError(
                    "missing algorithm.yaml at path: {}".format(args[0]))
            print('model.yaml does not exists, generating model.yaml to [{}] based on [{}].'.format(
                args[1], args[0]))
            func(*args)

    return verify


@verify_and_generate_model_cfg
def generate_model_config_from_algorithm_config(algorithm_config_path, model_config_path, location="model"):
    """
    根据 algorithm.yaml 生成 model.yaml

    :param algorithm_config_path: algorithm.yaml path
    :param model_config_path: model.yaml path
    :param location: model path
    """
    algo_cfg = load_config(algorithm_config_path)
    model_cfg = {
        "Model": {
            "name": algo_cfg["AlgorithmInformation"]["name"],
            "desc": algo_cfg["AlgorithmInformation"]["desc"],
            "location": location,
            "algorithm": {
                "name": algo_cfg["AlgorithmInformation"]["name"],
                "desc": algo_cfg["AlgorithmInformation"]["desc"],
            }
        }
    }
    _algo_cfg = algo_cfg["AlgorithmInformation"]["algorithm"]
    if "metadata" in _algo_cfg:
        model_cfg["Model"]["metadata"] = _algo_cfg["metadata"]
    if "transforms" in _algo_cfg:
        model_cfg["Model"]["transforms"] = _algo_cfg["transforms"]
    if "parameters" in _algo_cfg and isinstance(_algo_cfg["parameters"], list):
        params = {}
        for item in _algo_cfg["parameters"]:
            if "key" in item and "val" in item:
                params[item["key"]] = item["val"]
        model_cfg["Model"]["parameters"] = params
    if "command" in algo_cfg["AlgorithmInformation"]:
        command = algo_cfg["AlgorithmInformation"].get("command", [])
        args = algo_cfg["AlgorithmInformation"].get("args", [])
        if not args and command:
            raise Exception("自定义启动命令command不能为空")
        for a in args:
            command.extend([a['key'], a['val']])
        model_cfg["Model"]["boot"] = command
    if "system" in algo_cfg["AlgorithmInformation"]:
        params = {}
        for item in algo_cfg["AlgorithmInformation"]['system']["parameters"]:
            if "key" in item and "val" in item:
                params[item["key"]] = item["val"]
        model_cfg["Model"]["system"] = params
    model = yaml.dump(model_cfg, default_flow_style=False, allow_unicode=True)

    f = open(model_config_path, 'w', encoding='utf-8')
    f.write(model)
    f.close()
