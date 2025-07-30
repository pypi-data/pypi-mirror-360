#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/22 16:38
# @Author  : HEXU
# @File    : common.py
# @Description :


mode_set = {'single', 'sentinel', 'cluster'}


def check_mode(mode: str):
    return mode.lower() in mode_set
