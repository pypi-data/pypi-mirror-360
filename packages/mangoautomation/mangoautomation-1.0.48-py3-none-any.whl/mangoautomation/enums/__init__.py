# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-04-29 11:23
# @Author : 毛鹏
import sys

from ..enums._ui_enum import ElementExpEnum, ElementOperationEnum, DeviceEnum, BrowserTypeEnum, DriveTypeEnum

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = [
    'ElementOperationEnum',
    'DeviceEnum',
    'BrowserTypeEnum',
    'DriveTypeEnum',
    'ElementExpEnum',
]
