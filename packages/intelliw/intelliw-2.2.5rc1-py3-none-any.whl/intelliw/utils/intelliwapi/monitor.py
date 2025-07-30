import asyncio
import os
import subprocess
import time
import threading

from intelliw.config import config
from intelliw.utils import stop_thread
from intelliw.utils.global_val import gl
from intelliw.utils.logger import _get_framework_logger
from intelliw.utils.storage_service import FileTransferDevice, StorageService

logger = _get_framework_logger()


def init_request_data(data):
    # 请求参数校验
    if data.get('requestMode') == "monitor":
        monitorTime = data.get('monitorTime')
        # 请求监控必须要传monitorTime
        if monitorTime is None:
            return {"status": 9, "msg": "MonitorTime cannot be None"}
        if not isinstance(monitorTime, int):
            return {"status": 9, "msg": "MonitorTime must be of int type"}
        # monitorTime大小限制
        if monitorTime < 30 or monitorTime > 30 * 60:
            return {"status": 9, "msg": "The size range of monitorTime should be 30-1800"}
    return None


def monitor_query():
    # 默认返回状态为无监控任务
    response_data = {"status": 0}
    # 任务存在
    if gl.monitor:
        if gl.monitor.get("t").is_alive():
            # 监控线程存活且未超时，返回状态监控中
            if time.time() - gl.monitor.get("start") < 30 * 60:
                response_data = {"status": 1}
            # 监控线程存活且超时，杀掉监控线程，返回状态无任务
            else:
                stop_thread(gl.monitor.get("t"))
        # 监控线程不存活且有url，返回状态已完成
        elif gl.monitor.get("url"):
            response_data = {"status": 2, "url": gl.monitor.get("url")}
    return response_data


def monitor_request(data):
    monitorTime = data.get('monitorTime')
    # 无任务，创建新监控
    if not gl.monitor:
        start_new(monitorTime)
    # 有任务
    else:
        # 监控线程存活且未超时，返回状态监控中（默认）
        if gl.monitor.get("t").is_alive():
            # 监控线程存活且未超时，返回状态监控中（默认）
            if time.time() - gl.monitor.get("start") < 30 * 60:
                logger.info("Monitoring thread exists")
            # 监控线程存活且超时，杀掉监控线程，创建新监控，返回状态监控中（默认）
            else:
                stop_thread(gl.monitor.get("t"))
                start_new(monitorTime)
        # 监控线程不存活，创建新监控，返回状态监控中（默认）
        else:
            start_new(monitorTime)


def start_new(monitorTime):
    file_path = f'./result-{int(time.time())}.svg'
    # 异步上传
    thread = threading.Thread(target=upload_file, args=(file_path, monitorTime))
    thread.start()
    # 返回文件路径
    curKey = os.path.join(config.STORAGE_SERVICE_PATH, config.SERVICE_ID, os.path.basename(file_path))
    downloader = StorageService(key=curKey, process_type="download")

    gl.monitor = {"start": time.time(), "url": downloader.service_url, "t": thread}


def upload_file(file_path, monitorTime):
    """
        生成火焰图并且上传文件
    """
    cmdline = ['py-spy', 'record', '-o', file_path, '-s', '-d', str(monitorTime), '-p', config.MAINPID]
    try:
        subprocess.check_output(cmdline)
    except Exception as e:
        logger.info("堆栈火焰图错误： %s", e)
        pass
    FileTransferDevice(
        file_path, "profile_result", os.path.basename(file_path)
    )
