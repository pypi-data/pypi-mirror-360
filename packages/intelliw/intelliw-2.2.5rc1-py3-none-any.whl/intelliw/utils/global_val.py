'''
Author: hexu
Date: 2021-10-18 10:44:06
LastEditTime: 2023-05-10 15:32:22
LastEditors: Hexu
Description: 用来存储项目中需要的全局环境变量， 减少代码的耦合
FilePath: /iw-algo-fx/intelliw/utils/global_val.py
'''
import threading


class GlobalVal:
    # 单例锁
    _instance_lock = threading.Lock()
    _recorder = None
    _monitor = None
    _global_dict = {}

    def __new__(cls):
        """ 单例，防止调用生成更多环境变量dict """
        if not hasattr(GlobalVal, "_instance"):
            with GlobalVal._instance_lock:
                if not hasattr(GlobalVal, "_instance"):
                    GlobalVal._instance = object.__new__(cls)
        return GlobalVal._instance

    @staticmethod
    def set(key, value):
        """ 定义一个全局变量 """
        GlobalVal._global_dict[key] = value

    @staticmethod
    def set_dict(_dict: dict):
        if type(_dict) != dict:
            raise TypeError(
                "GlobalVal.set_dict input must be a dict, error type: ", type(_dict))
        for k, v in _dict.items():
            GlobalVal._global_dict[k] = v

    @staticmethod
    def get(key, default=None):
        """ 获得一个全局变量,不存在则返回默认值 """
        return GlobalVal._global_dict.get(key, default)

    @staticmethod
    def pop(key, default=None):
        """ 获得一个全局变量,并从全局变量中删除,不存在则返回默认值 """
        return GlobalVal._global_dict.pop(key, default)

    @staticmethod
    def value_is(key, value):
        return GlobalVal._global_dict.get(key, None) == value

    @staticmethod
    def has(key):
        return key in GlobalVal._global_dict

    @staticmethod
    def clear():
        del GlobalVal._global_dict
        GlobalVal._global_dict = {}

    def __getattr__(self, key):
        if key == "recorder":
            return GlobalVal._recorder
        elif key == "monitor":
            return GlobalVal._monitor
        return GlobalVal._global_dict.get(key)

    def __setattr__(self, key, value):
        if key == "recorder":
            GlobalVal._recorder = value
        elif key == "monitor":
            GlobalVal._monitor = value
        else:
            GlobalVal._global_dict[key] = value


gl = GlobalVal()
