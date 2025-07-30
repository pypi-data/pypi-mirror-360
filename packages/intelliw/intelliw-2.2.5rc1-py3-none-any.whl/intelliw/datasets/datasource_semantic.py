'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-26 19:54:39
LastEditors: Hexu
Description: 从语义模型获取模型数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_semantic.py
'''
from concurrent.futures import ThreadPoolExecutor
import os
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, \
    DataSourceType, DatasetSelector
from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class DataSourceSemanticData(AbstractDataSource):
    """
    语义模型数据源
    """

    def __init__(self, data_address, table_id, user_id, fields=None):
        """
        语义模型数据源
        :param data_address:   获取数据 url
        :param fields: 获取数据表字段
        :param table_id:   表Id
        """
        self.data_address = data_address
        self.table_id = table_id
        self.user_id = user_id
        self.fields = fields
        self.__total = None

    def total(self):
        """获取数据总行数"""
        if self.__total is not None:
            return self.__total

        data = {
            'entityId': self.table_id,
            'pager': {
                "pageIndex": 1,
                "pageSize": 1
            }
        }
        headers = {'user_id': self.user_id}
        response = iuap_request.post_json(
            self.data_address, json=data, headers=headers, auth_type=iuap_request.AuthType.YHT)
        if response.status != 200:
            msg = f"获取行数失败，url: {self.data_address}, response: {response}"
            raise DataSourceReaderException(msg)
        row_data = response.json

        self.__total = 0
        try:
            count = row_data["data"]["pager"]['recordCount']
            if isinstance(count, int):
                self.__total = count
        except Exception as e:
            msg = f"获取行数返回结果错误, response: {row_data}, request_url: {self.data_address}"
            raise DataSourceReaderException(msg)
        return self.__total

    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.data_address, self.table_id, self.fields, self.total(), self.user_id, pagesize,
                             transform_function)

    class __Reader:
        def __init__(self, data_address, table_id, fields, total, user_id, pagesize=5000, transform_function=None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            self.logger = _get_framework_logger()
            self.data_address = data_address
            self.table_id = table_id
            self.fields = fields
            self.page_size = max(100, pagesize)
            self.page_num = 1
            self.total_read = 0
            self.total_rows = total
            self.user_id = user_id
            self.meta = []
            self.worker = min(3, max(1, os.cpu_count()))
            self.transform_function = transform_function
            logger.info(f'数据获取中: 启用的获取线程 {self.worker} 条')

        def get_data_bar(self):
            """数据拉取进度条"""
            try:
                proportion = round(
                    (self.total_read / self.total_rows) * 100, 2)
                logger.info(
                    f"数据获取中: {self.total_read}/{self.total_rows}, 进度{proportion}%")
            except:
                pass

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            if self.total_read >= self.total_rows:
                logger.info('数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                raise StopIteration

            self.get_data_bar()

            try:
                with ThreadPoolExecutor(max_workers=self.worker) as executor:
                    futures, data_result = [], []
                    for i in range(self.worker):
                        futures.append(executor.submit(
                            self._read_page, self.page_num, self.page_size
                        ))
                        self.page_num += 1

                    for f in futures:
                        data_result.extend(f.result())
                    self.total_read += len(data_result)
                    if len(data_result) == 0:
                        logger.info(
                            '数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                        raise StopIteration

                    return_data = {"result": data_result, "meta": self.meta}
                    if self.transform_function is not None:
                        return_data = self.transform_function(return_data)
                    return return_data
            except Exception as e:
                logger.exception(
                    f"语义模型数据源读取失败, data_address: [{self.table_id}]")
                raise DataSourceReaderException(f'语义模型数据源读取失败: {e}')

        def _get_meta(self, meta):
            if self.meta == []:
                self.meta = meta
            return self.meta

        def _data_process(self, result):
            assert result is not None, "语义模型数据接口未返回任何有效数据"
            data = result["data"]
            assert data is not None, f"接口返回无数据, 请联系数据负责人：{result}"
            if len(data) > 0:
                self._get_meta(data['meta'])
            return data['result']

        def _read_page(self, page_index, page_size):
            """
            语义模型获取数据接口，分页读取数据
            :param page_index: 页码，从 0 开始
            :param page_size:  每页大小

            此接口：pageIndex 代表起始下标（不是页）， pagesize代表每页数据的数量， pagecount代表获取几页
                   但是返回的数据类型是[{},{}] 而不是 [[{},{}],[]], 所以保证pageSize和pageCount中某一个数为1的时候， 另一个参数就可以当size使用（很迷惑）
            例如： {'id': self.table_id, 'pageIndex': 1,'pageSize': 10, 'pageCount': 1} 和 {'id': self.table_id, 'pageIndex': 1,'pageSize': 1, 'pageCount': 10} 的结果完全一致
            :return:
            """
            request_data = {
                'entityId': self.table_id,
                'pager': {
                    "pageIndex": page_index,
                    "pageSize": page_size
                }
            }
            headers = {'user_id': self.user_id}
            response = iuap_request.post_json(
                url=self.data_address, json=request_data, headers=headers, timeout=30,
                auth_type=iuap_request.AuthType.YHT)
            response.raise_for_status()
            result = response.json
            return self._data_process(result)


DatasetSelector.register_func(DataSourceType.SEMANTIC, DataSourceSemanticData, {
    "data_address": "INPUT_ADDR",
    "table_id": "INPUT_MODEL_ID",
    "user_id": "USER_ID"})
