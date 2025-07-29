# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 03-09-09 3:17
# @Author : 毛鹏
from time import sleep

from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel
from ...tools import Meta
from ...uidrive._base_data import BaseData


class AndroidEquipment(metaclass=Meta):
    """设备操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('android', '设备操作', 1, [
        MethodModel(f='_time', p='请输入等待时间', d=True)])
    def a_sleep(self, time_: int):
        """强制等待"""
        sleep(time_)

    @sync_method_callback('android', '设备操作', 2)
    def a_screen_on(self):
        """打开屏幕"""
        self.base_data.android.screen_on()
        self.a_sleep(1)

    @sync_method_callback('android', '设备操作', 3)
    def a_screen_off(self):
        """关闭屏幕"""
        self.base_data.android.screen_off()
        self.a_sleep(1)

    @sync_method_callback('android', '设备操作', 4)
    def a_swipe_left(self):
        """获取屏幕开关状态"""
        self.base_data.android.info.get('screenOn')

    @sync_method_callback('android', '设备操作', 5)
    def a_get_window_size(self):
        """提取屏幕尺寸"""
        w, h = self.base_data.android.window_size()
        return w, h

    @sync_method_callback('android', '设备操作', 6, [
        MethodModel(f='feli_path', p='请输入计算机文件路径', d=True),
        MethodModel(f='catalogue', p='请输入设备目录', d=True)])
    def a_push(self, feli_path, catalogue):
        """推送一个文件到设备"""
        self.base_data.android.push(feli_path, catalogue)

    @sync_method_callback('android', '设备操作', 7, [
        MethodModel(f='feli_path', p='请输入设备文件路径', d=True),
        MethodModel(f='catalogue', p='请输入计算机目录', d=True)])
    def a_pull(self, feli_path, catalogue):
        """提取文件"""
        self.base_data.android.pull(feli_path, catalogue)

    @sync_method_callback('android', '设备操作', 8)
    def a_unlock(self):
        """解锁屏幕"""
        self.base_data.android.unlock()

    @sync_method_callback('android', '设备操作', 9)
    def a_press_home(self):
        """按home键"""
        self.base_data.android.press('home')

    @sync_method_callback('android', '设备操作', 10)
    def a_press_back(self):
        """按back键"""
        self.base_data.android.press('back')

    @sync_method_callback('android', '设备操作', 11)
    def a_press_left(self):
        """按left键"""
        self.base_data.android.press('left')

    @sync_method_callback('android', '设备操作', 12)
    def a_press_right(self):
        """按right键"""
        self.base_data.android.press('right')

    @sync_method_callback('android', '设备操作', 13)
    def a_press_up(self):
        """按up键"""
        self.base_data.android.press('up')

    @sync_method_callback('android', '设备操作', 14)
    def a_press_down(self):
        """按down键"""
        self.base_data.android.press('down')

    @sync_method_callback('android', '设备操作', 15)
    def a_press_center(self):
        """按center键"""
        self.base_data.android.press('center')

    @sync_method_callback('android', '设备操作', 16)
    def a_press_menu(self):
        """按menu键"""
        self.base_data.android.press('menu')

    @sync_method_callback('android', '设备操作', 17)
    def a_press_search(self):
        """按search键"""
        self.base_data.android.press('search')

    @sync_method_callback('android', '设备操作', 18)
    def a_press_enter(self):
        """按enter键"""
        self.base_data.android.press('enter')

    @sync_method_callback('android', '设备操作', 19)
    def a_press_delete(self):
        """按delete键"""
        self.base_data.android.press('delete')

    @sync_method_callback('android', '设备操作', 20)
    def a_press_recent(self):
        """按recent键"""
        self.base_data.android.press('recent')

    @sync_method_callback('android', '设备操作', 21)
    def a_press_volume_up(self):
        """按volume_up键"""
        self.base_data.android.press('volume_up')

    @sync_method_callback('android', '设备操作', 22)
    def a_press_volume_down(self):
        """按volume_down键"""
        self.base_data.android.press('volume_down')

    @sync_method_callback('android', '设备操作', 23)
    def a_press_volume_mute(self):
        """按volume_mute键"""
        self.base_data.android.press('volume_mute')

    @sync_method_callback('android', '设备操作', 24)
    def a_press_camera(self):
        """按camera键"""
        self.base_data.android.press('camera')

    @sync_method_callback('android', '设备操作', 25)
    def a_press_power(self):
        """按power键"""
        self.base_data.android.press('power')
