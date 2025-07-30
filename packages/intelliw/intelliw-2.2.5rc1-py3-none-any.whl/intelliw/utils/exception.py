'''
Author: Hexu
Date: 2022-03-30 11:47:31
LastEditors: Hexu
LastEditTime: 2023-04-06 14:31:34
FilePath: /iw-algo-fx/intelliw/utils/exception.py
Description: 错误类定义
'''
####### error class #######


import os


class LimitConcurrencyError(Exception):
    pass


class ExceptionNoStack(Exception):
    def ignore_stack(self):
        return True


class PipelineException(Exception):
    pass


class ModelLoadException(Exception):
    def __init__(self, msg) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return '''模型加载异常\n
报错信息: {}
可能原因:
1 内存分配过小, 模型加载时服务崩溃
2 模型文件是否存在,加载模型的路径是否正确
3 是否补全load函数,load函数是否存在问题
4 如果使用checkpoint,检查代码是否正确加载checkpoint
5 是否使用ONNX模型作为推理模型
'''.format(self.msg)


class UnverifiedRuntimeException(Exception):

    def __str__(self) -> str:
        return '''算法使用了未验证的运行环境：
    1. 请使用ONNX模型进行服务推理
    2. 请勿使用Torch， Paddle，TensorFlow等框架运行模型
        '''

    def ignore_stack(self):
        return True


class DatasetException(Exception):
    def ignore_stack(self):
        return True


class InferException(Exception):
    pass


class FeatureProcessException(Exception):
    def ignore_stack(self):
        return True


class DataSourceDownloadException(Exception):
    def ignore_stack(self):
        return True


class LinkServerException(Exception):
    pass


class HttpServerException(Exception):
    pass


class CheckpointException(Exception):
    def __str__(self) -> str:
        return '''checkpoint保存模型异常，发生错误的可能：
    1. save()方法在save_checkpoint()方法之前调用,请在训练结束后调用save()方法保存模型
    2. save_checkpoint()方法多次调用
        '''

    def ignore_stack(self):
        return True
