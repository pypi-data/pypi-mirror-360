#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/21 12:31
# @Author  : HEXU
# @File    : utils.py
# @Description :
import hashlib
from intelliw.config import config


def key_builder(func, args, kwargs):
    key, req = None, args[0].infer_request
    use_cache, cache_read, cache_write = True, True, True

    if not req.json and not req.query and not req.form:
        return key, not cache_read, not cache_write

    if isinstance(req.json, dict) and 'use_cache' in req.json:
        use_cache = req.json.pop('use_cache')

    if not use_cache:
        cache_read = False

    key = config.INFER_ID + args[2] + f"{req.json}{req.query}{req.form}"
    key = f"{hashlib.md5(key.encode()).hexdigest()[8:-8]}"
    return key, cache_read, cache_write


def skip_cache_func(result):
    return result[-1] is not None
