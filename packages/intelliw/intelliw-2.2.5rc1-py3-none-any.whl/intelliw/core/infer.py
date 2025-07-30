'''
Author: Hexu
Date: 2022-03-14 09:53:59
LastEditors: Hexu
LastEditTime: 2023-05-24 15:59:01
FilePath: /iw-algo-fx/intelliw/core/infer.py
Description: Infer core
'''
import os

# coding: utf-8
from intelliw.utils.intelliwapi import request
from intelliw.core.pipeline import Pipeline
from intelliw.utils.global_val import gl


class Infer:
    """
    infer entrypoint
    """
    def __init__(self, path, reporter_addr=None):
        self.pipeline = Pipeline(reporter_addr)
        self.pipeline.importmodel(path)

    def infer(self, data, request=request.Request(), func='infer', need_feature=True):
        """
        infer
        """
        return self.pipeline.infer(data, request, func, need_feature)

