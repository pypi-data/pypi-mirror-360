# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-15 11:54
# @Author : 毛鹏
import sys

from ..tools._mate import Meta
from ..tools._uiautodev import start_uiautodev, stop_uiautodev

python_version = sys.version_info
if f"{python_version.major}.{python_version.minor}" != "3.10":
    raise Exception("必须使用>Python3.10.4")
__all__ = ['Meta', 'start_uiautodev', 'stop_uiautodev']
