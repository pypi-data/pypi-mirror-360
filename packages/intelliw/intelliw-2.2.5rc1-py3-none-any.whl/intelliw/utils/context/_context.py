import logging
import time
from copy import deepcopy

from intelliw.utils.intelliwapi import _data_pool_context_storage, _request_header_context_storage, \
    _request_pool_context_storage
from contextvars import copy_context, ContextVar
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial


class _Context:
    def __init__(self, instance: ContextVar):
        self.ctx = instance

    def get(self):
        try:
            return self.ctx.get()
        except LookupError as e:
            raise RuntimeError(
                "You didn't use ContextMiddleware or "
                "you're trying to access `context` object "
                "outside of the request-response cycle."
            ) from e

    def copy_context(self):
        return copy_context()

    def copy_set(self, data):
        return self.ctx.set(
            deepcopy(data)
        )

    def set(self, data):
        return self.ctx.set(
            data
        )

    def exists(self) -> bool:
        return self.ctx in copy_context()


# context = _Context(_data_pool_context_storage)
header_ctx = _Context(_request_header_context_storage)
req_ctx = _Context(_request_pool_context_storage)


class CurrentReq:
    def __init__(self, request=None):
        if req_ctx:
            req_ctx.set(request)

    def __getattr__(self, key):
        return getattr(req_ctx.get(), key)

    def __setattr__(self, key, value):
        req = req_ctx.get()
        setattr(req, key, value)
        req_ctx.set(req)


class ContextThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        ctx = copy_context()
        # 包装目标函数
        super().__init__(target=ctx.run, args=(target, *args), kwargs=kwargs, group=group, name=name, daemon=daemon)


class ContextThreadExecutor:
    def __init__(self, max_workers=None, thread_name_prefix='',
                 initializer=None, initargs=()):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix,
                                           initializer=initializer, initargs=initargs)

    def submit(self, func, *args, **kwargs) -> Future:
        ctx = copy_context()
        return self.executor.submit(ctx.run, partial(func, *args, **kwargs))

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        if timeout is not None:
            end_time = timeout + time.monotonic()

        fs = [self.submit(fn, *args) for args in zip(*iterables)]

        def result_iterator():
            try:
                fs.reverse()
                while fs:
                    if timeout is None:
                        yield fs.pop().result()
                    else:
                        yield fs.pop().result(end_time - time.monotonic())
            finally:
                for future in fs:
                    future.cancel()

        return result_iterator()

    def shutdown(self, wait=True, *args, **kwargs):
        return self.executor.shutdown(wait=wait, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.executor, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()
