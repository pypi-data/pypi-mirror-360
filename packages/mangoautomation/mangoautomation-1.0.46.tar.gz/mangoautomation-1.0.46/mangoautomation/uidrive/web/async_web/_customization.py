# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-26 22:22
# @Author : 毛鹏

from ....tools import Meta
from ..._base_data import BaseData


class AsyncWebCustomization(metaclass=Meta):
    """定制开发"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data
