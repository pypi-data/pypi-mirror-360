# -*- coding:utf-8 -*-

"""
数据公共接口
Date: 2023.05.09
author: wgp
contact: 284250692@qq.com
"""

import json
import requests
import pandas as pd
from functools import partial
from ..common import constant
from ..util import common

class HttpClient:

    def __init__(self, token=''):
        self.basic_url = constant.BASIC_URL
        self.token = token

    """
        调用接口方法，需要token认证
    """
    def query(self, api_name, fields='', **kwargs):
        token = self.token
        if token == '':
            raise Exception(constant.TOKEN_NULL_MSG)
        json_params = {
            'apiName': api_name,
            'fields': fields,
            'params': kwargs
        }
        headers = {
            'Connection': 'close',
            'token': token
        }
        res = requests.post(self.basic_url, json=json_params, timeout=constant.TIME_OUT, headers=headers)
        result = json.loads(res.text)
        code = result['code']
        if code == constant.REQ_SUCCESS_CODE:
            compress_str = result['data']
            data = common.decompress(compress_str)
            return pd.DataFrame(json.loads(data))
        else:
            common.remove_file()
            raise Exception(code, result['msg'])

    def __getattr__(self, name):
        return partial(self.query, name)
