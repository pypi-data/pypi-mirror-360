import datetime
from typing import Iterable
from intelliw.datasets.datasource_base import AbstractDataSource, DatasetSelector, \
    DataSourceType, AbstractDataSourceWriter


class EmptyDataSourceWriter(AbstractDataSourceWriter):

    def write(self, data, starttime=None):
        if starttime is None:
            starttime = datetime.datetime.now()
        print(
            "datasource output: {}, starttime: {}".format(data, starttime))
        return {'status': 1}


class EmptyDataSource(AbstractDataSource):
    """
    空数据源
    """

    def __init__(self):
        pass

    def total(self):
        return 0

    def reader(self, page_size=100000, offset=0, limit=0, transform_function=None,
               dataset_type='train_set') -> Iterable:
        return self.__Reader()

    class __Reader:
        def __iter__(self):
            return self

        def __next__(self):
            raise StopIteration


DatasetSelector.register_func(DataSourceType.EMPTY, EmptyDataSource, {})
