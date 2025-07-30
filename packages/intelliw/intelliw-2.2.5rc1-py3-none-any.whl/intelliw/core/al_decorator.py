#!/usr/bin/env python
# coding: utf-8

import inspect
import json
import time
import errno
import shutil
import os
import cProfile
import zipfile
import traceback
from functools import wraps
from intelliw.utils import message
from intelliw.utils.exception import CheckpointException
from intelliw.utils.storage_service import FileTransferDevice
from intelliw.utils.logger import _get_framework_logger, Logger
from intelliw.config import config
from intelliw.utils import generate_random_str, get_json_encoder

logger = _get_framework_logger()

save_index = 0
curkey_r = generate_random_str(32)


def zipdir(model_path):
    outpath = '/tmp/model.zip'
    with zipfile.ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.isdir(model_path):
            for root, _, files in os.walk(model_path):
                relative_path = root.replace(model_path, "")
                for file in files:
                    logger.info("压缩文件 {}".format(os.path.join(root, file)))
                    zipf.write(os.path.join(root, file),
                               os.path.join(relative_path, file))
        elif os.path.isfile(model_path):
            zipf.write(model_path, os.path.basename(model_path))
    return outpath


def decorator_report_train_info(function, reporter=None):
    from intelliw.utils import get_json_encoder

    @wraps(function)
    def wrapper(loss, lr, iter, batchsize, **kwargs):
        if reporter is not None:
            info = json.dumps({
                "loss": loss,
                "lr": lr,
                "iter": iter,
                "batchsize": batchsize,
                "timestamp": int(time.time() * 1000),
                "other": kwargs
            }, cls=get_json_encoder())
            reporter.report(message.CommonResponse(
                200, 'report_train_info', '', str(info)))
        return function(loss, lr, iter, batchsize, **kwargs)
    return wrapper


def decorator_report_val_info(function, reporter=None):
    from intelliw.utils import get_json_encoder

    @wraps(function)
    def wrapper(*args, **kwargs):
        if reporter is not None:
            val = {}

            # process args
            varnames = function.__code__.co_varnames
            offset = 0
            for i in range(len(varnames)):
                if varnames[i] == 'self' or varnames[i] == 'args' or varnames[i] == 'kwargs':
                    offset = offset - 1
                    continue
                if i + offset < len(args):
                    val[varnames[i]] = args[i + offset]
                else:
                    val[varnames[i]] = None

            # process kwargs
            for k, v in kwargs.items():
                val[k] = v

            data = {
                "modelInstanceId": config.INSTANCE_ID,
                "tenantId": config.TENANT_ID,
                "valuationResult": val
            }
            reporter.report(message.CommonResponse(200, 'report_val_info', '', json.dumps(
                data, cls=get_json_encoder(), ensure_ascii=False)))
        return function(*args, **kwargs)
    return wrapper


# decorator_save 存储模型文件到云存储
def decorator_save(function, reporter=None):

    @wraps(function)
    def wrapper(*args, **kwargs):
        # 分布式训练 slave不需要保存模型
        if config.FRAMEWORK_MODE == config.FrameworkMode.DistTrain and \
                not config.DIST_IS_MASTER:
            logger.info("分布式训练slave服务不需要保存模型文件")
            return None

        # 如果用户输入的是绝对路径，就使用输入的路径
        user_path = args[0]
        if os.path.isabs(user_path):
            model_path = user_path
        else:
            hpath = os.path.join('/tmp', generate_random_str(16))
            os.makedirs(hpath)
            model_path = os.path.join(hpath, user_path)

        # 创建模型保存文件夹
        if not os.path.exists(model_path):
            logger.info("目录不存在， 自动创建 {}".format(model_path))
            try:
                os.makedirs(model_path)
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isdir(model_path):
                    pass
                else:
                    logger.error("保存模型错误:  创建目录失败")
                    reporter.report(str(message.CommonResponse(500, "train_save",
                                                               "保存模型错误:  创建目录失败 {}".format(model_path))))

        # 设置save_index
        global save_index
        is_checkpoint = False
        if function.__name__ == 'save_checkpoint':
            is_checkpoint = True
            if kwargs.get("save_best_only") is True:
                save_index = "best"
            elif "max_to_keep" in kwargs:
                # save_index类型为str类型，说明之前执行过save()方法或执行过save_checkpoint()方法save_best_only为true的情况，不符合逻辑
                if isinstance(save_index, str):
                    raise CheckpointException()
                max_to_keep = kwargs.get("max_to_keep")
                if max_to_keep < 0:
                    save_index = (save_index + 1) % config.CHECKPOINT_SAVE_MAX
                elif max_to_keep > 0:
                    save_index = (
                        save_index + 1) % max_to_keep % config.CHECKPOINT_SAVE_MAX
        else:
            save_index = "model"
        # 执行用户的保存函数
        result = function(model_path)

        # 上传模型
        if reporter is not None:
            _, outpath = __push_model_to_cloud(
                reporter, model_path, save_index, is_checkpoint, kwargs)
            try:
                os.remove(outpath)
                shutil.rmtree(hpath, ignore_errors=True)
            except:
                pass
        else:
            logger.info("保存模型错误: reporter is  None")

        return result
    return wrapper


