import io
import os
import sys
import tempfile
import time
from functools import wraps
import cProfile
import pstats

from intelliw.utils.storage_service import StorageService, FileTransferDevice
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


def _pre():
    logger.warning("performance profile request...")
    pr = cProfile.Profile()
    pr.enable()
    return pr


def _post(pr):
    pr.disable()
    with io.StringIO() as s:
        sort_by = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sort_by)
        ps.print_stats()
        profile = s.getvalue()

    logger.warning(f"\n{profile}")

    """
    上传云服务， 通过
    >>> flameprof pipeline.prof > pipeline.svg
    查看火焰图
    """
    with tempfile.NamedTemporaryFile() as tmp:
        tmp_file = tmp.name + '.prof'
        pr.dump_stats(tmp_file)
        fd = FileTransferDevice(
            tmp_file, "profile_result", filename=f"result-{int(time.time())}.prof"
        )
    raw_stats = fd.curkey
    return profile, raw_stats


async def async_performance_profile(func, *args, **kwargs):
    pr = _pre()
    result = await func(*args, **kwargs)
    profile, raw_stats = _post(pr)
    return {"result": result, "profile": profile, "raw_stats": raw_stats}


def performance_profile(func, *args, **kwargs):
    pr = _pre()
    result = func(*args, **kwargs)
    profile, raw_stats = _post(pr)
    return {"result": result, "profile": profile, "raw_stats": raw_stats}


def performance_profile_wrapper(filepath=None):
    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            pr = _pre()
            result = function(*args, **kwargs)
            profile, raw_stats = _post(pr)
            return {"result": result, "profile": profile, "raw_stats": raw_stats}

        return inner

    return wrapper
