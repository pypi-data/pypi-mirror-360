import os
import yaml
from intelliw.config import config

key = "iuapaipaas_iwinfer210706".encode('utf-8')
iv = b'iuapaipaas_iwinf'


class AttrDict(dict):
    """Single level attribute dict, NOT recursive"""

    def __init__(self, **kwargs):
        super(AttrDict, self).__init__()
        super(AttrDict, self).update(kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError("object has no attribute '{}'".format(key))


global_config = AttrDict()

READER_KEY = '_READER_'


def load_config(file_path):
    """
    Load config from file.

    Args:
        file_path (str): Path of the config file to be loaded.

    Returns: global config
    """
    _, ext = os.path.splitext(file_path)
    assert ext in ['.yml', '.yaml'], "only support yaml files for now"

    cfg = AttrDict()
    if config.IS_SPECIALIZATION == 2:
        with open(file_path, 'rb') as f:
            text = f.read()
            model = aes_cbc_decrypt(text)
            cfg = merge_config(yaml.load(model, Loader=yaml.Loader), cfg)
    else:
        with open(file_path, 'r', encoding='UTF-8') as f:
            cfg = merge_config(yaml.load(f, Loader=yaml.Loader), cfg)

    if READER_KEY in cfg:
        reader_cfg = cfg[READER_KEY]
        if reader_cfg.startswith("~"):
            reader_cfg = os.path.expanduser(reader_cfg)
        if not reader_cfg.startswith('/'):
            reader_cfg = os.path.join(os.path.dirname(file_path), reader_cfg)

        with open(reader_cfg) as f:
            merge_config(yaml.load(f, Loader=yaml.Loader))
        del cfg[READER_KEY]

    merge_config(cfg)
    return global_config


def load_single_config(file_path):
    _, ext = os.path.splitext(file_path)
    assert ext in ['.yml', '.yaml'], "only support yaml files for now"

    if config.IS_SPECIALIZATION == 2:
        with open(file_path, 'rb') as f:
            text = f.read()
            model = aes_cbc_decrypt(text)
            cfg = yaml.load(model, Loader=yaml.Loader)
    else:
        with open(file_path, 'r', encoding='UTF-8') as f:
            cfg = yaml.load(f, Loader=yaml.Loader)
    return cfg


def dump_config(data, file_path):
    _, ext = os.path.splitext(file_path)
    assert ext in ['.yml', '.yaml'], "only support yaml files for now"

    if config.IS_SPECIALIZATION == 2:
        with open(file_path, 'wb') as f:
            model = yaml.dump(data, default_flow_style=False)
            f.write(model)
    else:
        with open(file_path, 'w', encoding='UTF-8') as f:
            model = yaml.dump(data, default_flow_style=False,
                              allow_unicode=True)
            f.write(model)


def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    Args:
        dct: dict onto which the merge is executed
        merge_dct: dct merged into dct

    Returns: dct
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and
                isinstance(merge_dct[k], dict)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def merge_config(config, another_cfg=None):
    """
    Merge config into global config or another_cfg.

    Args:
        config (dict): Config to be merged.

    Returns: global config
    """
    global global_config
    dct = another_cfg if another_cfg is not None else global_config
    return dict_merge(dct, config)


def aes_cbc_decrypt(text):
    from Crypto.Cipher import AES
    cryptos = AES.new(key, AES.MODE_CBC, iv)
    plain_text = cryptos.decrypt(text)
    # remove ETX (end of text)
    a = bytes.decode(plain_text)
    return remove_ctl(a)


def remove_ctl(input_str):
    result = ''
    for c in input_str:
        ascii_val = ord(c)
        valid_chr_list = [
            9,  # 9=\t=tab
            10,  # 10=\n=LF=Line Feed=换行
            13,  # 13=\r=CR=回车
        ]
        # filter out others ASCII control character, and DEL=delete
        valid_chr = True
        if ascii_val == 0x7F:
            valid_chr = False
        elif (ascii_val < 32) and (ascii_val not in valid_chr_list):
            valid_chr = False

        if valid_chr:
            result += c

    return result
