'''
Author: Hexu
Date: 2022-04-08 17:13:36
LastEditors: Hexu
LastEditTime: 2022-09-16 16:43:37
FilePath: /iw-algo-fx/intelliw/functions/__init__.py
Description:  init
'''
from intelliw.functions.general import convert_data
from intelliw.functions.select_columns import select_columns
from intelliw.functions.data_filtering import filter_by_condition


class Const:
    split_function_list = ["convert_data",
                           "select_columns", "filter_by_condition"]
    feature_process = "feature_process"
    feature_process_param = "feature_process_param"
    timeseries_process = "timeseries_process"
    timeseries_param = "timeseries_param"
    timeseries_group_param = "group_param"
