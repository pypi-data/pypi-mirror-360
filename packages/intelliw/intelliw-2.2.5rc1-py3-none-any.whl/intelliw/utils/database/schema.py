'''
Author: Hexu
Date: 2022-09-26 13:34:19
LastEditors: Hexu
LastEditTime: 2022-09-26 13:40:13
FilePath: /iw-algo-fx/intelliw/utils/database/schema.py
Description:
'''

from typing import List

from sqlalchemy import Table, Column


class SchemaUtils(object):
    """该类一定要和sqlalchemy.ext.declarative.api.DeclarativeMeta类一起被继承
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> from intelliw.utils.database.schema import SchemaUtils
    >>> Base = declarative_base()
    >>> class ShannonResearchReportFinalDistinct(Base, SchemaUtils):
    >>>     __tablename__ = 'shannon_research_report_final_distinct'
    >>>     desc = '研报去重数据'
    >>>     OBJECT_ID = Column(Integer, primary_key=True)
    >>>     FILEPATH = Column(String(500), doc={'zh': 'OSS路径'})
    >>>     FILENAME = Column(String(500), doc={'zh': '文件名'})
    """

    __table__ = None

    @classmethod
    def table(cls) -> Table:
        """返回这个orm对象对应的SQLAlchemy Table对象"""
        return cls.__table__

    @classmethod
    def tablename(cls) -> str:
        """返回这个orm对象对应数据库里的表名"""
        return str(cls.__table__)

    @classmethod
    def orm_name(cls) -> str:
        """返回这个orm对象对应的ORM类类名"""
        return cls.__name__

    @classmethod
    def columns(cls) -> List[Column]:
        """返回这个orm对象的所有SQLAlchemy Column列对象"""
        return list(cls.table().columns)

    @classmethod
    def column_names(cls) -> List[str]:
        """返回这个orm对象对应数据库里的列名"""
        return [column.name for column in cls.columns()]

    @classmethod
    def get_column(cls, column_name) -> Column or None:
        """返回这个orm对象和column_name同名的SQLAlchemy Column列对象"""
        for column in cls.columns():
            if column.name == column_name:
                return column
        raise ValueError(
            'Cannot find a column with name: {}！'.format(column_name))

    def get_value(self, column_name: str = None, column: Column = None):
        """返回这个orm对象和column_name列的值"""
        return getattr(self, column_name or column.name)

    def get_values(self):
        return [self.get_value(column_name) for column_name in self.column_names()]

    def __repr__(self):
        s = []
        for column_name in self.column_names():
            s.append('[{}={}]'.format(
                column_name, repr(self.get_value(column_name))))
        return '<{} {}>'.format(self.orm_name(), ', '.join(s))
