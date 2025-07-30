import uuid
from abc import ABCMeta, abstractmethod
import datetime
import os
from intelliw.utils.storage_service import StorageService
from intelliw.datasets.datasource_base import AbstractDataSourceWriter, DataSourceWriterException, DataSourceType as DST
from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config
import pandas as pd
import tempfile
import json
import traceback

logger = _get_framework_logger()


class OutputCheckException(Exception):
    def __init__(self, msg) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return '数据输出校验失败:\n错误原因: {}'.format(self.msg) + '''
发生错误的可能：
    1 返回字段是否与数据库定一致
    2 返回字段的列名是否与每行一一对应
    3 如果使用数据输出功能，返回数据格式应为：
        {
            "meta":[
                {"code":"col1"},
                {"code":"col2"},
                {"code":"col3"}
            ],
            "result":[
                ["col1_value1", "col2_value1", "col3_value1"],
                ["col1_value2", "col2_value2", "col3_value2"],
                ["col1_value3", "col2_value3", "col3_value3"],
            ]
        }'''

    def ignore_stack(self):
        return True


class OutputConfigException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return '数据输出配置文件参数错误，请检查参数:\n{}'.format(self.msg)

    def ignore_stack(self):
        return True


class OutputRequestException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return '数据输出接口请求出错:\n{}'.format(self.msg)

    def ignore_stack(self):
        return True


