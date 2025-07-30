'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-25 14:49:05
LastEditors: Hexu
Description: 本地csv数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_local_csv.py
'''
import time
from intelliw.utils.exception import DatasetException
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, DataSourceType, \
    DatasetSelector
from intelliw.utils.global_val import gl
from intelliw.utils.logger import _get_framework_logger
from intelliw.utils.spark_process import Engine

logger = _get_framework_logger()
engine = Engine()


class DataSourceLocalCsv(AbstractDataSource):
    """
    本地 csv 文件数据源
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.__total = -1

    def total(self):
        if self.__total >= 0:
            return self.__total
        logger.info("start read files: %s", self.file_path)
        start_time = time.time()
        csv = engine.csv(self.file_path).read()
        self.__total = csv.index.size
        if self.__total == 0:
            raise DataSourceReaderException('csv 文件为空')
        logger.info("total: %s, load time: %s",
                    self.__total, time.time() - start_time)
        return self.__total

    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__DataSourceReaderLocalCsv(self.file_path, pagesize, offset, limit, transform_function)

    class __DataSourceReaderLocalCsv:
        """
        读取本地 csv
        """

        def __init__(self, file_path, pagesize=10000, offset=0, limit=0, transform_function=None):
            self.pagesize = pagesize
            self.is_stop = False
            self.file_path = file_path
            self.limit = limit
            self.meta = []  # csv 元数据
            self.read_count = 0
            self._init_meta()
            self.reader = self.__Reader(file_path, offset)
            self.transform_function = transform_function

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            if self.is_stop:
                raise StopIteration
            try:
                data = self._read_batch()
                return_data = {'result': data, 'meta': self.meta}
                if self.transform_function is not None:
                    return_data = self.transform_function(return_data)
                return return_data
            except Exception as e:
                logger.exception("csv 文件读取错误")
                self.reader.close()
                raise DataSourceReaderException('csv 文件读取失败') from e

        def _read_batch(self):
            if self.limit > 0 and self.read_count + self.pagesize >= self.limit:
                batch_amount = self.limit - self.read_count
                self.is_stop = True
            else:
                batch_amount = self.pagesize
            batch = self.reader.read(batch_amount)
            self.read_count += batch_amount
            if self.reader.is_finish:
                self.is_stop = True
            return batch

        def _init_meta(self):
            csv = engine.csv(self.file_path).read(nrows=0)
            self.meta = [{'code': i} for i in csv.columns.values.tolist()]

            # TODO 很恶心的逻辑 后续看看怎么干掉
            dataset_idx = gl.get("dataset_idx", 0)
            target_metadata = gl.target_metadata
            if isinstance(target_metadata, list) and len(target_metadata) > dataset_idx:
                target_info: dict = target_metadata[dataset_idx]
                target_col: int = target_info["target_col"]
                if target_col > len(self.meta):
                    raise DatasetException(
                        f"target column index:{target_col}, There are {len(self.meta)} "
                        f"columns in the source csv, index out of range")
                self.meta[target_col] = {'code': target_info["target_name"]}

        class __Reader:
            def __init__(self, file_path, offset=0):
                self.line_offset = offset
                self.is_finish = False
                self.file_path = file_path

            def close(self):
                del self.csv

            def read(self, amount=1):
                try:
                    self.csv = engine.csv(self.file_path).read(
                        skiprows=self.line_offset, nrows=amount)
                except DatasetException:
                    if self.line_offset == 0:
                        msg = 'csv 文件为空'
                    else:
                        msg = '超出范围的 offset {}'.format(self.line_offset)
                    raise DataSourceReaderException(msg)

                batch = self.csv.values.tolist()
                if len(batch) < amount:
                    self.is_finish = True
                    self.line_offset += len(batch)
                    return batch
                self.line_offset += amount
                return batch


DatasetSelector.register_func(DataSourceType.LOCAL_CSV, DataSourceLocalCsv, {
    "file_path": "CSV_PATH"})
