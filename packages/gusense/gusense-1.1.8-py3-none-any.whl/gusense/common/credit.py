# -*- coding:utf-8 -*-

"""
用户认证
Date: 2023.05.09
author: wgp
contact: 284250692@qq.com
"""

import json
import pandas as pd
import requests
from ..common import constant
from ..util import common

"""
    用户认证方法，开发者ID和密匙来源Gusense数据中心
"""
def auth(app_id, app_secret):
    token = get_token(app_id, app_secret)
    if token is None or token == '':
        params = {
            "appId": app_id,
            "appSecret": app_secret
        }
        res = requests.post(constant.LOGIN_URL, params=params, timeout=constant.TIME_OUT)
        json_res = json.loads(res.text)
        code = json_res['code']
        if code == constant.REQ_SUCCESS_CODE:
            token = json_res['data']
            df = pd.DataFrame([[app_id, app_secret, token]], columns=['app_id', 'app_secret', 'token'])
            op = common.get_op()
            df.to_csv(op, index=False)
        else:
            common.remove_file()
            msg = json_res['msg']
            raise Exception(msg)


"""
    获取token的方法
"""
def get_token(app_id=None, app_secret=None):
    credit_list = get_credit_list()
    if credit_list is None:
        return None
    if app_id is not None and app_secret is not None:
        oai = credit_list['app_id']  # 填写的与文件中的不相等，则重新登录
        oas = credit_list['app_secret']
        if app_id != oai:
            return None
        if app_secret != oas:
            return None
    return credit_list['token']


"""
    从csv文件中获取凭证信息
"""
def get_credit_list():
    op = common.get_op()
    if common.check_exist(op):
        df = pd.read_csv(op)
        credit_list = df.loc[0]
        return credit_list
    else:
        return None
