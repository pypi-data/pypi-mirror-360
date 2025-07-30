# -*- coding:utf-8 -*-

"""
数据公共接口
Date: 2023.05.09
author: wgp
contact: 284250692@qq.com
"""

import base64
import gzip
import os
from ..common import constant

user_path = os.path.expanduser('~')


"""
    字符串解压
"""
def decompress(compressed_str):
    try:
        compressed_bytes = base64.b64decode(compressed_str)
        decompressed_bytes = gzip.decompress(compressed_bytes)
        return decompressed_bytes.decode('utf-8')
    except Exception as e:
        print(e)
        return None


"""
    获取凭证的路径
"""
def get_op():
    return os.path.join(user_path, constant.USER_TOKEN_CN)


"""
    获取凭证的路径
"""
def get_path():
    return user_path + constant.SEPARATOR + constant.USER_TOKEN_CN


"""
    检查文件路径是否存在
"""
def check_exist(path):
    return os.path.exists(path)


"""
    删除文件
"""
def remove_file():
    path = get_path()
    if os.path.exists(path):
        os.remove(path)
