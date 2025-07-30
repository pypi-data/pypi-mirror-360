# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-29 12:11
# @Author : 毛鹏
from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel
from ....tools import Meta
from ....uidrive._base_data import BaseData


class SyncWebDeviceInput(metaclass=Meta):
    """输入设备"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('web', '输入设备', 0, [
        MethodModel(f='keyboard', p='请输入键盘名称，首字母大写', d=True)])
    def w_keys(self, keyboard: str):
        """模拟按下指定的键"""
        self.base_data.page.keyboard.press(str(keyboard))

    @sync_method_callback('web', '输入设备', 1, [
        MethodModel(f='y', p='请输入向上滚动像素', d=True)])
    def w_wheel(self, y):
        """鼠标上下滚动像素，负数代表向上"""
        self.base_data.page.mouse.wheel(0, y)

    @sync_method_callback('web', '输入设备', 2, [
        MethodModel(f='x', p='请输入点击的x轴', d=True), MethodModel(f='y', p='请输入点击的y轴', d=True)])
    def w_mouse_click(self, x: float, y: float):
        """鼠标点击坐标"""
        self.base_data.page.mouse.click(x, y)

    @sync_method_callback('web', '输入设备', 3)
    def w_mouse_center(self):
        """鼠标移动到中间"""

        viewport_size = self.base_data.page.evaluate('''() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            }
        }''')
        center_x = viewport_size['width'] / 2
        center_y = viewport_size['height'] / 2
        self.base_data.page.mouse.move(center_x, center_y)

    @sync_method_callback('web', '输入设备', 4)
    def w_mouse_center(self):
        """鼠标移动到中间并点击"""

        viewport_size = self.base_data.page.evaluate('''() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            }
        }''')
        center_x = viewport_size['width'] / 2
        center_y = viewport_size['height'] / 2
        self.base_data.page.mouse.click(center_x, center_y)

    @sync_method_callback('web', '输入设备', 5, [MethodModel(f='text', p='请输入键盘输入的内容', d=True)])
    def w_keyboard_type_text(self, text: str):
        """模拟人工输入文字"""
        self.base_data.page.keyboard.type(str(text))

    @sync_method_callback('web', '输入设备', 6, [
        MethodModel(f='text', p='请输入键盘输入的内容', d=True)])
    def w_keyboard_insert_text(self, text: str):
        """直接输入文字"""
        self.base_data.page.keyboard.insert_text(str(text))

    @sync_method_callback('web', '输入设备', 7, [
        MethodModel(f='count', p='请输入要删除字符串的个数', d=True)])
    def w_keyboard_delete_text(self, count: int):
        """删除光标左侧的字符"""
        for _ in range(0, int(count) + 1):
            self.base_data.page.keyboard.press("Backspace")
