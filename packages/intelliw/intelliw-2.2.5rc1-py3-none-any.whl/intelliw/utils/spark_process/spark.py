'''
Author: Hexu
Date: 2022-08-16 10:23:16
LastEditors: Hexu
LastEditTime: 2023-03-28 16:50:55
FilePath: /iw-algo-fx/intelliw/utils/spark_process/spark.py
Description: spark function
'''
import os
from intelliw.utils.exception import DatasetException
from pyspark import SparkContext
from pyspark import pandas as ps
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame as SparkDF
import warnings
warnings.filterwarnings('ignore')


app_name = "INTELLIW_SPARK_NAME"


class ReadFileType:
    CSV = "csv"
    TXT = "txt"
    JSON = "json"


class Spark(object):
    """
    Container class holding SparkContext and SparkSession instances, so that any changes
    will be propagated across the application
    """
    sc = None
    spark = None
    ps = ps

    # config

    def __new__(cls, *args, **kwargs):
        if cls is Spark:
            raise TypeError(
                'SparkSession & SparkContext container class may not be instantiated.')
        return object.__new__(cls, *args, **kwargs)

    @classmethod
    def get_sc(cls, master=None, appName=None, sparkHome=None, pyFiles=None, environment=None,
               batchSize=0, conf=None, gateway=None, jsc=None):
        """Creates and initializes a new `SparkContext` (the old one will be stopped).
        Argument signature is copied from `pyspark.SparkContext
        <https://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext>`_.
        """
        if cls.sc is not None:
            cls.sc.stop()
        cls.sc = SparkContext(master=master, appName=appName, sparkHome=sparkHome, pyFiles=pyFiles, environment=environment, batchSize=batchSize,
                              conf=conf, gateway=gateway, jsc=jsc)
        cls.__init_spark()

    @classmethod
    def get_spark(cls, master=None, appName=None, conf=None, hive_support=False):
        """Creates and initializes a new `SparkSession`. Argument signature is copied from
        `pyspark.sql.SparkSession
        <https://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.SparkSession>`_.
        """
        if cls.spark is not None:
            return Spark

        sess = SparkSession.builder
        if master:
            sess.master(master)

        if appName:
            sess.appName(appName)
        else:
            sess.appName(app_name)

        if conf:
            conf["spark.sql.debug.maxToStringFields"] = 10000
            sess.config(conf=conf)
        else:
            sess.config("spark.sql.debug.maxToStringFields", "10000")

        if hive_support:
            sess.enableHiveSupport()

        cls.spark = sess.getOrCreate()
        return Spark

    @classmethod
    def init_default(cls):
        """Create and initialize a default SparkContext and SparkSession"""
        if cls.spark is None and cls.sc is None:
            cls.__init_sc()
            cls.__init_spark()
        return Spark

    @classmethod
    def __init_sc(cls):
        cls.sc = SparkContext(appName=app_name).getOrCreate()

    @classmethod
    def __init_spark(cls):
        cls.spark = SparkSession.builder.appName(app_name).config(
            "spark.sql.debug.maxToStringFields", "10000").getOrCreate()

    @classmethod
    def read_file(cls, filetype, filepath) -> SparkDF:
        if not os.path.isdir(filepath) and \
           not os.path.isfile(filepath) and \
           not os.path.islink(filepath):
            raise DatasetException(
                "spark read file error: Not a file、directory or hdfs link")
        if filetype == ReadFileType.CSV:
            return cls.spark.read.option("inferSchema", "true") \
                .option("header", "true") \
                .option("encoding", "gbk") \
                .csv(filepath)
        elif filetype == ReadFileType.TXT:
            return cls.spark.read.text(filepath)
        elif filetype == ReadFileType.JSON:
            return cls.spark.read.json(filepath)
        else:
            raise DatasetException("An unsupported spark type")

    @staticmethod
    def save_file(data, filetype, filepath) -> None:
        if filetype == ReadFileType.CSV:
            data.repartition(1) \
                .write.mode("overwrite") \
                .option("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false") \
                .option("header", "true") \
                .option("delimiter", ",") \
                .csv(filepath)
