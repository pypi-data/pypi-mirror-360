#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/26 15:06
# @Author  : HEXIN
# @File    : cGroup.py.py
# @Description :

# refer from test_004
from pathlib import Path
import subprocess
import argparse
from multiprocessing import Process, cpu_count
import os

CGROUP_ROOT = '/sys/fs/cgroup'
PROCESS_CONTROL_PATH = f'{CGROUP_ROOT}/cpuset/'
GROUP_NAME_TEMPLATE = 'hTest_'


def _argparse():
    """
    get input arguments
    :return: argument object
    """
    parser = argparse.ArgumentParser(description="hexin test")
    parser.add_argument('--total_process_number', action='store', dest='totalProcessNumber', default="2",
                        help='Total number of processes')
    parser.add_argument('--total_thread_number_per_process', action='store', dest='totalThreadNumberPerProcess',
                        default="2", help='Total number of theads per process')
    parser.add_argument('--mprocessing_in_thread', action='store_true', dest='is_mprocessing_in_thread',
                        help='Run multiple process in main thread')

    return parser.parse_args()


def cgroup_maker(group_number: int = 2, thread_pre_group: int = 2, is_run_mp_in_thread: bool = False):
    """
    make cgroup
    """

    def _get_group_list() -> list:

        root: Path = Path(PROCESS_CONTROL_PATH)

        custom_group_list = []
        for _p in root.iterdir():

            if _p.is_dir():
                # TODO debug
                # print(_p)

                # remove parent path
                _p_name = _p.name.replace(PROCESS_CONTROL_PATH, '')

                if _p_name.startswith(GROUP_NAME_TEMPLATE):
                    # filter via name template
                    custom_group_list.append(_p_name)

        # TODO debug
        for _g in custom_group_list:
            print(_g)

        return custom_group_list

    def _remove_exist_groups(group_list: list = []):

        # remove exist groups
        for _g in group_list:
            wrk_path = f'{PROCESS_CONTROL_PATH}{_g}'
            print(f'delete {wrk_path}')

            result = subprocess.run(['rmdir', wrk_path], capture_output=True, text=True)

            if not (result.stderr is None or '' == result.stderr):
                print(result.stderr)

    def _create_new_groups():
        for i in range(group_number):
            # create new group
            _new_group_path = f'{PROCESS_CONTROL_PATH}{GROUP_NAME_TEMPLATE}{i}'
            print(f'creating {_new_group_path}')

            # create folder
            result = subprocess.run(['mkdir', _new_group_path], capture_output=True, text=True)
            if not (result.stderr is None or '' == result.stderr):
                print(result.stderr)

            # specify CPU core
            with open(f'{_new_group_path}/cpuset.cpus', 'w') as f:
                f.write(f'{i * thread_pre_group}-{(i + 1) * thread_pre_group - 1}')
            # specify mem node
            with open(f'{_new_group_path}/cpuset.mems', 'w') as f:
                f.write('0')

            if not is_run_mp_in_thread:
                p = Process(target=deadloop)
                p.start()
                # specify pid
                with open(f'{_new_group_path}/tasks', 'w') as f:
                    f.write(str(p.pid))
            else:
                p = Process(target=sub_process, args=(i, thread_pre_group))
                p.start()

                # TODO debug
                print(f'start sub-process with group id = {i}, pid = {p.pid}')

                # specify pid
                with open(f'{_new_group_path}/cgroup.procs', 'w') as f:
                    f.write(str(p.pid))

    # get exist group list
    exist_group_name_list = _get_group_list()
    # remove old ones
    _remove_exist_groups(exist_group_name_list)
    # create new groups with default template
    _create_new_groups()


def deadloop():
    while True:
        pass


def sub_process(current_group_number: int = 0, thread_pre_group: int = 2):
    _sub_pid = os.getpid()

    for i in range(thread_pre_group):
        p = Process(target=deadloop)
        p.start()
        print(f'Run sub-process in group {current_group_number}, parent pid = {_sub_pid}, local pid = {p.pid}')


if __name__ == '__main__':

    args = _argparse()

    # total process numer
    total_process_number = int(args.totalProcessNumber)
    # total thread numer per process
    total_thread_number_per_process = int(args.totalThreadNumberPerProcess)
    # run multiple process in main thread
    is_mprocessing_in_thread = args.is_mprocessing_in_thread

    # verify
    if total_process_number * total_thread_number_per_process > cpu_count():
        raise ValueError(f'invalid process and thread number')

    cgroup_maker(total_process_number, total_thread_number_per_process, is_mprocessing_in_thread)
