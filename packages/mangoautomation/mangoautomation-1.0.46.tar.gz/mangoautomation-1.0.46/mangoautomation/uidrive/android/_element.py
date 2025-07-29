# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
import os.path

import time
from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector

from ...exceptions import MangoAutomationError
from ...exceptions._error_msg import ERROR_MSG_0043, ERROR_MSG_0044
from ...tools import Meta
from ...uidrive._base_data import BaseData
from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel


class AndroidElement(metaclass=Meta):
    """元素操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('android', '元素操作', 0, [
        MethodModel(f='locating')])
    def a_click(self, locating: UiObject | XPathSelector):
        """元素单击"""
        locating.click()

    @sync_method_callback('android', '元素操作', 1, [
        MethodModel(f='locating')])
    def a_double_click(self, locating: UiObject):
        """元素双击"""
        locating.click()

    @sync_method_callback('android', '元素操作', 2, [
        MethodModel(f='locating'), MethodModel(f='text', p='请输入内容', d=True)])
    def a_input(self, locating: UiObject, text):
        """单击输入"""
        locating.click()
        self.base_data.android.set_fastinput_ime(True)
        time.sleep(1)
        self.base_data.android.send_keys(text)

    @sync_method_callback('android', '元素操作', 3, [
        MethodModel(f='locating'), MethodModel(f='text', p='请输入内容', d=True)])
    def a_set_text(self, locating: UiObject, text):
        """设置文本"""
        locating.set_text(text)

    @sync_method_callback('android', '元素操作', 4, [
        MethodModel(f='locating'),
        MethodModel(f='x', p='请输入x坐标', d=True),
        MethodModel(f='y', p='请输入y坐标', d=True)])
    def a_click_coord(self, x, y):
        """坐标单击"""
        self.base_data.android.click(x, y)

    @sync_method_callback('android', '元素操作', 5, [
        MethodModel(f='x', p='请输入x坐标', d=True),
        MethodModel(f='y', p='请输入y坐标', d=True)])
    def a_double_click_coord(self, x, y):
        """坐标双击"""
        self.base_data.android.double_click(x, y)

    @sync_method_callback('android', '元素操作', 6, [
        MethodModel(f='locating'),
        MethodModel(f='time_', p='请输入长按坐标时间', d=True)])
    def a_long_click(self, locating: UiObject, time_):
        """长按元素"""
        locating.long_click(duration=float(time_))

    @sync_method_callback('android', '元素操作', 7, [MethodModel(f='locating')])
    def a_clear_text(self, locating: UiObject):
        """清空输入框"""
        locating.clear_text()

    @sync_method_callback('android', '元素操作', 8, [
        MethodModel(f='locating'), MethodModel(f='set_cache_key', p='请输入元素文本存储的key', d=True)])
    def a_get_text(self, locating: UiObject, set_cache_key=None):
        """获取元素文本"""
        value = locating.get_text()
        if set_cache_key:
            self.base_data.test_data.set_cache(key=set_cache_key, value=value)
        return value

    @sync_method_callback('android', '元素操作', 9, [
        MethodModel(f='locating'),
        MethodModel(f='file_name', p='请输入元素截图存储的名称，后续可以通过名称获取', d=True)])
    def a_element_screenshot(self, locating: UiObject, file_name: str):
        """元素截图"""
        im = locating.screenshot()
        file_path = os.path.join(self.base_data.screenshot_path, file_name)
        self.base_data.test_data.set_cache(file_name, file_path)
        im.save(file_path)

    @sync_method_callback('android', '元素操作', 10, [
        MethodModel(f='locating')])
    def a_pinch_in(self, locating: UiObject):
        """元素缩小"""
        locating.pinch_in()

    @sync_method_callback('android', '元素操作', 11, [
        MethodModel(f='locating')])
    def a_pinch_out(self, locating: UiObject):
        """元素放大"""
        locating.pinch_out()

    @sync_method_callback('android', '元素操作', 12, [
        MethodModel(f='locating'), MethodModel(f='time_', p='请输入等待元素出现的时间', d=True)])
    def a_wait(self, locating: UiObject, time_):
        """等待元素出现"""
        if not locating.wait(timeout=float(time_)):
            raise MangoAutomationError(*ERROR_MSG_0043)

    @sync_method_callback('android', '元素操作', 13, [
        MethodModel(f='locating'), MethodModel(f='time_', p='请输入等待元素消失的时间', d=True)])
    def a_wait_gone(self, locating: UiObject, time_: str):
        """等待元素消失"""
        if not locating.wait_gone(timeout=float(time_)):
            raise MangoAutomationError(*ERROR_MSG_0044)

    @sync_method_callback('android', '元素操作', 14, [
        MethodModel(f='locating'), MethodModel(f='locating2')])
    def a_drag_to_ele(self, locating: UiObject, locating2: UiObject):
        """拖动A元素到达B元素上"""
        locating.drag_to(locating2)

    @sync_method_callback('android', '元素操作', 15, [
        MethodModel(f='locating'),
        MethodModel(f='x', p='请输入x坐标', d=True),
        MethodModel(f='y', p='请输入y坐标', d=True)])
    def a_drag_to_coord(self, locating: UiObject, x, y):
        """拖动元素到坐标上"""
        locating.drag_to(x, y)

    @sync_method_callback('android', '元素操作', 16, [MethodModel(f='locating')])
    def a_swipe_right(self, locating: UiObject):
        """元素内向右滑动"""
        locating.swipe('right')

    @sync_method_callback('android', '元素操作', 17, [MethodModel(f='locating')])
    def a_swipe_left(self, locating: UiObject):
        """元素内向左滑动"""
        locating.swipe('left')

    @sync_method_callback('android', '元素操作', 18, [MethodModel(f='locating')])
    def a_swipe_up(self, locating: UiObject):
        """元素内向上滑动"""
        locating.swipe('up')

    @sync_method_callback('android', '元素操作', 19, [MethodModel(f='locating')])
    def a_swipe_ele(self, locating: UiObject):
        """元素内向下滑动"""
        locating.swipe('down')

    @sync_method_callback('android', '元素操作', 20, [
        MethodModel(f='locating'),
        MethodModel(f='x_key', p='请输入x坐标', d=True),
        MethodModel(f='y_key', p='请输入y坐标', d=True)])
    def a_get_center(self, locating: UiObject, x_key, y_key):
        """提取元素坐标"""
        x, y = locating.center()
        if x_key and y_key:
            self.base_data.test_data.set_cache(key=x_key, value=x)
            self.base_data.test_data.set_cache(key=y_key, value=y)
        return x, y
