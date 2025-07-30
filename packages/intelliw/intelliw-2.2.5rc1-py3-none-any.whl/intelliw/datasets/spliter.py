'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-25 15:24:05
LastEditors: Hexu
Description: 数据集切分工具
FilePath: /iw-algo-fx/intelliw/datasets/spliter.py
'''
from abc import ABCMeta, abstractmethod
import math
from random import Random
from typing import Iterable
from intelliw.utils.exception import DatasetException
from intelliw.config import config
from intelliw.utils.global_val import gl
from intelliw.utils.logger import _get_framework_logger
from intelliw.datasets.datasource_base import DataSourceType


class SpliterClass:
    nothing = -1
    sequential = 0
    random = 1
    random_by_target = 2


def get_set_spliter(data, source_type, not_spliter=False):
    logger = _get_framework_logger()
    trr = config.TRAIN_DATASET_RATIO
    var = config.VALID_DATASET_RATIO
    ter = config.TEST_DATASET_RATIO
    msg = "\033[33mDataset Split Reader: %s\033[0m"

    if trr == 1 and (var + ter) == 0:
        not_spliter = True
    logger.info("SplitRatio: trr:%f,var:%f,ter:%f", trr, var, ter)
    if not data or not_spliter or \
            config.DATA_SPLIT_MODE == SpliterClass.nothing:
        logger.info(msg, "no Spliter")
        return NoSpliter(data, trr, var, ter, source_type)
    elif config.DATA_SPLIT_MODE == SpliterClass.random:
        target_col, err = target_verify()
        if err is None:  # 分类算法根据目标列特殊处理
            logger.info(msg, "Random Spliter by Target")
            return TargetRandomSpliter(data, trr, var, ter, target_col, source_type)
        else:
            logger.info(msg, "Random Spliter")
            return ShuffleSpliter(data, trr, var, ter, source_type)
    elif config.DATA_SPLIT_MODE == SpliterClass.random_by_target:
        target_col, err = target_verify()
        if err is not None:
            raise DatasetException(err)
        logger.info(msg, "Random Spliter by Target")
        return TargetRandomSpliter(data, trr, var, ter, target_col, source_type)
    else:  # 不指定都用顺序
        logger.info(msg, "Sequential Spliter")
        return SequentialSpliter(data, trr, var, ter, source_type)


def target_verify():
    target_col, err = None, None

    # 图像分类
    if gl.model_type == 12:
        return "labels", err

    # 表格分类
    if not gl.model_type == 3:
        err = "只有分类算法才能使用该规则"
        return target_col, err

    target_metadata = gl.target_metadata
    if target_metadata is None or len(target_metadata) == 0:
        err = "配置文件(algorithm.yaml)中未设置target相关数据"
        return target_col, err

    if len(target_metadata) > 1:
        err = "目前只支持针对单目标列的数据shuffle处理"
        return target_col, err

    # 先从特征工程后的target中获取
    # 无特征工程修改后的目标列， 再从源数据中获取
    target_cols = gl.get("target_cols", [])
    if len(target_cols) > 0:
        target_col = target_cols[0]["col"]
    else:
        target_col = target_metadata[0]["target_col"]
    if type(target_col) != int:
        err = f"目标列下标类型错误:targetCol类型应为int, 当前数据: {target_col}-{type(target_col)}"
        return target_col, err

    return target_col, err


def check_split_ratio(train_ratio, valid_ratio, test_ratio):
    assert 0 < train_ratio <= 1, f"数据集比例不正确, 训练集比例{train_ratio}"
    assert 0 <= valid_ratio < 1, f"数据集比例不正确, 验证集比例{valid_ratio}"
    assert 0 <= test_ratio < 1, f"数据集比例不正确, 测试集比例{test_ratio}"
    assert train_ratio + valid_ratio + test_ratio < 1.09, "数据集比例不正确, 总和不为1"


def get_set_count(length, train_ratio, valid_ratio, test_ratio):
    train_num = math.floor(length * float(train_ratio))
    if test_ratio == 0:
        valid_num = length - train_num
        test_num = 0
    else:
        valid_num = math.floor(length * float(valid_ratio))
        test_num = max(length - train_num - valid_num, 0)
    return train_num, valid_num, test_num


class DataSetSpliter(metaclass=ABCMeta):
    def __init__(self, data, train_ratio, valid_ratio, test_ratio, source_type, seed = config.DATA_RANDOM_SEED):
        if not isinstance(data, (dict, list)):
            raise TypeError("data_source has a wrong type, required: list, actually: {}".format(
                type(data).__name__))

        check_split_ratio(train_ratio, valid_ratio, test_ratio)
        self.source_type = source_type
        if not data:
            self.alldata = []
        elif self.source_type in DataSourceType.CV_TYPE_LIST:
            # 图片数据源
            self.alldata = data
        else:
            self.alldata = data.pop("result")
            self.column_meta = data.pop("meta")
        self.data_num = len(self.alldata)
        self.train_num, self.valid_num, self.test_num = get_set_count(
            self.data_num, train_ratio, valid_ratio, test_ratio
        )
        self.train_data = None
        self.valid_data = None
        self.test_data = None

        self.seed = seed  # 使用固定 seed 保证同一个数据集多次读取划分一致

    def train_reader(self) -> Iterable:
        if self.train_num == 0:
            return []
        return self._train_reader()

    @abstractmethod
    def _train_reader(self) -> Iterable:
        pass

    def validation_reader(self) -> Iterable:
        if self.valid_num == 0:
            return []
        return self._validation_reader()

    @abstractmethod
    def _validation_reader(self) -> Iterable:
        pass

    def test_reader(self) -> Iterable:
        if self.test_num == 0:
            return []
        return self._test_reader()

    @abstractmethod
    def _test_reader(self) -> Iterable:
        pass


class NoSpliter(DataSetSpliter):
    """
    不进行数据切分
    """
    def __init__(self, data, train_ratio, valid_ratio, test_ratio, source_type):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio, source_type)

    def _train_reader(self):
        return {"meta": self.column_meta, "result": self.alldata}

    def _validation_reader(self):
        return None

    def _test_reader(self):
        return None


class SequentialSpliter(DataSetSpliter):
    """顺序读取数据
    数据按照训练集比例分割，前面为训练集，后面为验证集
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio, source_type):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio, source_type)

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        # 获取所有数据
        train_data = self.alldata[:self.train_num]
        if self.test_num == 0:
            valid_data = self.alldata[self.train_num:]
            test_data = []
        else:
            valid_data = self.alldata[self.train_num:
                                      self.train_num + self.valid_num]
            test_data = self.alldata[self.train_num + self.valid_num:]

        if self.source_type in DataSourceType.CV_TYPE_LIST:
            self.train_data = train_data
            self.valid_data = valid_data
            self.test_data = test_data
        else:
            self.train_data = {"meta": self.column_meta, "result": train_data}
            self.valid_data = {"meta": self.column_meta, "result": valid_data}
            self.test_data = {"meta": self.column_meta, "result": test_data}


# ShuffleSpliter 乱序读取
class ShuffleSpliter(DataSetSpliter):
    """乱序读取

    注意:
    此方法需要读取全部数据，会给内存带来压力
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio, source_type):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio, source_type)

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        # 获取所有数据
        r = Random(self.seed)
        r.shuffle(self.alldata)
        train_data = self.alldata[:self.train_num]
        if self.test_num == 0:
            valid_data = self.alldata[self.train_num:]
            test_data = []
        else:
            valid_data = self.alldata[self.train_num:
                                      self.train_num + self.valid_num]
            test_data = self.alldata[self.train_num + self.valid_num:]

        if self.source_type in DataSourceType.CV_TYPE_LIST:
            self.train_data = train_data
            self.valid_data = valid_data
            self.test_data = test_data
        else:
            self.train_data = {"meta": self.column_meta, "result": train_data}
            self.valid_data = {"meta": self.column_meta, "result": valid_data}
            self.test_data = {"meta": self.column_meta, "result": test_data}


class TargetRandomSpliter(DataSetSpliter):
    """根据目标列乱序读取
    按照目标列中类别的比例，进行训练集和验证集的划分，保证训练集和验证集中类别比例与整体数据比例相同

    使用此方法的前提：
     - 有目标列
     - 是分类

    几种可能存在的边界：
     - 分类太多: 1w数据分出来5k类别, 算法框架在tag_count/total > 0.5的时候会warn
     - 类别唯一: 只有一个tag
     - 某类别唯一: 某个tag只有一
     - 无目标列下标: 需要配置targetCol
     - 训练集或验证集比例为1

    注意:
    此方法需要读取全部数据，会给内存带来压力
    """

    def __init__(self, data, train_ratio, valid_ratio, test_ratio, target_col, source_type):
        super().__init__(data, train_ratio,
                         valid_ratio, test_ratio, source_type)

        self.train_ratio = train_ratio
        self.valid_ratio = valid_ratio
        self.test_ratio = test_ratio
        self.target_col = self._target_col(target_col)

    def _target_col(self, target_col):
        if self.source_type in DataSourceType.CV_TYPE_LIST:
            return 'labels'
        return target_col

    def _train_reader(self):
        if self.train_data is None:
            self._set_data()
        return self.train_data

    def _validation_reader(self):
        if self.valid_data is None:
            self._set_data()
        return self.valid_data

    def _test_reader(self):
        if self.test_data is None:
            self._set_data()
        return self.test_data

    def _set_data(self):
        from intelliw.utils.spark_process import Engine
        engine = Engine()

        df = engine.DataFrame(self.alldata)
        if self.source_type in DataSourceType.CV_TYPE_LIST:
            target_index = self.target_col
        else:
            target_index = df.columns[self.target_col]
            # 边界处理
            if df.shape[1] < self.target_col + 1:
                raise DatasetException(
                    f"数据集不存在目标列, 数据集列数{df.shape[1]}, 目标列下标{self.target_col}")

        tags = df[target_index].unique().tolist()
        # 边界处理
        for tag in tags:
            if tag is None or engine.isna(tag):
                tags.remove(tag)
                # break

        tag_count = len(tags)
        if (tag_count < 2) or (tag_count / self.data_num > 1 / 3):
            raise DatasetException(
                f"目标列类别数量唯一, 或者类别数量超过总数据的30%, 类别数量: {tag_count}")

        train, valid, test = engine.DataFrame(), engine.DataFrame(), engine.DataFrame()
        for tag in tags:
            tag_data = df[df[target_index] == tag]

            line_count = tag_data.shape[0]
            train_num, valid_num, test_num = get_set_count(
                line_count, self.train_ratio, self.valid_ratio, self.test_ratio
            )

            # 边界处理
            if (test_num == 0 and line_count < 2) or (test_num != 0 and line_count < 3):
                raise DatasetException(
                    f"目标列类别: {tag} 存在过少的数据({line_count}条), 无法均匀分配到数据集中")

            # train
            tag_data = tag_data.sample(frac=float(1), random_state=self.seed)
            train_data = tag_data[:train_num]
            if test_num == 0:
                valid_data = tag_data[train_num:]
            else:
                valid_data = tag_data[train_num: train_num + valid_num]
                test_data = tag_data[train_num + valid_num:]
                test = engine.concat([test, test_data], ignore_index=True)
            valid = engine.concat([valid, valid_data], ignore_index=True)
            train = engine.concat([train, train_data], ignore_index=True)

        if self.source_type in DataSourceType.CV_TYPE_LIST:
            self.train_data = train.to_dict(orient='records')
            self.valid_data = valid.to_dict(orient='records')
            self.test_data = test.to_dict(orient='records')
        else:
            self.train_data = {"meta": self.column_meta,
                               "result": train.values.tolist()}
            self.valid_data = {"meta": self.column_meta,
                               "result": valid.values.tolist()}
            self.test_data = {"meta": self.column_meta,
                              "result": test.values.tolist()}
