'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-03-27 11:20:17
LastEditors: Hexu
Description: 从数据工场获取模型数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_iwfactorydata.py
'''
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, DataSourceType, \
    DatasetSelector
from intelliw.utils import iuap_request, util
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config
from pandas.api.types import is_numeric_dtype

logger = _get_framework_logger()


def err_handler(request, exception):
    print("请求出错,{}".format(exception))


class DataSourceIwFactoryData(AbstractDataSource):
    """
    数据工场数据源
    """

    def __init__(self, input_address, get_row_address, get_table_meta, table_id, tenant_id=None):
        """
        智能分析数据源
        :param input_address:   获取数据 url
        :param get_row_address: 获取数据总条数 url
        :param table_id:   表Id
        """
        self.input_address = input_address
        self.get_row_address = get_row_address
        self.get_table_meta = get_table_meta
        self.table_id = table_id
        self.__total = None
        self.tenant_id = tenant_id if tenant_id is not None else config.TENANT_ID

    def total(self):
        """获取数据总行数"""
        if self.__total is not None:
            return self.__total
        response = iuap_request.post_json(
            self.get_row_address, json={'tableid': self.table_id, 'ytenantId': config.TENANT_ID},
            auth_type=iuap_request.AuthType.YHT)
        if response.status != 200:
            msg = f"获取行数失败，url: {self.get_row_address}, response: {response}"
            raise DataSourceReaderException(msg)
        row_data = response.json

        try:
            count = row_data["data"]["count"]
            self.__total = count if isinstance(count, int) else 0
            return self.__total
        except Exception:
            msg = f"获取行数返回结果错误, response: {row_data}, request_url: {self.get_row_address}"
            raise DataSourceReaderException(msg)

    def table_meta(self):
        response = iuap_request.post_json(
            self.get_table_meta, json={'logicIds': [self.table_id], 'ytenantId': config.TENANT_ID},
            auth_type=iuap_request.AuthType.YHT)
        if response.status != 200:
            msg = f"获取表信息失败，url: {self.get_table_meta}, response: {response}"
            raise DataSourceReaderException(msg)
        row_data = response.json

        try:
            meta = row_data["data"][0]["fieldList"]
            return [{'type': m['columnType'], 'code': m['columnName']} for m in meta]
        except Exception:
            msg = f"获取表信息失败, response: {row_data}, request_url: {self.get_table_meta}"
            raise DataSourceReaderException(msg)

    def reader(self, page_size=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.input_address, self.table_id, self.table_meta(), self.total(), self.tenant_id
                             , page_size, transform_function)

    class __Reader:
        def __init__(self, input_address, table_id, table_meta, total, tenant_id, page_size=10000, transform_function=None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            self.input_address = input_address
            self.table_id = table_id
            self.meta = table_meta
            self.num_table_meta = self.get_number_column(self.meta)
            self.total_rows = total
            self.page_size = max(100, page_size)
            self.page_num = 1
            self.total_read = 0
            self.transform_function = transform_function
            self.worker = min(3, max(1, os.cpu_count()))
            self.tenant_id = tenant_id
            logger.info(f'数据获取中: 启用的获取线程 {self.worker} 条')

        def get_number_column(self, table_meta):
            # 所有数值型字段返回的都是字符型， 需要转一下
            number_column = []
            for m in table_meta:
                _type = m['type'].upper()
                if _type in util.DB_NUM_TYPE:
                    number_column.append(m['code'])
            return number_column

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
                    for i in range(self.worker * 2):
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
            except StopIteration:
                raise StopIteration
            except Exception as e:
                logger.exception(
                    f"智能工场数据源读取失败, input_address: [{self.input_address}, {self.table_id}]")
                raise DataSourceReaderException(f'智能工场数据源读取失败,{e}')

        def _data_process(self, result):
            assert result is not None, "智能工场数据接口未返回任何有效数据"

            data = result['data']
            if len(data) == 0:
                return []

            # 数据过滤
            df = pd.DataFrame(data=data)
            for nm in self.num_table_meta:
                if not is_numeric_dtype(df[nm]):
                    df[nm] = pd.to_numeric(df[nm], errors='coerce')
            # 数据format
            return df.values.tolist()

        def _read_page(self, page_index, page_size):
            """
            数据工场获取数据接口，分页读取数据
            :param page_index: 页码，从 0 开始
            :param page_size:  每页大小

            此接口：pageIndex 代表起始下标（不是页）， pagesize代表每页数据的数量， pagecount代表获取几页
                   但是返回的数据类型是[{},{}] 而不是 [[{},{}],[]], 所以保证pageSize和pageCount中某一个数为1的时候， 另一个参数就可以当size使用（很迷惑）
            例如： {'id': self.table_id, 'pageIndex': 1,'pageSize': 10, 'pageCount': 1} 和 {'id': self.table_id, 'pageIndex': 1,'pageSize': 1, 'pageCount': 10} 的结果完全一致
            :return:
            """
            request_data = {
                'id': self.table_id,
                'pageIndex': page_index,
                'pageCount': page_size,
                'ytenantId': config.TENANT_ID
            }
            response = iuap_request.post_json(
                url=self.input_address, json=request_data, timeout=60, auth_type=iuap_request.AuthType.YHT)
            response.raise_for_status()
            result = response.json
            return self._data_process(result)


DatasetSelector.register_func(DataSourceType.IW_FACTORY_DATA, DataSourceIwFactoryData, {
    "input_address": "INPUT_ADDR",
    "get_row_address": "INPUT_GETROW_ADDR",
    "get_table_meta": "INPUT_DATA_META_ADDR",
    "table_id": "INPUT_DATA_SOURCE_ID",
    "tenant_id": "TENANT_ID"})
