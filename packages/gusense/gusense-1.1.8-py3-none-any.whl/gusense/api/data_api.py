# -*- coding:utf-8 -*-

"""
Date: 2023.05.09
author: wgp
contact: 284250692@qq.com
"""

from ..api import client
from ..common import constant
from ..common.credit import get_token

"""
    获取调用接口实现类
"""
def goco_api():
    token = get_token()
    if token is None or token == '':
        raise Exception(constant.TOKEN_NULL_MSG)
    else:
        return client.HttpClient(token=token)
