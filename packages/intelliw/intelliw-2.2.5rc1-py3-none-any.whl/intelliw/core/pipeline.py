#!/usr/bin/env python
# coding: utf-8
import asyncio
import inspect
import json
import threading
import traceback
import importlib
import os
import time
import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from inspect import signature
from typing import Tuple, Union
from intelliw.config.cfg_parser import load_config
from intelliw.datasets.datasets import DataSets, MultipleDataSets
from intelliw.utils import exception, yms_downloader, yms_downloader_v2
from intelliw.utils.exception import ModelLoadException, LimitConcurrencyError
from intelliw.utils import prepare_algorithm_parameters, prepare_model_parameters, import_code, get_first_element
from intelliw.utils.check_algorithm_py import is_valid_algorithm
import intelliw.utils.message as message
from intelliw.core.recorder import Recorder
from intelliw.core.linkserver import linkserver
from intelliw.utils import iprofile
from intelliw.utils.context._context import CurrentReq, header_ctx
from intelliw.utils.logger import _get_framework_logger, _get_algorithm_logger
from intelliw.config import config
from intelliw.utils.global_val import gl
from intelliw import functions
from intelliw.core.al_decorator import make_decorators_server
from intelliw.utils import hijack_function

logger = _get_framework_logger()


class Const:
    # 文件
    algorithmInformation = "AlgorithmInformation"
    algorithm = "algorithm"
    algorithm_py = "algorithm.py"
    algorithm_yaml = "algorithm.yaml"
    model_yaml = "model.yaml"

    # 处理过程
    pre_predict = "pre-predict"
    post_predict = "post-predict"
    pre_train = "pre-train"
    post_train = "post-train"

    # 其他
    new_target_name = "new_target_data_unrepeatable_name"
    metadata = "metadata"
    model_type = "modelType"
    predict_type = "predictType"
    target = "target"
    target_name = "targetName"
    target_col = "targetCol"
    target_code = "targetCode"

    link_server = "linkserver"

    parameters = 'parameters'
    parametersUp = 'PARAMETERS'
    system = 'system'
    delivery = 'delivery'


def get_model_yaml():
    return Const.model_yaml


