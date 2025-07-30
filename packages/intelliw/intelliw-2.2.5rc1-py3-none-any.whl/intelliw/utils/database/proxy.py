'''
Author: Hexu
Date: 2022-09-26 13:34:19
LastEditors: Hexu
LastEditTime: 2022-09-26 13:46:59
FilePath: /iw-algo-fx/intelliw/utils/database/proxy.py
Description:

代理模式+装饰器模式实现AOP（面向切面编程）与IOC（控制反转）

目的：非侵入式地给SQLAlchemy的核心类：Session与Query加入横切面，在横切面中可以方便地加入新功能
比如可以扩展增加日志/安全/缓存和事务管理等功能，却不会影响到SQLAlchemy的原生功能。
'''

from sqlalchemy.orm.session import Session


class QueryProxy(object):

    def __init__(self, query):
        self.query = query

    def __getattr__(self, item):
        return getattr(self.query, item)

    def __call__(self, *args, **kwargs):
        return self.query.__call__(*args, **kwargs)


class SessionProxy(object):

    def __init__(self, session, query_proxy_cls=QueryProxy):
        self.session = session
        self.query_proxy_cls = query_proxy_cls

    def __getattr__(self, item):
        if item == 'query':
            query_init_func = self.session.query
            decorated_query_init_func = decorate_query_init_func(
                query_init_func, self.query_proxy_cls)
            return decorated_query_init_func
        else:
            return getattr(self.session, item)


def make_session_proxy(session, session_proxy_cls=SessionProxy, query_proxy_cls=QueryProxy) -> Session:
    """
    这里做了一个Hack。通过代理模式在Session外面wrap一层，
    也能够告诉IDE，返回的对象仍然是Session类，这样的话能够在代理的同时
    还能通过点符号来获取函数补全功能。
    """
    session_proxy: Session = session_proxy_cls(session, query_proxy_cls)
    return session_proxy


def decorate_query_init_func(query_init_func, query_proxy_cls):
    def make_query_proxy(*args, **kwargs):
        query = query_init_func(*args, **kwargs)
        query_proxy = query_proxy_cls(query)
        return query_proxy

    return make_query_proxy
