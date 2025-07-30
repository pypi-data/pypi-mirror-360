

from .common.credit import auth
from .api import data_api as da

"""
    python内置函数，可以用来获取一个对象的属性值或方法
"""

def __getattr__(method_name):
    ta = da.goco_api()
    return getattr(ta, method_name)






