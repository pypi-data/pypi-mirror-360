# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-10 21:37
# @Author : 毛鹏
class Meta(type):

    def __new__(cls, name, bases, attrs, **kwargs):
        methods = kwargs.pop('methods', {})
        for method_name, method_func in methods.items():
            attrs[method_name] = method_func
        return super().__new__(cls, name, bases, attrs)