class AbstractEngineWriter(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.table_columns = None
        self.write_successed = {"status": 1}
        self.write_failed = {"status": 0}

    @abstractmethod
    def write(self, data, **kwargs):
        pass


class UserWriter(AbstractEngineWriter):
    def write(self, data, **kwargs):
        pass


class SqlWriter(AbstractEngineWriter):
    def __init__(self) -> None:
        super().__init__()
        self.uri = ""
        self.table_name = ""
        self.batch_size = 10000
        self.driver = ""
        self.engine = self.__get_engine()

    def __get_engine(self):
        from intelliw.utils.database import connection
        connection.get_engine(self.driver, uri=self.uri)

    def write(self, data, **kwargs):
        frame = pd.DataFrame(data["result"], columns=data["mate"])
        start_index = 0
        end_index = self.batch_size if self.batch_size < len(
            frame) else len(frame)

        frame = frame.where(pd.notnull(frame), None)
        if_exists_param = 'replace'

        while start_index != end_index:
            logger.info("Writing rows %s through %s" %
                        (start_index, end_index))
            frame.iloc[start_index:end_index, :].to_sql(
                con=self.engine, name=self.table_name, if_exists=if_exists_param)
            if_exists_param = 'append'

            start_index = min(start_index + self.batch_size, len(frame))
            end_index = min(end_index + self.batch_size, len(frame))
        return self.write_successed


class DataCommonWriter(AbstractEngineWriter):
    def __init__(self, output_config):
        super().__init__()
        self.request_timeout = 3000
        self.batch_size = 3000
        self.default_column = ['id', 'batch_no', 'ts']
        self.id_prefix = str(uuid.uuid4())
        try:
            if not output_config:
                raise Exception("OUTPUT DATASET INFO 为空")
            # table
            self.table_meta = output_config['tableMeta']
            self.logic_table_id = self.table_meta['tableId']
            self.train_batch = self.table_meta['trainBatch']
            self.table_name = self.table_meta['tableName']
            self.table_columns = self.table_meta['columns']

            # params
            self.params = output_config['params']
            self.output_addr = self.params['outputURL']
            self.datasource_id = self.params['outputSourceID']

            if len(self.train_batch) == 0:
                raise Exception("train batch 为空")
        except Exception as e:
            traceback.print_exc()
            raise OutputConfigException(e)

    def check(self, user_data) -> pd.DataFrame:
        if self.logic_table_id == "" and (self.table_name == "" or self.datasource_id == ""):
            raise OutputConfigException(
                "logic_table_id/table_name、datasource_id 不能都为空")

        # 表字段校验
        table_column = {c['code']: True for c in self.table_columns}
        user_column = [c['code'] for c in user_data['meta']]

        if not set(user_column).issubset(table_column):
            raise Exception(
                f'用户数据存在数据表中不存在字段，数据表字段为:{table_column.keys()}, 用户字段为:{user_column}')

        # 数据校验
        rows = user_data['result']
        df = pd.DataFrame(columns=user_column, data=rows)

        # 清除关键字
        for c in self.default_column:
            if c in user_column:
                df = df.drop(labels=c, axis=1)
                logger.warn(f"[Output] DataCommonWriter drop user column: {c}")

        return df

    def _push_to_source(self, df: pd.DataFrame):
        columns = self.default_column + df.columns.tolist()
        req = {
            "logicTableId": self.logic_table_id,
            "ytenantId": config.TENANT_ID,
            "datasourceId": self.datasource_id,
            "dataModel": {
                "tableName": self.table_name,
                "columnSchema": columns,
            }
        }
        total = df.shape[0]
        df.insert(0, 'id', self.id_prefix + df.index.astype(str))
        split_data = None
        for idx in range(0, total, self.batch_size):
            ts = str(datetime.datetime.now())
            end_idx = min(total, idx + self.batch_size)
            logger.info("[Output] DataCommonWriter push data index: %d to %d, total: %d",
                        idx, end_idx, total)
            split_data = df[idx:end_idx].copy()
            split_data.insert(1, 'batch_no', self.train_batch)
            split_data.insert(2, 'ts', ts)
            req['dataModel']['modelData'] = split_data.values.tolist()
            resp = iuap_request.post_json(
                url=self.output_addr, json=req,
                headers={'service-code': 'iuap-aip-console'},
                timeout=self.request_timeout,
                auth_type=iuap_request.AuthType.YHT)
            resp.raise_for_status()
            resp_content = resp.json
            logger.info("[Output] DataCommonWriter response: %s", resp_content)
            if not isinstance(resp_content, dict) or resp_content.get("code") == 1:
                req['dataModel']['modelData'] = "数据隐藏"
                raise OutputRequestException(
                    f"request: {json.dumps(req, ensure_ascii=False, indent=1)},\nresponse: {resp_content}")

        del split_data
        return True

    def _push_to_s3(self, df: pd.DataFrame):
        curkey = os.path.join(config.STORAGE_SERVICE_PATH,
                              self.train_batch, "output.csv")
        with tempfile.NamedTemporaryFile() as temp:
            filename = temp.name + '.csv'
            df.to_csv(filename, index=False)
            StorageService(curkey, "upload").upload(filename)
        return curkey

    def write(self, data):
        try:
            df = self.check(data)
        except Exception as e:
            traceback.print_exc()
            raise OutputCheckException(e)

        try:
            self._push_to_source(df)
        except Exception as e:
            logger.error(
                f"[Output]DataCommonWriter push data error:{e}, try to s3")
            curkey = self._push_to_s3(df)
            raise OutputRequestException(
                f"DataCommonWriter push data error:{e}, try to s3: {curkey}")
        return self.write_successed


class DataSourceWriter(AbstractDataSourceWriter):
    def __init__(self, **kwargs):
        super().__init__()
        self.writer_info = kwargs
        self.writer_type = kwargs.get("writer_type")

        try:
            self.writer = self.__get_writer()
            self.table_columns = self.writer.table_columns
        except Exception as e:
            raise DataSourceWriterException(
                f"Data Output Initialization Error: {e}")

    def __get_writer(self) -> AbstractEngineWriter:
        if self.writer_type == DST.SQL:
            return SqlWriter()
        elif self.writer_type in (DST.IW_FACTORY_DATA, DST.INTELLIV):
            output_config = self.writer_info["output_config"]
            return DataCommonWriter(output_config)
        else:
            return UserWriter()

    def write(self, data, **kwargs):
        try:
            return self.writer.write(data=data, **kwargs)
        except Exception as e:
            raise DataSourceWriterException(f"Data Output Process error: {e}")
