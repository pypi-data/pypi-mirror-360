'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-23 18:46:45
LastEditors: Hexu
Description: nlp数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_nlp_corpora.py
'''
from random import Random
import shutil
import time
import os
import fileinput
import zipfile
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceType, DatasetSelector
from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger
import traceback
from intelliw.utils.storage_service import StorageService
from intelliw.config import config
from intelliw.utils.exception import DatasetException
from intelliw.utils import unzip_file
from intelliw.datasets.spliter import get_set_count, check_split_ratio

logger = _get_framework_logger()


class CorpusType:
    csv = 'csv'
    json = 'json'
    txt = 'txt'

    ItoN = {20: "txt", 21: "csv", 22: "json"}


class CorpusInputType:
    local = 'local'
    file = 'file'
    row = 'row'


class DataSourceNLPCorpora(AbstractDataSource):
    """
    nlp语料处理
    """
    # dataset_class 一共有 训练 验证 测试 三种数据集
    dataset_class = 3
    # file_index 文件名称，self._file_batch行拆分一个
    file_index = [1] * dataset_class
    # 共几个数据集， 当大于1时，写到同一个文件
    dataset_count = 0
    # counts 数据集总行数
    counts = [0] * dataset_class

    def __init__(self, source_address: str, ds_id: str, source_train_type: int, tenant_id: str = None,
                 reader_type: str = CorpusInputType.local, download_dir='./tmp_local_nlp_corpora_origin_data/'):
        DataSourceNLPCorpora.dataset_count += 1
        self.dataset_no = DataSourceNLPCorpora.dataset_count

        self.ratio = [config.TRAIN_DATASET_RATIO,
                      config.VALID_DATASET_RATIO, config.TEST_DATASET_RATIO]
        check_split_ratio(*self.ratio)

        self._file_batch = 5e4
        self.random = Random(config.DATA_RANDOM_SEED)
        self.download_dir = download_dir

        self.ds_id = ds_id
        self.source_address = source_address
        self.source_train_type = source_train_type
        self._file_suffix = self._get_file_suffix(self.source_train_type)
        self.reader_type = reader_type if reader_type else CorpusInputType.local
        self.dirpath = [config.NLP_CORPORA_TRAIN_FILEPATH,
                        config.NLP_CORPORA_VAL_FILEPATH, config.NLP_CORPORA_TEST_FILEPATH]
        self.tenant_id = tenant_id if tenant_id is not None else config.TENANT_ID

        # 3种模式  local 和 file 需要进行预处理
        # local  语料文件在本地 本地测试用
        # file   接口获取的为语料文件
        # row    接口获取的为某行语料
        self._csv_label = None
        if self.reader_type != CorpusInputType.row:
            if self.reader_type == CorpusInputType.local:
                local_corpus = self.source_address
            else:
                local_corpus = self.__download_file(
                    self.source_address, self.ds_id, self.source_train_type, download_dir)
            self._file_list, self._csv_label = self._file_process(local_corpus)

    def total(self):
        return 1

    def reader(self, *args, **kwargs):
        return list()

    def corpora_process(self, split_mode: int = 0):
        """nlp语料切分

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
        io_reader = []
        for i in range(DataSourceNLPCorpora.dataset_class):
            file_path = os.path.join(
                self.dirpath[i], f"{DataSourceNLPCorpora.file_index[i]}.{self._file_suffix}")
            io_reader.append(open(file_path, "a", encoding="utf-8"))
            if self._csv_label:
                io_reader[i].write(self._csv_label)

        # 进行多文件循环数据集拆分
        for epoch, part in enumerate(self._get_reader()):
            # split_mode 根据拆分模式进行处理
            if split_mode:
                self.random.shuffle(part)
            part_count = len(part)

            # set_data 此part数据集原始数据
            set_data = [[]] * DataSourceNLPCorpora.dataset_class
            nums = spliter_cache.get(part_count)
            if nums is None:
                nums = [part_count, 0, 0] if part_count < 10 else get_set_count(
                    part_count, *self.ratio)
                spliter_cache[part_count] = nums

            _start, _end = 0, 0
            for idx, num in enumerate(nums):
                _end += num
                set_data[idx] = part[_start:] if idx == len(
                    nums) - 1 else part[_start:_end]
                _start += num
            part.clear()

            # 更新数据集总数据
            for idx, num in enumerate(nums):
                DataSourceNLPCorpora.counts[idx] += num

            # 将数据写入对应文件
            [i.writelines(s) for i, s in zip(io_reader, set_data)]

            # 5轮刷新一次缓存区，减少内存压力
            if epoch and epoch % 5 == 0:
                [i.flush() for i in io_reader]

            # 根据数据条数,更新句柄
            for idx, count in enumerate(DataSourceNLPCorpora.counts):
                if count > self._file_batch * DataSourceNLPCorpora.file_index[idx]:
                    DataSourceNLPCorpora.file_index[idx] += 1
                    file_path = os.path.join(
                        self.dirpath[idx],
                        f"{DataSourceNLPCorpora.file_index[idx]}.{self._file_suffix}"
                    )
                    io_reader[idx].close()
                    io_reader[idx] = open(file_path, "a", encoding="utf-8")
                    if self._csv_label:
                        io_reader[idx].write(self._csv_label)

            logger.info(
                f"语料文件下载中: train: {DataSourceNLPCorpora.counts[0]} 条, validation: {DataSourceNLPCorpora.counts[1]} 条, test: {DataSourceNLPCorpora.counts[2]} 条")

        # 关闭所有句柄
        [io.close() for io in io_reader]
        logger.info(
            f"语料[{self.dataset_no}]下载完成: total: {sum(DataSourceNLPCorpora.counts)} 条, train: {DataSourceNLPCorpora.counts[0]} 条, validation: {DataSourceNLPCorpora.counts[1]} 条, test: {DataSourceNLPCorpora.counts[2]} 条, time: {time.time() - start_time}")

        # 清空下载文件夹
        shutil.rmtree(self.download_dir, ignore_errors=True)

    def _gen_corpora_dir(self):
        logger = _get_framework_logger()
        filepath = os.path.join('./', config.NLP_CORPORA_FILEPATH)
        if os.path.exists(filepath) and self.dataset_no == 1:
            logger.warn(f"语料数据保存路径存在:{filepath}, 正在删除路径内容")
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(config.NLP_CORPORA_TRAIN_FILEPATH, 0o755, True)
        os.makedirs(config.NLP_CORPORA_VAL_FILEPATH, 0o755, True)
        os.makedirs(config.NLP_CORPORA_TEST_FILEPATH, 0o755, True)

    def __download_file(self, source_address, ds_id, source_train_type, download_dir):
        start_time = time.time()
        logger.info('Downloading nlp corpora from %s to %s',
                    source_address, download_dir)

        filepath = os.path.join('./', download_dir)
        if os.path.exists(filepath):
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(download_dir, 0o755, True)

        # 1 获取s3链接
        request_data = {'dsIds': ds_id,
                        'type': source_train_type, 'tenantId': self.tenant_id}
        response = iuap_request.post_json(
            url=source_address, json=request_data)
        response.raise_for_status()
        file_links = response.json.get("data", [])  # type: ignore
        if len(file_links) == 0:
            raise DatasetException(
                f"nlp corpora is empty, get data is {response.json}")

        # 2 下载文件
        for idx, link in enumerate(file_links):
            filename = f"{idx + 1}.{self._file_suffix}"
            filepath = os.path.join(
                download_dir, f"{idx + 1}.{self._file_suffix}")
            try:
                downloader = StorageService(
                    link, "download")
                downloader.download(filepath, stream=True)
                logger.info(
                    f"NLP语料 {filename} 下载成功, 耗时:{time.time() - start_time}s")
            except Exception as e:
                err = traceback.format_exc()
                raise DatasetException(f"NLP语料下载失败: {err}")
        return download_dir

    def _file_process(self, path):
        if zipfile.is_zipfile(path):
            logger.info("解压语料文件")
            dirpath = unzip_file(path)
        elif os.path.isdir(path):
            dirpath = path
        else:
            raise DatasetException(f"不支持的文件格式{path}")
        # 读取文件夹， 筛选文件
        file_list = []

        def get_file(d, f):
            for i in os.listdir(d):
                p = os.path.join(d, i)
                if i.endswith(self._file_suffix):
                    f.append(p)
                elif os.path.isdir(p):
                    get_file(p, f)
            return f

        file_list = get_file(dirpath, file_list)

        if len(file_list) == 0:
            raise DatasetException(
                f"未获取语料文件， 文件格式应为 .{self._file_suffix} 后缀文件")

        csv_label = self._get_csv_label(file_list)
        return file_list, csv_label

    def _get_csv_label(self, file_list):
        # 获取csv表头
        if self._file_suffix == CorpusType.csv:
            fp = open(file_list[0], encoding='utf-8')
            csv_label = fp.__next__()
            fp.close()
            return csv_label
        else:
            return None

    def _get_file_suffix(self, source_train_type):
        if source_train_type not in CorpusType.ItoN.keys():
            raise DatasetException(
                f"NLP语料类型错误: CorpusType is {source_train_type}, 20-txt 21-csv 22-json")
        return CorpusType.ItoN[source_train_type]

    def __call__(self):
        abspath = os.path.abspath('.')
        return {'path': os.path.join(abspath, config.NLP_CORPORA_FILEPATH),
                'train_set': os.path.join(abspath, config.NLP_CORPORA_TRAIN_FILEPATH),
                'val_set': os.path.join(abspath, config.NLP_CORPORA_VAL_FILEPATH),
                'test_set': os.path.join(abspath, config.NLP_CORPORA_TEST_FILEPATH)}

    # reader
    def _get_reader(self, pagesize=5000):
        if self.reader_type == "row":
            return DataSourceNLPCorpora.__OnlineReader(self.source_address, self.ds_id, self.tenant_id, pagesize)
        else:
            return self.__local_reader(self._file_list, pagesize)

    def __local_reader(self, file_paths, limit=5000, encoding="utf-8"):
        hook = fileinput.hook_encoded(encoding=encoding)
        with fileinput.input(files=file_paths, openhook=hook) as f:
            while True:
                part = []
                for _ in range(limit):
                    try:
                        t = f.__next__()
                        if f.isfirstline() and self._file_suffix == CorpusType.csv:
                            continue
                        part.append(t)
                    except StopIteration:
                        if part:
                            break
                        else:
                            return
                yield part

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
            self.logger = _get_framework_logger()
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
                    raise Exception("nlp 数据获取失败, 无已标注语料")
                content = page['data']['content']
                content = [i if i.endswith(
                    "\n") else f"{i}\n" for i in content]
            except Exception as e:
                errmsg = f"nlp 数据获取失败, \nds_id: [{self.ds_id}], \nerror: [{e}], \nresponse: {page}"
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
            response = iuap_request.post_json(
                url=self.input_address, json=request_data)
            response.raise_for_status()
            return response.json


DatasetSelector.register_func(DataSourceType.NLP_CORPORA, DataSourceNLPCorpora, {
    "source_address": ["NLP_CORPORA_PATH", "INPUT_ADDR"],
    "ds_id": "INPUT_DATA_SOURCE_ID",
    "source_train_type": "INPUT_DATA_SOURCE_TRAIN_TYPE",
    "reader_type": "NLP_CORPORA_INPUT_TYPE",
    "tenant_id": "TENANT_ID"})
