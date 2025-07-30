'''
Author: hexu
Date: 2021-10-28 19:43:56
LastEditTime: 2021-10-28 19:43:56
LastEditors: your name
Description: 
FilePath: /iw-algo-fx/intelliw/interface/__init__.py
'''
# from intelliw.utils import yms_downloader
from intelliw.utils.env_file_util import read_env_file
from intelliw.utils import yms_downloader_v2 as yms_downloader
# 专属化加载环境变量文件
read_env_file()
yms_downloader.run()

from intelliw.utils.logger import Logger
Logger()
