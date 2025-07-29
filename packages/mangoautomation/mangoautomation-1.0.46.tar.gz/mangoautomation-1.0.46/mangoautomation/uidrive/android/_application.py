# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
import time

from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel
from ...exceptions import MangoAutomationError
from ...exceptions._error_msg import ERROR_MSG_0046
from ...tools import Meta
from ...uidrive._base_data import BaseData


class AndroidApplication(metaclass=Meta):
    """应用操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def is_app_installed(self, package_name: str) -> bool:
        return any(package_name in str(i) for i in self.base_data.android.shell("pm list packages"))

    @sync_method_callback('android', '应用操作', 0,
                          [MethodModel(f='package_name', p='请输入应用名称', d=True)])
    def a_start_app(self, package_name: str):
        """启动应用"""
        if not package_name:
            raise MangoAutomationError(*ERROR_MSG_0046)
        if not self.is_app_installed(package_name):
            raise MangoAutomationError(*ERROR_MSG_0046)
        self.base_data.android.app_start(package_name)
        time.sleep(4)

    @sync_method_callback('android', '应用操作', 1,[
        MethodModel(f='package_name', p='请输入应用名称', d=True)])
    def a_close_app(self, package_name: str):
        """关闭应用"""
        if not package_name:
            raise MangoAutomationError(*ERROR_MSG_0046)
        if not self.is_app_installed(package_name):
            raise MangoAutomationError(*ERROR_MSG_0046)

        self.base_data.android.app_stop(package_name)

    @sync_method_callback('android', '应用操作', 2,[
        MethodModel(f='package_name', p='请输入应用名称', d=True)])
    def a_clear_app(self, package_name: str):
        """清除app数据"""
        if not package_name:
            raise MangoAutomationError(*ERROR_MSG_0046)
        if not self.is_app_installed(package_name):
            raise MangoAutomationError(*ERROR_MSG_0046)

        self.base_data.android.app_clear(package_name)

    @sync_method_callback('android', '应用操作',3 )
    def a_app_stop_all(self):
        """停止所有app"""
        self.base_data.android.app_stop_all()

    @sync_method_callback('android', '应用操作',4, [
        MethodModel(f='package_name', p='请输入应用名称列表', d=True)])
    def a_app_stop_appoint(self, package_name_list: list):
        """停止除指定app外所有app"""
        for i in package_name_list:
            if not self.is_app_installed(i):
                raise MangoAutomationError(*ERROR_MSG_0046)
        self.base_data.android.app_stop_all(excludes=package_name_list)
