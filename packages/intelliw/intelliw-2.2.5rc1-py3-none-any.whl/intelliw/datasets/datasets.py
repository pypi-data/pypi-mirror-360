'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-25 15:26:26
LastEditors: Hexu
Description: 数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasets.py
'''
import json
from typing import List, Tuple,Union, overload
from intelliw.datasets.spliter import get_set_spliter
from intelliw.datasets.datasource_base import DatasetSelector, AbstractDataSource, AbstractDataSourceWriter, \
    DataSourceType as DST, DatasetType, AlgorithmsType
from intelliw.datasets.datasource_empty import EmptyDataSourceWriter
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config
from intelliw.utils.global_val import gl


logger = _get_framework_logger()


class DataSets:
    """
    DataSets
    dataset metadata
    """

    def __init__(self, datasource: AbstractDataSource, source_type: int):
        self.datasource = datasource
        self.alldata = []
        self.column_meta = []
        self.source_type = source_type
        self.model_type = gl.model_type  # 分类/回归/ocr/时间序列/文本分类。。。。。

    def empty_reader(self, dataset_type=DatasetType.TRAIN):
        """
        empty reader
        """
        return self.datasource.reader(page_size=1, offset=0, limit=0, transform_function=None,
                                      dataset_type=dataset_type)

    def reader(self, page_size=10000, offset=0, limit=0, split_transform_function=None):
        """
        reader
        """
        return self.datasource.reader(page_size, offset, limit, split_transform_function)

    @overload
    def data_pipeline(self, split_transform_function,
                      alldata_transform_function, feature_process):
        """
        pipeline: download -> filter -> spliter -> user
        """
        pass

    def data_pipeline(self, *args):
        """
        pipeline: download -> filter -> spliter -> user
        """
        if self.source_type in DST.NLP_TYPE_LIST:
            return self._nlp_data(config.DATA_SPLIT_MODE)
        if self.source_type in DST.LARGE_MODEL_LIST:
            return self._large_model_data(config.DATA_SPLIT_MODE)
        elif self.source_type in DST.CV_TYPE_LIST:
            return self._images_data(*self._data_pipeline(*args))
        else:
            train, validation, test = self._data_pipeline(*args)
            return [train], [validation], [test]

    def read_all_data(self, split_transform_function=None):
        """
        download all data
        """
        reader = self.reader(config.DATA_SOURCE_READ_SIZE, 0,
                             self.datasource.total(), split_transform_function)
        for idx, content in enumerate(reader):
            if self.source_type not in DST.CV_TYPE_LIST:
                if idx == 0:
                    self.column_meta = reader.meta
                    self.alldata = content
                elif 'result' in content and 'result' in self.alldata:
                    self.alldata['result'].extend(content['result'])
            else:
                self.alldata.extend(content)
        return self.alldata

    def _data_pipeline(self, stf, atf, fp, ignore_dp=False, ignore_split=False):
        # 获取全部数据(切片数据处理， 列选择和数据筛选)
        alldata = self.read_all_data(stf)

        if not alldata:
            logger.warning("Data is empty")

        # 数据处理（时间序列，全局函数和特征工程）
        _data_process_args = [alldata, atf, fp]
        if ignore_dp:
            _data_process_args.append(True)
        alldata = self._data_process(*_data_process_args)

        # 数据集切分
        _get_set_spliter_args = [alldata, self.source_type]
        if ignore_split:
            _get_set_spliter_args.append(True)
        spliter = get_set_spliter(*_get_set_spliter_args)

        # 数据集处理 图片下载/语料下载/数据返回
        return spliter.train_reader(), spliter.validation_reader(), spliter.test_reader()

    def _data_process(self, alldata, atf, fp, do_nothing=False):
        """
        download -> filter -> spliter -> user
        """
        if atf is None and fp is None:
            do_nothing = True

        if do_nothing is True:
            pass
        elif self.source_type in DST.CV_TYPE_LIST:
            pass
        elif atf or fp:
            alldata = atf(alldata) if atf else alldata
            alldata = fp(alldata) if fp else alldata
        return alldata

    def _images_data(self, train, val, test):
        tr = self.datasource.download_images(
            train, dataset_type=DatasetType.TRAIN)
        v = self.datasource.download_images(
            val, dataset_type=DatasetType.VALID)
        te = self.datasource.download_images(
            test, dataset_type=DatasetType.TEST)
        return tr, v, te

    def _nlp_data(self, split_mode: int):
        self.datasource.corpora_process(split_mode)
        return [self.datasource()] * 3

    def _large_model_data(self, split_mode: int):
        self.datasource.corpora_process(split_mode)
        return self.datasource()


class MultipleDataSets:
    def __init__(self) -> None:
        self._total = 0
        self.datasets: List[DataSets] = []
        self.join_type = "no"
        self.model_type = gl.model_type  # 分类/回归/ocr/时间序列/文本分类。。。。。
        self.column_meta = []

    @property
    def total(self):
        return self._total

    @property
    def onlyone(self):
        return self._total == 1

    def add(self, dataset: DataSets):
        self.datasets.append(dataset)
        self._total += 1

    def pop(self, idx=None):
        if idx is not None and isinstance(idx, int):
            return self.datasets.pop(idx)
        return self.datasets.pop()

    @overload
    def data_pipeline(self, split_transform_function,
                      alldata_transform_function, feature_process):
        pass

    def read_all_data(self, split_transform_function=None):
        # TODO 多数据集暂时不支持特征工程
        return [d.read_all_data() for d in self.datasets]

    def data_pipeline(self, *args):
        result = None
        # TODO 这块的配置不支持混合模式
        for idx in range(self._total):
            dataset = self.pop(0)
            if dataset.source_type in DST.NLP_TYPE_LIST:
                result = dataset._nlp_data(
                    config.DATA_SPLIT_MODE
                )
            elif dataset.source_type in DST.LARGE_MODEL_LIST:
                result = dataset._large_model_data(
                    config.DATA_SPLIT_MODE
                )
            elif dataset.source_type in DST.CV_TYPE_LIST:
                result = dataset._images_data(
                    *dataset._data_pipeline(*args)
                )
            else:
                if not result:
                    result = [[None] * self._total for _ in range(3)]

                gl.dataset_idx = idx
                # TODO 多数据集暂时不支持特征工程
                this_args = list(args) + [True]
                result[0][idx], result[1][idx], result[2][idx] = dataset._data_pipeline(
                    *this_args)
                self.column_meta.extend(dataset.column_meta)
        return result


def get_dataset(cfg) -> Union[DataSets, MultipleDataSets]:
    """
    use dataset config to get dataset inforew

    """
    if not cfg:
        dataset_conf = [{"SOURCE_TYPE": DST.EMPTY}]
    elif isinstance(cfg, str):
        dataset_conf = json.loads(cfg)
    else:
        dataset_conf = cfg

    # 格式校验
    assert isinstance(dataset_conf, list), "dataset config must list"

    # table, cv, nlp
    mds = MultipleDataSets()
    for conf in dataset_conf:
        datasource, stype = DatasetSelector.parse(conf)
        mds.add(DataSets(datasource, stype))
    if mds.onlyone:
        return mds.pop()
    return mds


def get_datasource_writer(cfg: str = None) -> AbstractDataSourceWriter:
    """
    use dataset config to get dataset writer info
    """
    output_datasource_type = 0
    cfg = cfg or config.OUTPUT_DATASET_INFO
    if cfg:
        if isinstance(cfg, str):
            cfg = json.loads(cfg)
        output_datasource_type = cfg['sourceType']
    if output_datasource_type == DST.EMPTY:
        return EmptyDataSourceWriter()
    elif output_datasource_type in (DST.INTELLIV, DST.IW_FACTORY_DATA):
        from intelliw.datasets.dataset_writer import DataSourceWriter
        return DataSourceWriter(output_config=cfg, writer_type=output_datasource_type)
    else:
        err_msg = f"输出数据源设置失败，无效的数据源类型: {output_datasource_type}"
        raise ValueError(err_msg)