class Pipeline:
    def __init__(self, reporter: Tuple[str, Recorder] = None):
        self.alldata_transforms = None  # 自定义针对总体数据结构处理的  特征工程
        self.splitdata_transforms = None  # 自定义针对单条数据数据结构处理的  特征工程
        self.feature_transforms = None  # 内置针对总体数据结构处理的  特征工程
        self.recorder = reporter if isinstance(reporter, Recorder) else Recorder(
            reporter)
        self.instance = None
        self.custom_router = []
        self.alg_describe = ''
        self.background_tasks = set()
        self.async_executor = ThreadPoolExecutor(999)
        self.max_wait_task = 999
        self.thread_data_pool = {}

    @staticmethod
    def _check_certified_image():
        # 检查是不是规范化镜像（onnx）
        if any([importlib.util.find_spec("torch"),
                importlib.util.find_spec("paddle"),
                importlib.util.find_spec("tensorflow"),
                not importlib.util.find_spec("onnxruntime")]):
            raise exception.UnverifiedRuntimeException()

    @staticmethod
    def _check_algorithm_parameters_format(alg):
        try:
            alg_ps = alg['parameters'] if 'parameters' in alg else None
            if alg_ps is not None:
                for _, v in enumerate(alg_ps):
                    _ = v['key'] if 'key' in v else None
                    option = v['option'] if 'option' in v else None
                    if option is None:
                        return False
            return True
        except:
            return False

    def _prepare(self, path):
        sys.path.append(path)
        py_file = os.path.join(path, Const.algorithm_py)
        spec = importlib.util.spec_from_file_location(Const.algorithm, py_file)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        return self.module

    @staticmethod
    def load_config(yaml_file):
        cfg = load_config(yaml_file)
        return cfg

    @staticmethod
    def debug_mode():
        if os.environ.get('INTELLIW_HOLD_DEBUG') == "1":
            logger.warn("Intelliw will hold for one hour for debugging, please clear the container after use")
            time.sleep(3600)
            return True
        return False

    @staticmethod
    def initialize_env(envs):
        if envs and "parameters" in envs:
            ps: dict = envs.get("parameters", {})
            for k, v in ps.items():
                os.environ[str(k)] = str(v)

    def _initialize_algorithm(self, algorithm_yaml_file):
        cfg = self.load_config(algorithm_yaml_file)
        gl.alg_yaml_file = algorithm_yaml_file

        # 路由配置获取
        self.custom_router = cfg[Const.algorithmInformation].get(
            'router', [])

        # 算法配置获取
        alg_ps = cfg[Const.algorithmInformation][Const.algorithm].get(
            'parameters', None)
        return prepare_algorithm_parameters(alg_ps)

    def _initialize_model(self, model_yaml_file, parameters, option):
        model_cfg = self.load_config(model_yaml_file)
        self.model_cfg = model_cfg['Model']

        # 算法描述
        self.alg_describe = model_cfg['Model'].get('desc', '')

        # 算法元数据
        metadata = self.model_cfg.get(Const.metadata, {})

        # 算法类型 string（分类回归时间序列, classify|regression）
        self.predict_type = metadata.get(Const.predict_type)
        # 算法类型 int（分类回归时间序列。。。）
        self.model_type = metadata.get(Const.model_type)
        if self.model_type is not None:
            gl.model_type = self.model_type
        gl.model_yaml_file = model_yaml_file

        model_ps = self.model_cfg.get(Const.parameters)

        # model and algorithm's parameters are all in this var 'parameters'
        parameters = prepare_model_parameters(
            model_ps, parameters, option)

        # 从环境变量中加载PARAMETERS
        env_model_ps = os.environ.get(Const.parametersUp)
        if env_model_ps:
            env_model_ps = json.loads(env_model_ps)
            parameters = prepare_model_parameters(
                env_model_ps, parameters, option)

        # 获取系统级环境变量
        sys_envs = self.model_cfg.get(Const.system)
        self.initialize_env(sys_envs)

        if self.debug_mode():
            exit(0)

        # 特征处理可能会修改target_col，所以需要先保存起来, 有target_name时一定会有target_col
        target_metadata_cfg = metadata.get(Const.target, [])
        target_metadata = None
        if len(target_metadata_cfg) > 0:
            target_metadata = [{"target_col": int(m[Const.target_col]), "target_name": m.get(
                Const.target_code, m[Const.target_name])} for m in target_metadata_cfg]
        else:
            # TODO 暂时兼容 后面删了
            target_col = parameters.get(Const.target_col)
            target_name = parameters.get(Const.target_name)
            if target_col is not None or target_name is not None:
                target_col = int(
                    target_col) if target_col is not None else None
                target_metadata = [
                    {"target_col": target_col, "target_name": target_name}]

        gl.target_metadata = target_metadata

        # link server
        linkserver.config = self.model_cfg.get(Const.link_server, None)

        # self config
        gl.self_config = self.model_cfg.get(Const.delivery, None)

        return parameters, option

    def initialize_config(self, alg_file, model_file=None):
        # algorithm.yaml
        parameters, option = self._initialize_algorithm(alg_file)

        # model.yaml
        if model_file is not None:
            parameters, option = self._initialize_model(
                model_file, parameters, option)
        return parameters, option

    def _initialize(self, path, alg_file, model_file=None):
        try:
            # 初始化配置
            parameters, option = self.initialize_config(alg_file, model_file)

            # 校验
            if self._prepare(path) is None:
                self.raise_exception(
                    message.err_import_alg_invalid_algorithpy_format)
            is_valid, msg = is_valid_algorithm(self.module)
            if not is_valid:
                self.raise_exception(msg)

            # parameters
            # 日志
            parameters["framework_log"] = _get_algorithm_logger()
            if self.predict_type:
                parameters[Const.predict_type] = self.predict_type

            instance = self.module.Algorithm(parameters)
            if instance is None:
                self.raise_exception(message.err_import_alg_invalid_path)

            # 检测自定义路由方法是否存在
            for router in self.custom_router:
                func = router.get('func')
                if not hasattr(instance, func):
                    self.raise_exception(message.err_missing_router_func)

            # add decorator to functions
            if config.is_server_mode():
                make_decorators_server(instance, self.recorder)

            # FRAMEWORK_MODE
            instance.is_train_mode = config.FRAMEWORK_MODE == config.FrameworkMode.Train
            instance.is_infer_mode = config.FRAMEWORK_MODE == config.FrameworkMode.Infer

            return instance
        except Exception as e:
            self.raise_exception(message.err_import_alg_invalid_path, e)

    def _importalg_phase(self, path):
        hijack_function.HijackRequests()
        # 镜像校验
        if config.CHECK_CERTIFIED_IMAGE:
            hijack_function.HijackModelLoad()

        if not os.path.isfile(os.path.join(path, Const.algorithm_py)):
            self.raise_exception(message.err_import_alg_missing_algorithpy)
        if not os.path.isfile(os.path.join(path, Const.algorithm_yaml)):
            self.raise_exception(message.err_import_alg_missing_algorithyaml)
        cfg = self.load_config(os.path.join(path, Const.algorithm_yaml))
        self.algorithm_cfg = cfg  # SELF-DEFINE DICT
        if not self._check_algorithm_parameters_format(cfg):
            self.raise_exception(
                message.err_import_alg_invalid_algorithyaml_format)

    def _load_mode(self, path, model_path):
        model_file = model_path if os.path.isabs(model_path) else \
            os.path.join(path, model_path.lstrip("./"))
        logger.info(f"model load path：{model_file}")
        self.instance.load(model_file)

    def importalg(self, path, need_initialize=True):
        """
        导入算法
        :param path: 算法包所在路径
        :return: None
        :raises PipelineException: 框架导入算法失败原因
        """
        try:
            self._importalg_phase(path)
            if need_initialize:
                self._initialize(os.path.join(path, Const.algorithm_yaml))
        except Exception as e:
            self.raise_exception(message.err_import_algorithm, e)
        self.recorder.report(message.ok_import_algorithm)

    def importmodel(self, path, need_initialize=True, load_model=True):
        """
        导入模型
        :param path: 算法包所在路径
        :param load_model: 是否要导入模型，即是否调用 Algorithm 的 load 方法
        :return: None
        :raises PipelineException: 框架导入模型失败原因
        """
        model_yaml_path = os.path.join(path, Const.model_yaml)
        algorithm_yaml_path = os.path.join(path, Const.algorithm_yaml)
        # check model yaml file
        if not os.path.isfile(model_yaml_path):
            logger.error(
                "未找到 model.yaml, path: {}, file_name: {}".format(path, Const.model_yaml))
            self.raise_exception(message.err_import_model_missing_modelyaml)

        try:
            # check algorithm package
            self._importalg_phase(path)
            if need_initialize:
                self.instance = self._initialize(
                    path, algorithm_yaml_path, model_yaml_path)

                # get transforms
                trans_cfg = self.model_cfg.get('transforms', None)
                transforms_result = self.prepare_transforms(trans_cfg)
                self.splitdata_transforms = transforms_result[0]
                self.alldata_transforms = transforms_result[1]
                self.feature_transforms = transforms_result[2]
                gl.set_dict({
                    'feature_process': self.feature_transforms,
                    'timeseries_process': transforms_result[3]
                })

                # load model
                if load_model:
                    try:
                        model_path: str = self.model_cfg['location']
                        self._load_mode(path, model_path)
                    except Exception as e:
                        raise ModelLoadException(e)

                del self.model_cfg
        except Exception as e:
            self.raise_exception(message.err_import_model, e)

        # report
        self.recorder.report(message.ok_import_model)

    def _vaild_transforms_cfg(self, stage, is_split):
        transforms = self.splitdata_transforms if is_split else self.alldata_transforms
        if transforms is not None:
            transforms = transforms.get(stage)
            if transforms:
                return transforms
        return None

    def _transform_helper(self, stage, data, is_split):
        transforms = self._vaild_transforms_cfg(stage, is_split)
        if transforms is not None:
            return self.transform_call_chains(transforms, data)
        return data

    def _transform_function(self, stage, is_split):
        if self._vaild_transforms_cfg(stage, is_split) is None:
            return None

        def _transform(data):
            return self._transform_helper(stage, data, is_split)

        return _transform

    def _valid_feature_transforms(self, stage):
        if self.feature_transforms is not None:
            params = self.feature_transforms.get(stage)
            if params:
                return params
        return None

    def _feature_helper(self, stage, data):
        params = self._valid_feature_transforms(stage)
        if params is not None:
            from intelliw.functions.feature_process import feature_process
            return feature_process(data, params, stage)
        return data

    def _feature_process(self, stage):
        if self._valid_feature_transforms(stage) is None:
            return None

        def _process(data):
            return self._feature_helper(stage, data)

        return _process

    def _get_train_kwargs(self, reader, column_meta):
        if reader is None:
            return {}

        # config
        feature_process_cfg = gl.pop("feature_process")
        if feature_process_cfg is not None:
            feature_process_cfg = {
                Const.pre_train: feature_process_cfg.get(Const.pre_train),
                Const.post_train: feature_process_cfg.get(Const.post_train)
            }

        final_target_col = gl.pop("final_target_col")
        target_cols = gl.pop("target_cols")
        target_metadata = gl.pop("target_metadata")
        if target_cols is None and target_metadata is not None and len(target_metadata) > 0:
            target_cols = [
                {
                    "col": m["target_col"],
                    "column_name": m["target_name"]
                } for m in target_metadata
            ]
            final_target_col = target_cols[-1]["col"]

        kwargs = {
            "final_target_col": final_target_col,
            "target_cols": target_cols,
            "category_cols": gl.pop("category_cols"),
            "column_meta": gl.pop("column_meta") if gl.column_meta is not None else [i["code"] for i in
                                                                                     column_meta],
            "column_relation_df": gl.pop("column_relation_df"),
            "feature_process_cfg": feature_process_cfg,
        }

        # self config
        if gl.self_config:
            kwargs = {**kwargs, **{i['key']: i['val'] for i in gl.self_config}}

        return kwargs

    def train(self, datasets: Union[DataSets, MultipleDataSets]):
        """
        训练入口
        """
        if datasets is None:
            self.raise_exception(message.err_empty_train_data)

        # 特征值处理
        try:
            if config.SOURCE_TYPE == 0:
                train_set, valid_set, test_set = [], [], []
            else:
                train_set, valid_set, test_set = datasets.data_pipeline(
                    self._transform_function(Const.pre_train, True),
                    self._transform_function(Const.pre_train, False),
                    self._feature_process(Const.pre_train)
                )
        except Exception as e:
            self.raise_exception(message.err_function_process, e)

        # 开始训练
        try:
            logger.info("data process success, start train mode")

            # 数据集
            self.instance.train_set = train_set
            self.instance.valid_set = valid_set
            self.instance.test_set = test_set

            # 训练参数
            train_func = getattr(self.instance, "train")
            varnames = signature(train_func).parameters
            if "kwargs" not in varnames:
                # train(train, valid)
                train_func(
                    self.instance.train_set,
                    self.instance.valid_set
                )
            else:
                kwargs = self._get_train_kwargs(
                    train_set,
                    datasets.column_meta
                )
                if len(varnames) == 1:
                    # train(**kwargs)
                    train_func(**kwargs)
                elif len(varnames) == 3:
                    # train(train_set, valid_set, **kwargs)
                    train_func(
                        self.instance.train_set,
                        self.instance.valid_set,
                        **kwargs
                    )
                else:
                    self.raise_exception(message.err_missing_train_parameter)
            self.recorder.report(message.ok_train_finish)
        except exception.DatasetException as de:
            self.raise_exception(
                message.err_dataset, de, is_framework_error=False
            )
        except Exception as e:
            self.raise_exception(
                message.err_train, e, is_framework_error=False
            )

    async def _infer_process(self, data, request, func='infer', need_feature=False):
        work_queue_size = self.async_executor._work_queue.qsize()
        if func == 'intelliw-worker':
            return {
                "num_threads": len(self.async_executor._threads),
                "num_process": config.INFER_MULTI_PROCESS_COUNT,
                "cur_process": os.getpid(),
                "working_task": work_queue_size,
                "max_wait_task/process": self.max_wait_task,
                "total_wait_task": self.max_wait_task * config.INFER_MULTI_PROCESS_COUNT
            }

        if work_queue_size >= self.max_wait_task:
            error_msg = (f"Exceeded concurrency limit, "
                         f"Max wait task limit: {self.max_wait_task * config.INFER_MULTI_PROCESS_COUNT}")
            logger.warning(error_msg)
            raise LimitConcurrencyError(error_msg)

        loop = asyncio.get_event_loop()

        if need_feature:  # 前处理
            data = await loop.run_in_executor(
                self.async_executor, self._feature_helper, Const.pre_predict,
                self._transform_helper(Const.pre_predict, data, False)
            )

        # profile
        check_profile = request.query.get('intelliw_profile')
        check_mprofile = request.query.get('intelliw_mprofile')

        # 推理
        infer_func = getattr(self.instance, func)
        arg = [data] if infer_func.__code__.co_argcount > 1 else []  # 获取函数参数数量

        if not inspect.iscoroutinefunction(infer_func):

            cur_header_ctx = header_ctx.get()

            def infer_process(*a):
                self.instance.request = CurrentReq(request)
                header_ctx.set(cur_header_ctx)

                # 数据池
                if self.thread_data_pool:
                    t = threading.currentThread().ident
                    self.instance.request.datapool = self.thread_data_pool.get(t)

                if check_profile:  # 性能检测
                    return iprofile.performance_profile(infer_func, *a)
                elif check_mprofile:  # 内存检测
                    try:
                        from intelliw.utils import memory_profiler
                    except ImportError as e:
                        return {"result": e}
                    memory_usage, res = memory_profiler.memory_usage(
                        (infer_func, a), retval=True,
                        include_children=True,
                        interval=.2, max_iterations=1)
                    return {"result": res, "profile": memory_usage}
                else:
                    return infer_func(*a)

            # 非异步算法异步执行
            result = await loop.run_in_executor(
                self.async_executor, infer_process, *arg
            )
        else:
            self.instance.request = CurrentReq(request)

            # 异步算法默认已经做了从头到尾的异步处理
            # 出现阻塞问题，是算法对async await理解不够透彻
            if check_profile:
                result = await iprofile.async_performance_profile(infer_func, *arg)
            else:
                result = await infer_func(*arg)

        if need_feature:  # 后处理
            result = await loop.run_in_executor(
                self.async_executor, self._transform_helper, Const.post_predict, result, False
            )

        return result

    async def infer(self, data, request, func='infer', need_feature=True):
        """
        推理入口
        """
        try:
            start = time.time()

            result = await self._infer_process(
                data, request, func, need_feature
            )

            rst = request.raw.state.req_start_time
            ist = request.raw.state.ingress_start_time
            ingress_duration = rst - float(ist) / 1000 if ist else 0
            req_duration = start - rst if rst else None

            logger.info(
                f'{request.method} {request.url.path if request.url else "TestCase"}   function: {func}   '
                f'time: \033[33m connect: {ingress_duration:.4f}s, request: {req_duration:.4f}s, '
                f'response: {time.time() - start:.4f}s\033[0m '
            )
            return result, None
        except LimitConcurrencyError as e:
            msg = f"inference error: {e}"
            return f"inference error: {e}", LimitConcurrencyError()
        except Exception as e:
            stack_info = traceback.format_exc()
            logger.error("推理错误 %s, stack:\n%s", e, stack_info)
            return None, f"inference error: {e}"

    def transform_call_wrapper(self, src, func, params):
        """
        数据处理调用
        """
        if type(func) is type:
            return func().__call__(src, params)
        return func(src, params)

    def transform_call_chains(self, funcs, src):
        """
        数据处理函数链
        data, config -> func1(data, config) -> data, config -> func2(data, config) -> ...
        """
        name = ""
        try:
            for _, item in enumerate(funcs):
                (name, func, params) = item
                if id(func) == id(functions.select_columns) and \
                        self._not_select_columns():
                    continue
                src = self.transform_call_wrapper(src, func, params)
            return src
        except Exception as e:
            msg = message.CommonResponse(
                500, "transforms", f"特征工程函数 {name} 出错")
            self.raise_exception(msg, e)

    def _not_select_columns(self):
        """
        如果有特征工程前处理，就需要忽略select_columns
        """
        if gl.feature_process and gl.feature_process.get(Const.pre_train):
            return True
        return False

    def _get_func_by_name(self, name):
        """
        根据 name 加载函数

        加载顺序:
        1. 尝试在算法项目中加载
        2. 尝试在内置的特征处理中查找
        3. 尝试在当前 module 中加载

        :param name: 待加载的函数名称
        :return: 函数
        :raise: RuntimeError 加载失败原因
        """
        # 尝试在算法项目中加载
        mod = self.module
        if hasattr(mod, name):
            return getattr(mod, name)

        # 尝试在内置的特征处理中查找
        if hasattr(functions, name):
            return getattr(functions, name)

        # 尝试在当前 module 中加载
        mod = sys.modules[__name__]
        if hasattr(mod, name):
            return getattr(mod, name)

        raise RuntimeError(f'函数无效: [{name}]')

    @staticmethod
    def _prepare_timeseries_transforms(timeseries_features, typ, params):
        # normal
        normal = json.loads(params.get(
            functions.Const.timeseries_param, 'null')
        )
        if normal and normal.get("holiday", "none") == "none":
            normal["holiday"] = None
        timeseries_features[typ]["normal"] = normal

        # group
        group_params = json.loads(params.get(
            functions.Const.timeseries_group_param, '[]')
        )
        for idx, i in enumerate(group_params):
            k = f"industry_{idx}" if idx > 0 else "group"
            timeseries_features[typ][k] = i
        return timeseries_features

    def prepare_transforms(self, cfgs):
        """
        解析配置文件中的特征工程
        """

        def init_dict(item):
            return {} if item is None else item

        def init_list(item):
            return [] if item is None else item

        # 没用到就不初始化，减少后面的判断
        split_transforms, alldate_transforms = None, None
        data_features, timeseries_features = None, None
        if not cfgs:
            return split_transforms, alldate_transforms, data_features, timeseries_features

        for cfg in cfgs:
            typ, functions_cfg = cfg.get('type'), cfg.get('functions')
            if typ is not None and functions_cfg is not None:
                for item in functions_cfg:
                    key = item.get('key')
                    params, _ = prepare_algorithm_parameters(
                        item.get('parameters')
                    )
                    if key == functions.Const.feature_process:
                        # 特征工程
                        # 如果是离职预测，所有的特征auto配置必须为0，只做列数据筛选
                        data_features = init_dict(data_features)
                        data_features[typ] = json.loads(params.get(
                            functions.Const.feature_process_param, 'null')
                        )
                    elif key == functions.Const.timeseries_process:
                        # 时间序列
                        timeseries_features = init_dict(
                            timeseries_features)
                        timeseries_features[typ] = dict()
                        timeseries_features = self._prepare_timeseries_transforms(
                            timeseries_features, typ, params
                        )
                    else:
                        # 常规数据处理
                        body = item.get('body')
                        func = self._get_func_by_name(
                            key) if body is None else get_first_element(import_code(body, None))
                        if func is not None:
                            can_split = key in functions.Const.split_function_list or item.get(
                                'canSplit')

                            _t = {}
                            if can_split:
                                split_transforms = init_dict(
                                    split_transforms)
                                _t = split_transforms
                            else:
                                alldate_transforms = init_dict(
                                    alldate_transforms)
                                _t = alldate_transforms

                            _t[typ] = init_list(_t.get(typ))
                            _t[typ].append((key, func, params))
                            logger.info(
                                "特征函数 %s, 是否可以进行分片处理 %s", key, can_split)
                        else:
                            logger.info("找不到函数 %s", key)
        return split_transforms, alldate_transforms, data_features, timeseries_features

    def validate_transforms(self, cfgs, data):
        """
        验证特征工程函数， 用于用户校验函数正确性和结果，服务于validateService
        """
        transforms = []
        if not cfgs:
            return self.transform_call_chains(transforms, data)

        for cfg in cfgs:
            transforms = self._set_transform(cfg, transforms)

        return self.transform_call_chains(transforms, data)

    def _set_transform(self, cfg, transforms):
        inner_functions = cfg.get('functions', None)
        if not inner_functions:
            return transforms

        for item in inner_functions:
            desc = item['desc'] if 'desc' in item else None
            key = item['key'] if 'key' in item else None
            body = item['body'] if 'body' in item else None
            parameters = item['parameters'] if 'parameters' in item else None
            if body is not None:
                n_mod = import_code(body, None)
                func = get_first_element(n_mod)
            else:
                func = self._get_func_by_name(key)
            params, _ = prepare_algorithm_parameters(parameters)
            if func is not None:
                logger.info("特征函数 %s", key)
                transforms.append((key, func, params))
            else:
                logger.info("找不到函数 %s", key)
        return transforms

    def raise_exception(self, msg: message.CommonResponse,
                        error: Exception = None, is_framework_error=True):
        raise_logger = logger if is_framework_error else \
            _get_algorithm_logger()

        # 用于传递错误给prepare_env.sh
        err_stack = "\n"
        if hasattr(error, "ignore_stack") or isinstance(error, ImportError):
            logger.error(traceback.format_exc())
            err_stack += f"错误描述: {error}"  # 数据集错误不需要调用栈，知道什么问题就行
        elif error:
            err_stack += f"错误描述: {error} \n错误详情: {traceback.format_exc()}"
        else:
            err_stack = ""
        err_content = f"\n错误内容: {msg.msg}{err_stack}"
        os.environ["ERR_MASSAGE"] = err_content

        if error is not None:
            msg.msg = err_content
        raise_logger.error(msg.msg)

        if hasattr(error, "btype"):
            msg.other['businessType'] = error.btype()

        # 上报
        self.recorder.report(msg)
        sys.exit()
