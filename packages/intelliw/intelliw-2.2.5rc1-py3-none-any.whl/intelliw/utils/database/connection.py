'''
Author: Hexu
Date: 2022-08-16 10:23:16
LastEditors: Hexu
LastEditTime: 2022-09-27 10:06:25
FilePath: /iw-algo-fx/intelliw/utils/database/connection.py
Description:

数据库连接层，SQLAlchemy的基础上wrap了一层接口，
负责自动管理SQLAlchemy的engine/session/scoped_session的创建，注册与销毁。

一个数据库uri，对应一个engine，一个sessionmaker工厂类，一个scoped_session工厂类
若要获取session/scoped_session对象执行数据库相关的操作，则：

引擎池由该模块进行维护。采用注册机制，通过user + password + host + db构造uri
然后获取一个SQLAlchemy数据库引擎，如果没有引擎则自动创建再返回。
其中，uri为'mysql+pymysql://{user}:{passwd}@{host}'的形式。
'''

import warnings

from sqlalchemy import create_engine as __create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session

warnings.simplefilter('ignore')

# 引擎池，uri -> engine obj
__engines = {}

# sessionmakers工厂类池，engine obj -> sessionmakers
__SessionFactories = {}

# scoped_session工厂类池，engine obj -> scoped_session
__ScopedSessionFactories = {}


def get_engine(driver=None,
               user=None, password=None, host=None, db=None, uri=None,
               charset='utf8', use_cache=True, echo=False) -> Engine:
    """

    Args:
        driver(str): 驱动, e.g.: mysql+pymysql / postgresql+psycopg2 / oracle+cx_oracle
        user(str): 用户名
        password(str): 密码
        host(str): ip或者'localhost'
        db(str or None): 数据库名称
        charset(str): 字符集
        use_cache(bool): 为True时，用完engine记得dispose
        echo(bool): 是否显示sql

    Returns:

    """
    if uri is None:
        uri = '{driver}://{user}:{password}@{host}/'
        uri = uri.format(driver=driver, user=user,
                         password=password, host=host)
        uri += '{}'.format(db) if db else ''
        uri += '?charset={}'.format(charset) if charset else ''
    if use_cache:
        if uri not in __engines:
            __engines[uri] = __create_engine(uri, echo=echo)
        return __engines[uri]
    else:
        return __create_engine(uri, echo=echo)


def get_scoped_session(engine) -> Session:
    """Get a Thread-Local Storage SQLAlchemy session object"""
    return get_scoped_session_factory(engine)()


def get_session(engine) -> Session:
    """Get a non thread-safe SQLAlchemy session"""
    warnings.warn(
        '正在使用一个非线程安全的Session！推荐使用get_scoped_session(engine)函数来获取session。')
    return get_session_factory(engine)()


def get_session_factory(engine):
    if not __SessionFactories.get(engine):
        __SessionFactories[engine] = sessionmaker(bind=engine)
    return __SessionFactories[engine]


def get_scoped_session_factory(engine):
    if not __ScopedSessionFactories.get(engine):
        if not __SessionFactories.get(engine):
            __SessionFactories[engine] = sessionmaker(bind=engine)
        __ScopedSessionFactories[engine] = scoped_session(
            __SessionFactories[engine])
    return __ScopedSessionFactories[engine]
