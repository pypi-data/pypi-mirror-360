'''
Author: Hexu
Date: 2022-08-16 10:18:29
LastEditors: Hexu
LastEditTime: 2023-05-10 14:21:04
FilePath: /iw-algo-fx/intelliw/utils/spark_process/engine.py
Description: data process engine
'''
import inspect
import threading
from functools import wraps
from typing import Tuple, Union
import numpy as np
import pandas as pd
from random import Random
from intelliw.utils.exception import DatasetException, FeatureProcessException
from intelliw.config.config import SPARK_MODE, SPARK_MASTER_URL, FRAMEWORK_MODE, FrameworkMode
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()

# 只有训练才需要spark
if SPARK_MODE and FRAMEWORK_MODE in (FrameworkMode.DistTrain, FrameworkMode.Train):
    try:
        from intelliw.utils.spark_process.spark import Spark
        from pyspark import pandas as ps
        from pyspark.ml.feature import (Bucketizer, MaxAbsScaler, MinMaxScaler,
                                        QuantileDiscretizer, StandardScaler,
                                        VectorAssembler)
        from pyspark.pandas.series import Series as SparkSeries
        from pyspark.sql import functions as F
        from pyspark.ml.functions import vector_to_array
        from pyspark.sql.types import DoubleType, IntegerType
        from pyspark.sql.dataframe import DataFrame as SparkDF

        _unlist = F.udf(lambda x: float(list(x).pop()), DoubleType())
    except ImportError:
        raise ImportError(
            "\033[31mIf use spark, you need: pip install pyspark and pyarrow>=2.0.0\033[0m")
else:
    SPARK_MODE = False

random = Random(1024)


class CsvProcessEngine:
    type = "csv"

    def __init__(self, filepath: str, local_mode=True) -> None:
        self.filepath = filepath
        if local_mode:
            self.spark_mode = False
        else:
            self.spark_mode = SPARK_MODE

        if self.spark_mode:
            self.spark_core = Spark.get_spark(master=SPARK_MASTER_URL)

    def read(self, nrows=None, skiprows=None) -> list:
        if self.spark_mode:
            csv = self.spark_core.read_file(
                CsvProcessEngine.type, self.filepath)
            if skiprows is not None:
                csv = csv.rdd.zipWithIndex().filter(
                    lambda x: x[1] > skiprows).map(lambda x: x[0]).toDF()
            if nrows is not None:
                csv = csv.limit(nrows)
            return csv.toPandas()
        else:
            coding = ["utf8", "GB2312", "GBK", "GB18030", "utf-8-sig"]
            for c in coding:
                try:
                    return pd.read_csv(self.filepath, nrows=nrows, skiprows=skiprows, encoding=c)
                except UnicodeDecodeError:
                    continue
                except pd.errors.EmptyDataError:
                    raise DatasetException("empty csv")
            else:
                raise UnicodeDecodeError(
                    f"Can Not Encoding, Support Coding: {coding}")


