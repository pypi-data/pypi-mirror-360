'''
Author: Hexu
Date: 2022-11-22 09:48:10
LastEditors: Hexu
LastEditTime: 2023-02-22 13:37:41
FilePath: /iw-algo-fx/intelliw/core/trainer.py
Description: Train core
'''
# coding: utf-8
from intelliw.config import config
from intelliw.datasets.datasets import DataSets, MultipleDataSets
from intelliw.core.pipeline import Pipeline


class Trainer:
    def __init__(self, path, reporter=None):
        self.pipeline = Pipeline(reporter)
        self.pipeline.importmodel(path, True, config.CHECKPOINT_MODE)

    def train(self, datasets: (DataSets, MultipleDataSets)):
        if not isinstance(datasets, DataSets) and not isinstance(datasets, MultipleDataSets):
            raise TypeError("datasets has a wrong type, required: DataSets, MultipleDataSets, actually: {}"
                            .format(type(datasets).__name__))

        return self.pipeline.train(datasets)
