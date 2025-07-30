# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023/4/6 13:31
# @Author : 毛鹏
import os.path

from uiautomator2 import Direction

from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel
from ...tools import Meta
from ...uidrive._base_data import BaseData


class AndroidPage(metaclass=Meta):
    """页面操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('android', '页面操作', 1)
    def a_swipe_right(self):
        """右滑"""
        self.base_data.android.swipe_ext(Direction.HORIZ_FORWARD)

    @sync_method_callback('android', '页面操作', 2)
    def a_swipe_left(self):
        """左滑"""
        self.base_data.android.swipe_ext(Direction.HORIZ_BACKWARD)

    @sync_method_callback('android', '页面操作', 3)
    def a_swipe_up(self):
        """上滑"""
        self.base_data.android.swipe_ext(Direction.FORWARD)

    @sync_method_callback('android', '页面操作', 4)
    def a_swipe_down(self):
        """下滑"""
        self.base_data.android.swipe_ext(Direction.BACKWARD)

    @sync_method_callback('android', '页面操作', 5, [
        MethodModel(f='sx', p='请输入sx坐标', d=True),
        MethodModel(f='sy', p='请输入sy坐标', d=True),
        MethodModel(f='ex', p='请输入ex坐标', d=True),
        MethodModel(f='ey', p='请输入ey坐标', d=True)])
    def a_swipe(self, sx, sy, ex, ey):
        """坐标滑动"""
        self.base_data.android.swipe(sx, sy, ex, ey, 0.5)

    @sync_method_callback('android', '页面操作', 6, [
        MethodModel(f='sx', p='请输入sx坐标', d=True),
        MethodModel(f='sy', p='请输入sy坐标', d=True),
        MethodModel(f='ex', p='请输入ex坐标', d=True),
        MethodModel(f='ey', p='请输入ey坐标', d=True)])
    def a_drag(self, sx, sy, ex, ey):
        """坐标拖动"""
        self.base_data.android.drag(sx, sy, ex, ey, 0.5)

    @sync_method_callback('android', '页面操作', 7)
    def a_open_quick_settings(self):
        """打开快速通知"""
        self.base_data.android.open_quick_settings()

    @sync_method_callback('android', '页面操作', 8, [
        MethodModel(f='file_name', p='请输入截图文件名称', d=True)])
    def a_screenshot(self, file_name: str):
        """屏幕截图"""
        self.base_data.android.screenshot(filename=os.path.join(self.base_data.screenshot_path, file_name))

    @sync_method_callback('android', '页面操作', 9, [
        MethodModel(f='x', p='请输入按下的x坐标', d=True),
        MethodModel(f='y', p='请输入按下的x坐标', d=True),
        MethodModel(f='time_', p='请输入长按时间', d=True)])
    def a_long_click(self, x, y, time_):
        """长按屏幕N秒"""
        self.base_data.android.long_click(x, y, time_)

    @sync_method_callback('android', '页面操作', 10)
    def a_set_orientation_natural(self):
        """设置为natural"""
        self.base_data.android.set_orientation("natural")

    @sync_method_callback('android', '页面操作', 11)
    def a_set_orientation_left(self):
        """设置为natural"""
        self.base_data.android.set_orientation("left")

    @sync_method_callback('android', '页面操作', 12)
    def a_set_orientation_right(self):
        """设置为right"""
        self.base_data.android.set_orientation("right")

    @sync_method_callback('android', '页面操作', 13)
    def a_set_orientation_upsidedown(self):
        """设置为upsidedown"""
        self.base_data.android.set_orientation("upsidedown")

    @sync_method_callback('android', '页面操作', 14)
    def a_freeze_rotation(self):
        """冻结旋转"""
        self.base_data.android.freeze_rotation()

    @sync_method_callback('android', '页面操作', 15)
    def a_freeze_rotation_false(self):
        """取消冻结旋转"""
        self.base_data.android.freeze_rotation(False)

    @sync_method_callback('android', '页面操作', 16)
    def a_dump_hierarchy(self):
        """获取转储的内容"""
        return self.base_data.android.dump_hierarchy()

    @sync_method_callback('android', '页面操作', 17)
    def a_open_notification(self):
        """打开通知"""
        return self.base_data.android.dump_hierarchy()