class Engine:
    _instance_lock = threading.Lock()
    spark_mode = SPARK_MODE

    def __new__(cls):
        if not hasattr(Engine, "_instance"):
            with Engine._instance_lock:
                if not hasattr(Engine, "_instance"):
                    if Engine.spark_mode:
                        Engine.spark_core = Spark.get_spark(master=SPARK_MASTER_URL)
                    Engine._instance = object.__new__(cls)
                    _mode = "Spark" if Engine.spark_mode else "Normal"
                    logger.info(
                        f"\033[33mData Process Engine: {_mode}\033[0m")
        return Engine._instance

    def __init__(self) -> None:
        self.pd = pd
        if Engine.spark_mode:
            self.ps = Engine.spark_core.ps
            self.ps.set_option('compute.ops_on_diff_frames', True)
            SparkFeatureProcess._hijacked()
        else:
            self.ps = None

    def isna(self, obj):
        if Engine.spark_mode:
            return self.ps.isna(obj)
        return self.pd.isna(obj)

    def csv(self, filepath) -> CsvProcessEngine:
        return CsvProcessEngine(filepath)

    def DataFrame(self, data=None, index=None, columns=None, dtype=None, copy=False):
        if Engine.spark_mode:
            df = self.ps.DataFrame(
                data, index=index, columns=columns, dtype=dtype, copy=copy)
        else:
            df = self.pd.DataFrame(data, index=index,
                                   columns=columns, dtype=dtype, copy=copy)
        return df

    def concat(self, objs: list, axis: int = 0, join: str = "outer", ignore_index: bool = False, sort: bool = False):
        if Engine.spark_mode:
            df = self.ps.concat(objs, axis=axis, join=join,
                                ignore_index=ignore_index, sort=sort)
        else:
            df = self.pd.concat(objs, axis=axis, join=join,
                                ignore_index=ignore_index, sort=sort)
        return df

    def to_numeric(self, arg, errors='raise'):
        if Engine.spark_mode:
            df = self.ps.to_numeric(arg, errors)
        else:
            df = self.pd.to_numeric(arg, errors)
        return df

    def cut(self, x,
            bins,
            right: bool = True,
            labels=None,
            retbins: bool = False,
            precision: int = 3,
            include_lowest: bool = False,
            duplicates: str = "raise"):
        if Engine.spark_mode:
            x, _ = SparkFeatureProcess.bucket({'boundaries': bins}, x, "")
        else:
            df = self.pd.cut(x, bins, right, labels, retbins,
                             precision, include_lowest, duplicates)
        return df

    def pivot_table(self, data,
                    values=None,
                    index=None,
                    columns=None,
                    fill_value=None, ):
        if Engine.spark_mode:
            df = data.to_spark()
            df = df.groupBy(index).pivot(columns).sum(values)
            df = df.pandas_api()
        else:
            df = self.pd.pivot_table(
                data, values=values, index=index, columns=columns, fill_value=fill_value)
        return df


