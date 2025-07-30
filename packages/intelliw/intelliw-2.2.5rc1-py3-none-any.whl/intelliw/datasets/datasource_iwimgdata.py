'''
Author: Hexu
Date: 2022-04-25 15:16:48
LastEditors: Hexu
LastEditTime: 2023-05-11 09:45:28
FilePath: /iw-algo-fx/intelliw/datasets/datasource_iwimgdata.py
Description: 图片数据集
'''
import json
import os
import shutil

from intelliw.config import config
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, DatasetSelector, \
    DataSourceType
from intelliw.utils.exception import DataSourceDownloadException
from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = _get_framework_logger()


def is_classification():
    """Checks whether the dataset is for image classification.

    Returns:
        bool: True if the dataset is for image classification, False otherwise.
    """
    from intelliw.utils.global_val import gl
    return gl.model_type == 12


class CocoProcess:
    coco_type = 3
    coco_config = None
    licenses = None
    info = None
    categories = None
    set_config = None
    current_no = 0

    @classmethod
    def set_coco_info(cls, instance, prefix):
        cls.info = instance['info']
        cls.licenses = instance['licenses']
        cls.categories = instance['categories']
        cls.coco_config = cls.__gen_config(
            instance['images'], instance['annotations'], prefix)
        cls.reset_config()

    @classmethod
    def reset_config(cls):
        cls.set_config = {'licenses': cls.licenses, 'info': cls.info,
                          'categories': cls.categories, 'images': [], 'annotations': []}

    @classmethod
    def __gen_config(cls, images, annotations, prefix):
        a_map, i_config = {}, {}
        for a in annotations:
            image_id = a['image_id']
            a_map[image_id] = a_map.get(image_id, [])
            a_map[image_id].append(a)
        for i in images:
            i['file_name'] = prefix + i['file_name']
            i_config[i['file_name']] = {
                'image': i, 'annotation': a_map[i['id']]}
        return i_config

    @classmethod
    def gen_config(cls, filename):
        meta = cls.coco_config.get(filename)
        if meta is None:
            return f"image:{filename} annotation not exist"
        cls.set_config['images'].append(meta['image'])
        cls.set_config['annotations'].extend(meta['annotation'])
        return None

    @classmethod
    def flush(cls, path, dataset_no):
        if dataset_no > 1 and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as rfp:
                cfg = json.load(rfp)
                cls.set_config['images'].extend(cfg['images'])
                cls.set_config['annotations'].extend(cfg['annotations'])
        with open(path, 'w') as wfp:
            json.dump(cls.set_config, wfp, ensure_ascii=False)