def __push_model_to_cloud(reporter, model_path, index, is_checkpoint, kwargs):
    from intelliw.utils.storage_service import StorageService

    try:
        out_path = zipdir(os.path.abspath(model_path))
        save_fn = config.INSTANCE_ID or curkey_r
        curkey = os.path.join(config.STORAGE_SERVICE_PATH, save_fn, str(index))
        uploader = StorageService(curkey, "upload")
        logger.info(
            f"模型上传地址{uploader.service_url}, checkpoint模式：{is_checkpoint}")
        try:
            uploader.upload(out_path)

            logger.info(
                f"上传模型文件成功：{curkey}, checkpoint模式：{is_checkpoint}")
            if is_checkpoint:
                data = {'modelPath': curkey, 'epoch': kwargs.get(
                    'epoch'), 'indice': str(kwargs.get('indice'))}
                request = json.dumps(
                    data, cls=get_json_encoder(), ensure_ascii=False)
                business_type = "save_checkpoint"
            else:
                request = [curkey]
                business_type = "save_model"

            reporter.report(message.CommonResponse(
                200, 'train_save', 'success', request, businessType=business_type))
        except Exception:
            err_info = traceback.format_exc()
            logger.info(
                f"上传模型文件失败: {err_info}, checkpoint模式：{is_checkpoint}")
            reporter.report(str(message.CommonResponse(
                500, "train_save", f"保存模型错误 {err_info}")))
    except Exception as e:
        stack_info = traceback.format_exc()
        reporter.report(str(message.CommonResponse(500, "train_save",
                                                   "保存模型错误 {}, stack: \n {}".format(e, stack_info))))
    return curkey, out_path


def flame_prof_process(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not config.FLAME_PROF_MODE:
            return function(*args, **kwargs)
        else:
            prof_file = "./request.prof"

            pr = cProfile.Profile()
            pr.enable()
            result = function(*args, **kwargs)
            pr.disable()
            pr.dump_stats(prof_file)
            FileTransferDevice(prof_file, "flame_prof")
            logger.info("\033[33mFlame Performance Complete: Save file to ./request.prof\033[0m")
            return result
    return wrapper


def make_decorators_server(instance, reporter=None):
    # report_train_info
    if (hasattr(instance, 'report_train_info')) and inspect.ismethod(instance.report_train_info):
        instance.report_train_info = decorator_report_train_info(
            instance.report_train_info, reporter)

    # report_val_info
    if (hasattr(instance, 'report_val_info')) and inspect.ismethod(instance.report_val_info):
        instance.report_val_info = decorator_report_val_info(
            instance.report_val_info, reporter)

    # save model
    if (hasattr(instance, 'save')) and inspect.ismethod(instance.save):
        instance.save = decorator_save(instance.save, reporter)

    # save model
    if (hasattr(instance, 'save_checkpoint')) and inspect.ismethod(instance.save_checkpoint):
        instance.save_checkpoint = decorator_save(
            instance.save_checkpoint, reporter)


def make_decorators_local(instance):
    if (hasattr(instance, 'get_user_logger')) and inspect.isfunction(instance.get_user_logger):
        instance.get_user_logger = Logger()._get_logger