class SparkFeatureProcess:

    @staticmethod
    def _hijacked():
        from intelliw.functions import feature_process as fp
        for f in dir(SparkFeatureProcess):
            if not f.startswith("_") \
                    and hasattr(fp, f) \
                    and inspect.isfunction(getattr(fp, f)):
                hijacked_func = getattr(SparkFeatureProcess, f)
                setattr(fp, f, hijacked_func)

    # feature_process.
    def _dataframe_process(f):
        @wraps(f)
        def inner(params, col_frame, mode):
            # input
            if isinstance(col_frame, SparkSeries):
                col_frame = col_frame.to_frame()
            col_frame = col_frame.to_spark()

            # do process
            result = f(params, col_frame, mode)

            # output
            is_multi_result, frame_idx = type(result) == tuple, None
            if is_multi_result:
                result = list(result)
                for idx, c in enumerate(result):
                    if isinstance(c, SparkDF):
                        col_frame, frame_idx = c.pandas_api(), idx
                        break
            elif isinstance(result, SparkDF):
                col_frame = result.pandas_api()
            else:
                return result

            if col_frame.shape[-1] == 1:
                col_frame = col_frame[col_frame.columns[0]]
            if is_multi_result and frame_idx is not None:
                result[frame_idx] = col_frame
                return result
            else:
                return col_frame

        return inner

    @staticmethod
    def _to_vector(df: object) -> object:
        col_name, new_col = df.columns.pop(), "new_col"
        assembler = VectorAssembler(
            inputCols=[col_name], outputCol=new_col, handleInvalid="keep")
        df: object = assembler.transform(df)
        df = df.select(new_col).withColumnRenamed(new_col, col_name)
        return df

    @staticmethod
    @_dataframe_process
    def ordinal(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[object, Union[str, dict, list]]:
        col_name = col_frame.columns.pop()
        category = col_frame.select(col_name).distinct().collect()
        category_list = [i[col_name] for i in category]
        params['category_list'] = category_list

        if col_frame.where(~col_frame[col_name].isin(category_list)).count() > 0:
            # when not in category_list is len(category_list) other keep the data
            col_frame = col_frame.withColumn(
                col_name,
                F.when(
                    ~F.col(col_name).isin(
                        category_list), len(category_list)
                ).otherwise(
                    F.col(col_name)
                ))

        # ordinal
        for i, cate in enumerate(category_list):
            col_frame = col_frame.withColumn(
                col_name,
                F.when(
                    F.col(col_name) == cate, int(i)
                ).otherwise(
                    F.col(col_name)
                ))
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def one_hot(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[object, Union[str, dict, list]]:
        col_name, drop_col_name = col_frame.columns.pop(), "drop_col"
        category = col_frame.select(col_name).distinct().collect()
        category_list = [i[col_name] for i in category]
        params['category_list'] = category_list
        col_frame = col_frame.withColumnRenamed(col_name, drop_col_name)
        for i, cate in enumerate(category_list + [None]):
            col_frame = col_frame.withColumn(
                str(i),
                F.when(
                    F.col(drop_col_name) == cate, 1
                ).otherwise(
                    0
                ))
        col_frame = col_frame.drop(drop_col_name)
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def quantile_transform(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name, new_col_name = col_frame.columns.pop(), "new_col"

        bucket_size = max(2, params.get('bucket_size', 10))
        model = QuantileDiscretizer(numBuckets=bucket_size, inputCol=col_name,
                                    outputCol=new_col_name, relativeError=0.01,
                                    handleInvalid="keep").fit(col_frame)
        boundaries = model.getSplits()
        params['boundaries'] = boundaries[1:-1]  # drop -inf inf
        col_frame = model.transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name, F.col(new_col_name).cast(IntegerType())
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def log_transform(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name = col_frame.columns.pop()
        if col_frame.where((col_frame[col_name].isNotNull()) & (col_frame[col_name] < 0)).count() > 0:
            raise FeatureProcessException(
                'log_transform transform can only handle the data bigger than zero! while there are negetive data in dataframe')

        col_frame = col_frame.withColumn(
            col_name,
            F.when(
                F.col(col_name).isNotNull(),
                F.log(float(10), F.col(col_name) + 1)
            ).otherwise(
                F.col(col_name)
            ))
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def standard_scale(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name, new_col_name = col_frame.columns.pop(), "new_col"
        col_frame = SparkFeatureProcess._to_vector(col_frame)
        model = StandardScaler(
            inputCol=col_name, outputCol=new_col_name,
            withStd=True, withMean=True
        ).fit(col_frame)
        params['mean'] = list(model.mean).pop()
        params['std'] = list(model.std).pop()

        col_frame = model.transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name,
            _unlist(new_col_name)
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def max_abs_scale(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name, new_col_name = col_frame.columns.pop(), "new_col"
        col_frame = SparkFeatureProcess._to_vector(col_frame)
        model = MaxAbsScaler(
            inputCol=col_name, outputCol=new_col_name
        ).fit(col_frame)
        params['max_abs'] = list(model.maxAbs).pop()

        col_frame = model.transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name,
            _unlist(new_col_name)
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def min_max_scale(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name, new_col_name = col_frame.columns.pop(), "new_col"
        col_frame = SparkFeatureProcess._to_vector(col_frame)
        model = MinMaxScaler(
            inputCol=col_name, outputCol=new_col_name
        ).fit(col_frame)
        params['max'] = list(model.originalMax).pop()
        params['min'] = list(model.originalMin).pop()
        col_frame = model.transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name,
            _unlist(new_col_name)
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def bucket(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[object, Union[str, dict, list]]:
        if not ('boundaries' in params and len(params['boundaries']) > 0):
            raise FeatureProcessException(
                "for bucket transform ,boundaries can't be empty!")
        col_name, new_col_name = col_frame.columns.pop(), "new_col"
        bins = [float('-inf')] + params['boundaries'] + [float('inf')]

        model = Bucketizer(
            splits=bins, inputCol=col_name, outputCol=new_col_name, handleInvalid="keep")
        col_frame = model.transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name, F.col(new_col_name).cast(IntegerType())
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def translation(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name = col_frame.columns.pop()
        min = col_frame.rdd.min()[col_name]
        params['min'] = min
        if min < 0:
            col_frame = col_frame.withColumn(
                col_name, F.col(col_name) + abs(min))
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def square(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[object, Union[str, dict, list]]:
        col_name = col_frame.columns.pop()
        col_frame = col_frame.withColumn(
            col_name,
            F.when(
                col_frame[col_name].isNotNull(), F.col(col_name) *
                                                 F.col(col_name)
            ).otherwise(
                F.col(col_name)
            ))
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def robust_scale(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        col_name = col_frame.columns.pop()
        median, quant25, quant75 = col_frame.approxQuantile(
            col_name, [0.5, 0.25, 0.75], 0.01)
        params['median'] = median
        params['quant25'] = quant25
        params['quant75'] = quant75
        if quant25 != quant75:
            col_frame = col_frame.withColumn(
                col_name,
                F.when(
                    F.col(col_name).isNotNull(),
                    (F.col(col_name) - median) / (quant75 - quant25)
                ).otherwise(
                    F.col(col_name)
                ))
        return col_frame, params

    @staticmethod
    def drop(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[object, Union[str, dict, list]]:
        return ps.DataFrame(), params

    @staticmethod
    @_dataframe_process
    def hash_feature(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        hash_bucket_size = max(2, params.get('bucket_size', 10))
        params['bucket_size'] = hash_bucket_size
        col_name = col_frame.columns.pop()
        tohash = F.udf(lambda x: hash(x) % hash_bucket_size, IntegerType())
        col_frame = col_frame.withColumn(
            col_name,
            F.when(
                F.col(col_name).isNotNull(),
                tohash(col_name)
            ).otherwise(
                F.col(col_name)
            ))
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def interval_bucket(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        bucket_size = params.get('bucket_size', 10)
        boundaries = []

        col_name, new_col_name = col_frame.columns.pop(), "new_col"
        _rdd = col_frame.rdd
        minim = _rdd.min()[col_name]
        maxim = _rdd.max()[col_name]
        del _rdd

        for pos in range(1, bucket_size):
            boundaries.append((maxim - minim) * pos / bucket_size + minim)
        params['boundaries'] = boundaries

        bins = [float('-inf')]
        bins.extend(boundaries)
        bins.append(float('inf'))

        bucketizer = Bucketizer(
            splits=bins, inputCol=col_name, outputCol=new_col_name)
        col_frame = bucketizer.setHandleInvalid("keep").transform(col_frame)
        col_frame = col_frame.select(
            new_col_name
        ).withColumn(
            new_col_name,
            F.col(new_col_name).cast(IntegerType())
        ).withColumnRenamed(
            new_col_name, col_name
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def kmeans_bucket(params: Union[str, dict, list], col_frame: object, mode: str) -> Tuple[
        object, Union[str, dict, list]]:
        from sklearn.cluster import KMeans
        col_name = col_frame.columns.pop()
        data = col_frame.pandas_api().to_numpy().reshape(-1, 1)
        k = max(2, params.get('bucket_size', 10))
        kmeans = KMeans(n_clusters=k).fit(data)
        centers = kmeans.cluster_centers_
        params['cluster_centers'] = centers
        dist = [abs(data - c).reshape(-1) for c in centers]
        label = np.array(dist).argmin(axis=0)
        col_frame = Spark.sc.parallelize(
            label
        ).map(
            lambda x: (int(x) if x is not None else None,)
        ).toDF(
            [col_name]
        )
        return col_frame, params

    @staticmethod
    @_dataframe_process
    def numeric_miss_check_repair(check_repair_config: Union[str, dict, list], col_frame: object, mode: str) -> object:
        col_name = col_frame.columns.pop()
        group_cols = check_repair_config['group_cols']
        index = check_repair_config['index']
        mr = check_repair_config['miss_repair']

        if mr == '1':
            mean = col_frame.pandas_api().mean()[0]
            col_frame = col_frame.fillna(mean)
        elif mr == '2':
            col_frame = col_frame.fillna(0)
        elif mr == '3':
            median = col_frame.approxQuantile(col_name, (0.5,), 0.01)[0]
            col_frame = col_frame.fillna(median)
        elif mr == '4':
            mode = col_frame.groupby(col_name).count().orderBy(
                "count", ascending=False).first()[0]
            col_frame = col_frame.fillna(mode)
        elif mr == '6':
            pass
        elif type(check_repair_config['miss_repair']) == dict:
            if check_repair_config['miss_repair']['repair_type'] == '7':
                if not ('quantile_low' in check_repair_config['miss_repair'] and 'quantile_high' in check_repair_config[
                    'miss_repair']):
                    raise FeatureProcessException(
                        f"origin_col_num:{index}, when miss_repair='7', quantile_low and  quantile_high must be set")
                low = check_repair_config['miss_repair']['quantile_low']
                high = check_repair_config['miss_repair']['quantile_high']
                if not (0.0 <= low <= high <= 1.0):
                    raise FeatureProcessException(
                        f"origin_col_num:{index}, quantile_low and quantile_high must between 0.0 and 1.0, and quantile_low must be smaller than quantile_high ")

                quantile_high = col_frame.approxQuantile(
                    col_name, (high,), 0.01)[0]
                quantile_low = col_frame.approxQuantile(
                    col_name, (low,), 0.01)[0]
                val = quantile_low + \
                      (quantile_high - quantile_low) * random.random()

                if check_repair_config['type'].lower() in ['int', 'integer']:
                    val = int(val)
                col_frame = col_frame.fillna(val)
        return col_frame

    @staticmethod
    @_dataframe_process
    def numeric_outlier_check(check_repair_config, col_frame, mode):
        index = check_repair_config['index']
        if 'outlier_check' not in check_repair_config:
            raise FeatureProcessException(
                f"origin_col_num:{index}, outlier_check config missing!")
        if not (check_repair_config['outlier_check'] in ['1', '2', '3']):
            raise FeatureProcessException(
                f"origin_col_num:{index}, outlier_check must be in ['1', '2', '3']!")

        low, high = 0, 0
        col_name = col_frame.columns.pop()
        # 3 西格玛
        if check_repair_config['outlier_check'] == '1':
            new_col_name = "new_col"
            col_frame = SparkFeatureProcess._to_vector(col_frame)
            model = StandardScaler(
                inputCol=col_name, outputCol=new_col_name,
                withStd=True, withMean=True
            ).fit(col_frame)
            mean = list(model.mean).pop()
            std = list(model.std).pop()
            low = mean - 3 * std
            high = mean + 3 * std
        elif check_repair_config['outlier_check'] == '2':
            quantile25 = col_frame.approxQuantile(col_name, (0.25,), 0.01)[0]
            quantile75 = col_frame.approxQuantile(col_name, (0.75,), 0.01)[0]
            low = quantile25 - 1.5 * (quantile75 - quantile25)
            high = quantile75 + 1.5 * (quantile75 - quantile25)
        return low, high

    @staticmethod
    @_dataframe_process
    def numeric_outlier_repair(check_repair_config, col_frame, mode):
        index = check_repair_config['index']
        if not ('outlier_repair' in check_repair_config):
            raise FeatureProcessException(
                f"origin_col_num:{index}, outlier_repair config missing!")
        if not (check_repair_config['outlier_repair'] in ['1', '2', '3']):
            raise FeatureProcessException(
                f"origin_col_num:{index}, outlier_repair must in ['1', '2', '3']!")

        col_name = col_frame.columns.pop()
        if check_repair_config['outlier_repair'] == '1':
            new_col_name = "new_col"
            col_frame = SparkFeatureProcess._to_vector(col_frame)
            model = StandardScaler(
                inputCol=col_name, outputCol=new_col_name,
                withStd=True, withMean=True
            ).fit(col_frame)
            mean = list(model.mean).pop()
            std = list(model.std).pop()
            low = mean - 3 * std
            high = mean + 3 * std
            col_frame = col_frame.select(
                vector_to_array(col_name).alias(col_name))
            col_frame = col_frame.withColumn(
                col_name,
                F.when(
                    F.col(col_name)[0] < low, low
                ).when(
                    F.col(col_name)[0] > high, high
                ).otherwise(
                    F.col(col_name)[0]
                ))
        elif check_repair_config['outlier_repair'] == '2':
            quantile25 = col_frame.approxQuantile(col_name, (0.25,), 0.01)[0]
            quantile75 = col_frame.approxQuantile(col_name, (0.75,), 0.01)[0]
            low = quantile25 - 1.5 * (quantile75 - quantile25)
            high = quantile75 + 1.5 * (quantile75 - quantile25)

            col_frame = col_frame.withColumn(
                col_name,
                F.when(
                    F.col(col_name) < low, low
                ).when(
                    F.col(col_name) > high, high
                ).otherwise(
                    F.col(col_name)
                ))
        return col_frame

    @staticmethod
    @_dataframe_process
    def category_miss_check_repair(check_repair_config, col_frame, mode):
        col_name = col_frame.columns.pop()
        if check_repair_config['miss_repair'] == '4':
            mode = col_frame.groupby(col_name).count().orderBy(
                "count", ascending=False).first()[0]
            col_frame = col_frame.fillna(mode)
        elif check_repair_config['miss_repair'] == '6':
            pass
        return col_frame