class DataSourceIwImgData(AbstractDataSource):
    """
    非结构化存储数据源
    图片数据源
    """

    # 共几个数据集， 当大于1时，写到同一个文件
    dataset_count = 0

    def __init__(self, input_address, get_row_address, ds_id, ds_type, tenant_id=None):
        """
        智能分析数据源
        :param input_address:   获取数据 url
        :param get_row_address: 获取数据总条数 url
        :param ds_id:   数据集Id
        :param ds_type: cv标注类型: 0-自有 1-labelme 2-voc 3-coco
        :param is_classification 是否为分类数据集，需要做样本均分
        """
        DataSourceIwImgData.dataset_count += 1
        self.dataset_no = DataSourceIwImgData.dataset_count

        self.input_address = input_address
        self.get_row_address = get_row_address
        self.ds_id = ds_id
        self.ds_type = ds_type
        self.__total = None
        self.__gen_img_dir()
        self.is_classification = is_classification()
        self.tenant_id = tenant_id if tenant_id is not None else config.TENANT_ID

    def __gen_img_dir(self):
        logger = _get_framework_logger()
        filepath = os.path.join('./', config.CV_IMG_FILEPATH)
        if os.path.exists(filepath) and self.dataset_no == 1:
            logger.warn(f"图片数据保存路径存在:{filepath}, 正在删除路径内容")
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(config.CV_IMG_ANNOTATION_FILEPATH, 0o755, True)
        os.makedirs(config.CV_IMG_TRAIN_FILEPATH, 0o755, True)
        os.makedirs(config.CV_IMG_VAL_FILEPATH, 0o755, True)
        os.makedirs(config.CV_IMG_TEST_FILEPATH, 0o755, True)

    def total(self):
        if self.__total is not None:
            return self.__total
        params = {'dsId': self.ds_id, 'yTenantId': self.tenant_id}
        response = iuap_request.get(self.get_row_address, params=params)
        if 200 != response.status:
            msg = "获取行数失败，url: {}, response: {}".format(
                self.get_row_address, response)
            raise DataSourceReaderException(msg)

        row_data = response.json
        self.__total = row_data['data']

        if not isinstance(self.__total, int):
            msg = "获取行数返回结果错误, response: {}, request_url: {}".format(
                row_data, self.get_row_address)
            raise DataSourceReaderException(msg)
        return self.__total

    def reader(self, page_size=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        r = self.__Reader(self.input_address, self.ds_id, self.ds_type, self.total(), dataset_type, self.tenant_id,
                          page_size, transform_function, is_classification=self.is_classification)
        r.dataset_no = self.dataset_no
        return r

    def download_images(self, images, transform_function=None, dataset_type='train_set'):
        r = self.reader(transform_function=transform_function,
                        dataset_type=dataset_type)
        r.dataset_no = self.dataset_no
        r.set_download(images)
        return r()

    class __Reader:
        def __init__(self, input_address, ds_id, ds_type, total, process_type, tenant_id, page_size=100,
                     transform_function=None, is_classification=False):
            self.input_address = input_address
            self.ds_id = ds_id
            self.ds_type = ds_type
            self.total_data = total
            self.total_read = 0
            self.page_size = max(100, page_size)
            self.page_num = 0
            self.process_type = process_type
            self.transform_function = transform_function
            self.worker = min(3, max(1, os.cpu_count()))
            self.dataset_no = 0
            self.is_classification = is_classification
            self.tenant_id = tenant_id

        def get_data_bar(self):
            """数据拉取进度条"""
            try:
                proportion = round(
                    (self.total_read / self.total_data) * 100, 2)
                logger.info(
                    f"图片数据集[{self.dataset_no}]元数据下载获取中: 共{self.total_data}条数据, 已获取{self.total_read}条, 进度{proportion}%")
            except:
                pass

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            logger = _get_framework_logger()
            if self.total_read >= self.total_data:
                logger.info(
                    f'图片数据集[{self.dataset_no}]元数据下载完成，准备下载图片，共读取原始数据 {self.total_read} 条')
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
                        page = f.result()
                        data = page['data']['content']
                        data_result.extend(self._label_process(data))

                    self.total_read += len(data_result)
                    if len(data_result) == 0:
                        logger.info(
                            f'图片数据集[{self.dataset_no}]元数据下载完成，准备下载图片，共读取原始数据 {self.total_read} 条')
                        raise StopIteration
                    return data_result
            except StopIteration:
                raise StopIteration
            except Exception as e:
                logger.exception(
                    f"图片数据集[{self.dataset_no}]数据源读取失败, input_address: [{self.ds_id}]")
                raise DataSourceReaderException(f'图片数据源读取失败:{e}')

        def _label_process(self, data):
            if self.is_classification:
                for idx, d in enumerate(data):
                    labels = d.get('labels', [])
                    if len(labels) == 0:
                        raise Exception("分类数据集含有未标注的图片")
                    data[idx]['labels'] = labels[0]['name']
            return data

        def _read_page(self, page_index, page_size):
            """
            图片数据接口，分页读取数据
            :param page_index: 页码，从 0 开始
            :param page_size:  每页大小
            :return:
            """
            request_data = {'dsId': self.ds_id, 'pageNumber': page_index,
                            'pageSize': page_size,
                            'yTenantId': self.tenant_id,
                            'type': self.ds_type}
            response = iuap_request.get(
                url=self.input_address, params=request_data)
            response.raise_for_status()
            return response.json

        def set_download(self, page):
            logger = _get_framework_logger()
            prefix = str(
                self.dataset_no) if DataSourceIwImgData.dataset_count > 1 else ""
            logger.info(f"图片数据集[{self.dataset_no}]开始下载")
            if self.ds_type == CocoProcess.coco_type:
                CocoProcess.reset_config()
                if CocoProcess.current_no != self.dataset_no:
                    CocoProcess.current_no = self.dataset_no
                    annotation_urls = page[0]['annotationUrl']
                    annotation = save_file(
                        annotation_urls, timeout=90, is_img=False)
                    if annotation is None:
                        raise DataSourceReaderException(
                            f'图片数据级标注信息有误，标注文件地址：{annotation_urls}')
                    annotation = json.loads(annotation)
                    CocoProcess.set_coco_info(annotation, prefix)

            err_count, success_count, err_msg = 0, 0, ""
            with ThreadPoolExecutor(max_workers=self.worker) as executor:
                futures = [executor.submit(
                    self.__download, p, prefix) for p in page]
                for f in as_completed(futures):
                    try:
                        f.result()
                        success_count += 1
                        if success_count % 10 == 0:
                            logger.info(
                                f"图片数据集[{self.dataset_no}]下载中: {success_count}/{self.total_data}")
                    except Exception as e:
                        err_count += 1
                        err_msg = e
                        logger.error(
                            f'图片数据集[{self.dataset_no}]下载错误: {e}, total {err_count}')

            if err_count > self.total_data * 1e-2 and success_count / err_count < 1000:
                raise DataSourceDownloadException(
                    f"图片数据集[{self.dataset_no}]下载失败的图片过多,  successed: {success_count},  failed: {err_count}, msg: {err_msg}")

            if self.ds_type == CocoProcess.coco_type:
                filename = self.process_type + ".json"
                CocoProcess.flush(os.path.join(
                    '.', config.CV_IMG_ANNOTATION_FILEPATH, filename), self.dataset_no)

            logger.info(
                f"图片数据集[{self.dataset_no}] {self.process_type} 下载完成， 成功{success_count}, 失败{err_count}")

        def __download(self, page, prefix):
            url = page['url']
            annotation_url = page['annotationUrl']
            filename = prefix + page['rowFileName']
            annotationname = filename.replace(
                page['fileNameType'], page['annotationType'])

            # 图片下载， 图片可能伴随特征工程
            if self.process_type == 'train_set':
                process_file = config.CV_IMG_TRAIN_FILEPATH
            elif self.process_type == 'validation_set':
                process_file = config.CV_IMG_VAL_FILEPATH
            else:
                process_file = config.CV_IMG_TEST_FILEPATH

            filepath = os.path.join('.', process_file, filename)
            if save_file(url, filepath, self.transform_function, timeout=90, is_img=True) is None:
                raise Exception(f"image:{filename} download error")

            # 标注下载或写入内存
            if self.ds_type == CocoProcess.coco_type:
                err = CocoProcess.gen_config(filename)
                if err is not None:
                    raise KeyError(f"CocoProcess.gen_config error: {err}")
            else:
                filepath = os.path.join(
                    '.', config.CV_IMG_ANNOTATION_FILEPATH, annotationname)
                if save_file(annotation_url, filepath, is_img=False) is None:
                    raise Exception(
                        f"annotation:{annotationname} download error")

            return filename

        def __call__(self):
            abspath = os.path.abspath('.')
            return {'path': os.path.join(abspath, config.CV_IMG_FILEPATH),
                    'train_set': os.path.join(abspath, config.CV_IMG_TRAIN_FILEPATH),
                    'val_set': os.path.join(abspath, config.CV_IMG_VAL_FILEPATH),
                    'test_set': os.path.join(abspath, config.CV_IMG_TEST_FILEPATH),
                    'annotations': os.path.join(abspath, config.CV_IMG_ANNOTATION_FILEPATH)}


def save_file(url, filepath=None, transform_function=None, timeout=None, is_img=True):
    logger = _get_framework_logger()
    try:
        response = iuap_request.download(url=url)
        status = response.status
        if status == 200:
            data = response.body
            if is_img and transform_function:
                data = transform_function(data)
            if filepath:
                with open(filepath, 'wb') as fp:
                    fp.write(data)
                return filepath
            return data
        logger.error("http get url %s failed, status is %s", url, status)
        return None
    except Exception as e:
        logger.error("http get url %s failed, error is %s", url, e)
        return None


DatasetSelector.register_func(
    DataSourceType.IW_IMAGE_DATA, DataSourceIwImgData, {
        "input_address": "INPUT_ADDR",
        "get_row_address": "INPUT_GETROW_ADDR",
        "ds_id": "INPUT_DATA_SOURCE_ID",
        "ds_type": "INPUT_DATA_SOURCE_TRAIN_TYPE",
        "tenant_id": "TENANT_ID"})

if __name__ == '__main__':
    save_file(
        url='https://intelliw-console.oss-cn-beijing-internal.aliyuncs.com/AI-CONSOLE/iwdata/0000L4PB5VYW84IL8O0000/1826085601888698376/voc/2b820359dbbd83c981b6357e6edc4bee.xml?Expires=3272593373&OSSAccessKeyId=LTAI5tR6jdSeCNyRfTZ5CN2s&Signature=8E7KGaKrBIEgnAaBpLX4bBRLNok%3D',
        filepath="./a.xml", is_img=False)
