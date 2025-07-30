'''
Author: hexu
Date: 2021-11-19 10:29:02
LastEditTime: 2023-05-23 18:48:50
LastEditors: Hexu
Description: 文件存储服务
FilePath: /iw-algo-fx/intelliw/utils/storage_service.py
'''
import json
import os
import io
import mimetypes
import traceback
import logging
from intelliw.utils import iuap_request
from intelliw.config import config
import urllib.parse as urlparse


class StorageService:
    """
    文件传输，通过服务端获取的临时url进行文件在多个云存储（AliOss/Minio/HWObs）上的操作
    所有的请求需要进行加签
    """

    def __init__(self, key, process_type):
        """
        初始化下载/上传链接
            Args:
                key :
                    upload ： 文件存储于桶的位置（包含文件名） OSS_PATH + filename
                    download : AI工作坊存储在环境变量的值     DATA_SOURCE_ADDRESS
                process_type : download/upload
            Returns:
                self.service_url 为服务端根据client_type，process_type生成的链接， download和upload操作需要此链接
        """
        self.key = key
        self.service_url = self.__client_init(
            key, process_type)
        self.content_type = mimetypes.guess_type(
            key)[0] or 'application/octet-stream'
        if self.content_type == "text/csv":
            self.content_type = 'application/octet-stream'

    def __client_init(self, key, process_type):
        """
        从服务端获取云存储操作链接

        下载链接一般可以直接下载的
        """
        data = {
            'key': key,
            'UrlType': process_type,
            'instanceid': config.INSTANCE_ID
        }
        client_type = self._get_client_type(config.FILE_UP_TYPE)
        if client_type != "":
            data["clientType"] = client_type

        # shit
        if os.environ.get('useGpaas') == 'true':
            STORAGE_SERVICE_URL = f"{os.environ.get('domain.url')}{os.environ.get('STORAGE_SERVICE_URL')}" or \
                                  config.STORAGE_SERVICE_URL
        else:
            STORAGE_SERVICE_URL = os.environ.get('STORAGE_SERVICE_URL') or config.STORAGE_SERVICE_URL
        if not STORAGE_SERVICE_URL:
            raise EnvironmentError("STORAGE_SERVICE_URL is not set")
        resp = iuap_request.get(url=STORAGE_SERVICE_URL, params=data)
        resp.raise_for_status()
        result = resp.json
        assert result.get("status") == 1, result
        return result.get("data")

    def upload(self, file):
        """
        通过操作链接进行上传操作
            Args:
                file ： 上传文件本地路径/文件流
        """

        def _put_file(f):
            headers = {'Content-Type': self.content_type}
            resp = iuap_request.put_file(
                url=self.service_url, headers=headers, data=f)
            resp.raise_for_status()

        if isinstance(file, str) and os.path.exists(file) and os.path.isfile(file):
            with open(file, 'rb') as f:
                _put_file(f)
        elif isinstance(file, (bytes, bytearray, io.BufferedIOBase)):
            _put_file(file)
        else:
            file = json.dumps(file, ensure_ascii=False).encode('utf-8')
            _put_file(file)

    def download(self, output_path, stream=False):
        """
        通过操作链接进行下载操作
            Args:
                output_path ： 下载文件保存路径
        """
        if os.path.exists(output_path):
            raise FileExistsError(f'文件 {output_path} 已存在')
        if stream:
            iuap_request.stream_download(
                method="get", url=self.service_url, output_path=output_path)
        else:
            iuap_request.download(url=self.service_url,
                                  output_path=output_path)

    def _get_client_type(self, _type):
        env_val = _type.upper()
        if env_val == "MINIO":
            return "Minio"
        elif env_val == "ALIOSS":
            return "AliOss"
        elif env_val == "HWOBS":
            return "HWObs"
        else:
            return ""


class FileTransferDevice(Exception):
    """FileTransferDevice 文件传输引擎

    使用方法:
        >>> from intelliw.feature import FileTransferDevice
        >>> ftd = FileTransferDevice(fileobj/filepath, "report_type", filename="xxx.csv")

    如果文件上传后需要中断服务（e.g. 数据集检查出错，上传检查报告后，中断训练服务）
        >>> if "存在某些错误":
        >>>     ftd.msg = "xxxxx错误"
        >>>     raise ftd

    :param file 必须 上传的文件, 可以是路径, 也可以是open后的文件
    :param transfer_type 必须 上传文件的业务类型
    :param filename 非必需 上传后文件的名称，类型需要与源文件一致(.csv/.json)
    :param msg 非必需 错误信息
    """

    def __init__(self, file, transfer_type, filename="data", msg="") -> None:
        self.url = ""
        self.curkey = None
        self.msg = msg
        self.upload_msg = None
        self.transfer_type = transfer_type
        self.__put_file__(file, filename)

    def __put_file__(self, file, filename) -> None:
        import intelliw.utils.message as message
        from intelliw.utils.global_val import gl

        try:
            if config.is_server_mode():
                # filename
                if isinstance(file, str) and os.path.isfile(file):
                    filename = os.path.basename(file)

                # s3 path
                self.curkey = os.path.join(
                    config.STORAGE_SERVICE_PATH, config.SERVICE_ID, filename
                )

                # file upload
                uploader = StorageService(self.curkey, "upload")
                uploader.upload(file)

                url = urlparse.urlparse(uploader.service_url)
                self.url = url.scheme + "://" + url.netloc + url.path

                # report
                if gl.recorder:
                    gl.recorder.report(message.CommonResponse(
                        200, 'file_transfer', 'success',
                        {'filepath': self.curkey},
                        businessType=self.transfer_type))
        except Exception as e:
            self.upload_msg = e
            logging.error("上传文件错误: %s, %s", e, traceback.format_exc())

    def __str__(self) -> str:
        msg = f"算法服务中断: {self.msg}\n中断类型: {self.transfer_type}\n"
        if self.upload_msg is None:
            msg += f'文件上传：成功\n中断原因查看：{self.curkey}'
        else:
            msg = f'文件上传：失败\n上传失败信息: {self.upload_msg}'
        return msg

    def ignore_stack(self):
        """
        error ignore stack
        """
        return True

    def btype(self):
        """
        error btype
        """
        return self.transfer_type
