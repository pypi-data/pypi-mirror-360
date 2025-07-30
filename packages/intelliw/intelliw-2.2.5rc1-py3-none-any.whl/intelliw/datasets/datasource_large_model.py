"""
Author: liutengx
Date: 2024-03-05 14:54:05
LastEditTime: 2024-03-05 14:54:05
LastEditors: liutengx
Description: 大模型数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_large_model.py
"""
import json
import os
import shutil
import time
from random import Random

from intelliw.config import config
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceType, DatasetSelector
from intelliw.datasets.spliter import get_set_count, check_split_ratio
from intelliw.utils import iuap_request
from intelliw.utils.exception import DatasetException
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class CorpusType:
    json = 'json'


class FineTuningSerType:
    train = 'train'
    test = 'test'
    mixed = 'mixed'
    general = 'general'


class DataSourceLMCorpora(AbstractDataSource):
    """
    大模型数据处理
    """
    # dataset_class 一共有 训练 验证 测试 三种数据集
    dataset_class = 3
    # file_name 文件名称
    file_name = ['train.json', 'val.json', 'test.json']
    # 共几个数据集， 当大于1时，写到同一个文件
    dataset_count = 0
    # counts 数据集总行数
    counts = [0] * dataset_class

    def __init__(self, source_address: str, ds_id: str, set_type: str, tenant_id: str = None,
                 download_dir='./tmp_local_large_model_origin_data/'):
        DataSourceLMCorpora.dataset_count += 1
        self.dataset_no = DataSourceLMCorpora.dataset_count

        self.ratio = [config.TRAIN_DATASET_RATIO,
                      config.VALID_DATASET_RATIO, config.TEST_DATASET_RATIO]
        check_split_ratio(*self.ratio)

        self.random = Random(config.DATA_RANDOM_SEED)
        self.download_dir = download_dir

        self.ds_id = ds_id
        self.source_address = source_address
        self.dirpath = [config.LARGE_MODEL_TRAIN_FILEPATH,
                        config.LARGE_MODEL_VAL_FILEPATH, config.LARGE_MODEL_TEST_FILEPATH]
        self.set_type = set_type
        self.tenant_id = tenant_id if tenant_id is not None else config.TENANT_ID

    def total(self):
        return 1

    def reader(self, *args, **kwargs):
        return list()

    def corpora_process(self, split_mode: int = 0):
        """ 大模型数据切分

        Args:
            split_mode (int, optional): 0顺序 1乱序. Defaults to 0.

        此方法中所有长度3的列表, 均代表 [训练, 验证, 测试]
        """
        # 生成数据文件夹
        self._gen_corpora_dir()

        start_time = time.time()
        # 切分函数的缓存, 减少切分次数
        spliter_cache = {}
        # io_reader 数据集写入文件io
        dataset_list = [[], [], []]
        if DataSourceLMCorpora.dataset_count > 1:
            for i in range(DataSourceLMCorpora.dataset_class):
                file_path = os.path.join(self.dirpath[i], self.file_name[i])
                if os.path.exists(file_path):
                    with open(file_path, "r") as fp:
                        dataset_list[i] = json.load(fp)

        # 进行多文件循环数据集拆分
        for epoch, part in enumerate(self._get_reader()):
            # split_mode 根据拆分模式进行处理
            if split_mode:
                self.random.shuffle(part)
            part_count = len(part)

            # set_data 此part数据集原始数据,切分规则按混合数据集[1,0,0],验证数据集[0,1,0]
            set_data = [[]] * DataSourceLMCorpora.dataset_class
            nums = [0] * DataSourceLMCorpora.dataset_class
            if self.set_type == FineTuningSerType.mixed:
                nums = spliter_cache.get(part_count)
                if nums is None:
                    nums = [part_count, 0, 0] if part_count < 10 else get_set_count(
                        part_count, *self.ratio)
                    spliter_cache[part_count] = nums
            elif self.set_type in [FineTuningSerType.train, FineTuningSerType.general]:
                nums = [part_count, 0, 0]
            elif self.set_type == FineTuningSerType.test:
                nums = [0, 0, part_count]

            _start, _end = 0, 0
            for idx, num in enumerate(nums):
                _end += num
                set_data[idx] = part[_start:] if idx == len(nums) - 1 else part[_start:_end]
                _start += num
            part.clear()

            # 更新数据集总数据
            for idx, num in enumerate(nums):
                DataSourceLMCorpora.counts[idx] += num

            [i.extend(s) for i, s in zip(dataset_list, set_data)]

            logger.info(
                f"大模型数据文件下载中: train: {DataSourceLMCorpora.counts[0]} 条, validation: {DataSourceLMCorpora.counts[1]} 条, "
                f"test: {DataSourceLMCorpora.counts[2]} 条")

        # 关闭所有句柄
        for i in range(DataSourceLMCorpora.dataset_class):
            file_path = os.path.join(self.dirpath[i], self.file_name[i])
            with open(file_path, "w", encoding="utf-8") as fp:
                json.dump(dataset_list[i], fp, ensure_ascii=False)

        logger.info(
            f"大模型数据[{self.dataset_no}]下载完成: total: {sum(DataSourceLMCorpora.counts)} 条, "
            f"train: {DataSourceLMCorpora.counts[0]} 条, "
            f"validation: {DataSourceLMCorpora.counts[1]} 条, "
            f"test: {DataSourceLMCorpora.counts[2]} 条, "
            f"time: {time.time() - start_time}")

        # 清空下载文件夹
        shutil.rmtree(self.download_dir, ignore_errors=True)

    def _gen_corpora_dir(self):
        filepath = os.path.join('./', config.LARGE_MODEL_FILEPATH)
        if os.path.exists(filepath) and self.dataset_no == 1:
            logger.warn(f"大模型数据保存路径存在:{filepath}, 正在删除路径内容")
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(config.LARGE_MODEL_TRAIN_FILEPATH, 0o755, True)
        os.makedirs(config.LARGE_MODEL_VAL_FILEPATH, 0o755, True)
        os.makedirs(config.LARGE_MODEL_TEST_FILEPATH, 0o755, True)

    def __call__(self):
        abspath = os.path.abspath('.')
        return [os.path.join(abspath, config.LARGE_MODEL_TRAIN_FILEPATH, self.file_name[0]),
                os.path.join(abspath, config.LARGE_MODEL_VAL_FILEPATH, self.file_name[1]),
                os.path.join(abspath, config.LARGE_MODEL_TEST_FILEPATH, self.file_name[2])]

    # reader
    def _get_reader(self, pagesize=5000):
        return DataSourceLMCorpora.__OnlineReader(self.source_address, self.ds_id, self.tenant_id, pagesize)

    class __OnlineReader:
        def __init__(self, input_address, ds_id, tenant_id, limit=5000):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            # self.logger = _get_framework_logger()
            self.input_address = input_address
            self.ds_id = ds_id
            self.page_size = max(100, limit)
            self.page_num = 0
            self.total_read = 0
            self.tenant_id = tenant_id

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            """
            {
                "data": {
                    "content": ["...","..."],
                    "pageNumber": 0,
                    "pageSize": 1,
                    "totalElements": 14,
                    "totalPages": 14
                },
                "msg": "成功",
                "status": 1
            }
            """
            page = None
            try:
                page = self._read_page(self.page_num, self.page_size)
                assert page is not None, "获取的数据为空"
                if page['status'] != 1:
                    raise Exception(page['msg'])
                if page['data']['totalElements'] == 0:
                    raise Exception("大模型 数据获取失败, 无数据")
                content = page['data']['content']
                content = [json.loads(i) for i in content]
            except Exception as e:
                errmsg = f"大模型 数据获取失败, \nds_id: [{self.ds_id}], \nerror: [{e}], \nresponse: {page}"
                raise DatasetException(errmsg)

            if len(content) == 0:
                raise StopIteration
            self.page_num += 1
            self.total_read += len(content)
            return content

        def _read_page(self, page_num, page_size):
            """
            调用智能分析接口，分页读取数据
            :param page_num: 页码，从 0 开始
            :param page_size:  每页大小
            :return:
            """
            request_data = {'dsId': self.ds_id, 'pageNumber': page_num,
                            'pageSize': page_size, 'yTenantId': self.tenant_id}
            response = iuap_request.post_json(url=self.input_address, json=request_data)
            response.raise_for_status()
            return response.json


DatasetSelector.register_func(DataSourceType.LARGE_MODEL, DataSourceLMCorpora, {
    "source_address": ["LARGE_MODEL_PATH", "INPUT_ADDR"],
    "ds_id": "INPUT_DATA_SOURCE_ID",
    "set_type": "FINE_TUNING_SET_TYPE",
    "tenant_id": "TENANT_ID"})
