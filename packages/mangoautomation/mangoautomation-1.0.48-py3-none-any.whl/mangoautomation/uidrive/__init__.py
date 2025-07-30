# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-07-15 11:57
# @Author : 毛鹏
import sys

from ..uidrive._async_element import AsyncElement
from ..uidrive._base_data import BaseData
from ..uidrive._driver_object import DriverObject
from ..uidrive._sync_element import SyncElement

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = [
    'AsyncElement',
    'BaseData',
    'DriverObject',
    'SyncElement',
]
