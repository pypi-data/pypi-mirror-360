# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-26 22:22
# @Author : 毛鹏
import asyncio
import os

import time
from mangotools.decorator import async_method_callback
from mangotools.models import MethodModel
from playwright.async_api import Locator, Error

from ..._base_data import BaseData
from ....exceptions import MangoAutomationError
from ....exceptions._error_msg import ERROR_MSG_0024, ERROR_MSG_0056
from ....tools import Meta


class AsyncWebElement(metaclass=Meta):
    """元素操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @async_method_callback('web', '元素操作', 0, [MethodModel(f='locating')])
    async def w_click(self, locating: Locator):
        """元素单击"""
        await locating.click()

    @async_method_callback('web', '元素操作', 1, [MethodModel(f='locating')])
    async def w_dblclick(self, locating: Locator):
        """元素双击"""
        await locating.dblclick()

    @async_method_callback('web', '元素操作', 2, [MethodModel(f='locating')])
    async def w_force_click(self, locating: Locator):
        """强制单击"""
        await locating.evaluate('element => element.click()')

    @async_method_callback('web', '元素操作', 3, [
        MethodModel(f='locating'),
        MethodModel(f='input_value', p='请输入输入内容', d=True)])
    async def w_input(self, locating: Locator, input_value: str):
        """元素输入"""
        await locating.fill(str(input_value))

    @async_method_callback('web', '元素操作', 4, [MethodModel(f='locating')])
    async def w_hover(self, locating: Locator):
        """鼠标悬停"""
        await locating.hover()
        await asyncio.sleep(1)

    @async_method_callback('web', '元素操作', 5, [
        MethodModel(f='locating'),
        MethodModel(f='set_cache_key', p='请输入获取元素文本后存储的key', d=True)])
    async def w_get_text(self, locating: Locator, set_cache_key=None):
        """获取元素文本"""
        value = await locating.inner_text()
        if set_cache_key:
            self.base_data.test_data.set_cache(key=set_cache_key, value=value)
        return value

    @async_method_callback('web', '元素操作', 5, [
        MethodModel(f='locating'),
        MethodModel(f='input_value', p='请输入输入内容', d=True)])
    async def w_clear_input(self, locating: Locator, input_value: str):
        """元素清空再输入"""
        await locating.clear()
        await locating.fill(str(input_value))

    @async_method_callback('web', '元素操作', 6, [MethodModel(f='locating')])
    async def w_many_click(self, locating: Locator):
        """多元素循环单击"""
        await asyncio.sleep(1)
        elements = await locating.all()
        for element in elements:
            await element.click()

    @async_method_callback('web', '元素操作', 6, [
        MethodModel(f='locating'),
        MethodModel(f='file_path', p='请输入文件路径，参照帮助文档', d=True)])
    async def w_upload_files(self, locating: Locator, file_path: str | list):
        """拖拽文件上传"""
        try:
            if isinstance(file_path, str):
                await locating.set_input_files(file_path)
            else:
                for file in file_path:
                    await locating.set_input_files(file)
        except Error:
            raise MangoAutomationError(*ERROR_MSG_0024)

    @async_method_callback('web', '元素操作', 7, [
        MethodModel(f='locating'),
        MethodModel(f='file_path', p='请输入文件路径，参照帮助文档', d=True)])
    async def w_click_upload_files(self, locating: Locator, file_path: str | list):
        """点击并选择文件上传"""
        async with self.base_data.page.expect_file_chooser() as fc_info:
            await locating.click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)

    @async_method_callback('web', '元素操作', 8, [
        MethodModel(f='locating'),
        MethodModel(f='file_key', p='请输入文件存储路径的key，后续通过key获取文件保存的绝对路径', d=True)])
    async def w_download(self, locating: Locator, file_key: str):
        """下载文件"""
        async with self.base_data.page.expect_download() as download_info:
            await locating.click()
        download = await download_info.value
        file_name = download.suggested_filename
        save_path = os.path.join(self.base_data.download_path, file_name)
        await download.save_as(save_path)
        self.base_data.test_data.set_cache(file_key, file_name)

    @async_method_callback('web', '元素操作', 9, [
        MethodModel(f='locating')])
    async def w_element_wheel(self, locating: Locator):
        """滚动到元素位置"""
        await locating.scroll_into_view_if_needed()

    @async_method_callback('web', '元素操作', 9, [MethodModel(f='locating')])
    async def w_right_click(self, locating: Locator):
        """元素右键点击"""
        await locating.click(button='right')

    @async_method_callback('web', '元素操作', 10, [
        MethodModel(f='locating'),
        MethodModel(f='n', p='请输入循环点击的时间', d=True)])
    async def w_time_click(self, locating: Locator, n: int):
        """循环点击N秒"""
        try:
            n = int(n)
        except ValueError:
            raise MangoAutomationError(*ERROR_MSG_0056)
        s = time.time()
        while True:
            await locating.click()
            if time.time() - s > n:
                return

    @async_method_callback('web', '元素操作', 11, [
        MethodModel(f='locating'),
        MethodModel(f='n', p='请输入向上像素', d=True)])
    async def w_drag_up_pixel(self, locating: Locator, n: int):
        """往上拖动N个像素"""
        try:
            n = int(n)
        except ValueError:
            raise MangoAutomationError(*ERROR_MSG_0056)

        box = await locating.bounding_box()

        if box:
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.down()
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2 - n)
            await self.base_data.page.mouse.up()

    @async_method_callback('web', '元素操作', 12, [
        MethodModel(f='locating'),
        MethodModel(f='n', p='请输入向下像素', d=True)])
    async def w_drag_down_pixel(self, locating: Locator, n: int):
        """往下拖动N个像素"""
        try:
            n = int(n)
        except ValueError:
            raise MangoAutomationError(*ERROR_MSG_0056)

        box = await locating.bounding_box()

        if box:
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.down()
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2 + n)
            await self.base_data.page.mouse.up()

    @async_method_callback('web', '元素操作', 13, [
        MethodModel(f='locating'),
        MethodModel(f='n', p='请输入向左像素', d=True)])
    async def w_drag_left_pixel(self, locating: Locator, n: int):
        """往左拖动N个像素"""
        try:
            n = int(n)
        except ValueError:
            raise MangoAutomationError(*ERROR_MSG_0056)

        box = await locating.bounding_box()

        if box:
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.down()
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2 - n, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.up()

    @async_method_callback('web', '元素操作', 14, [
        MethodModel(f='locating'),
        MethodModel(f='n', p='请输入向右像素', d=True)])
    async def w_drag_right_pixel(self, locating: Locator, n: int):
        """往右拖动N个像素"""
        try:
            n = int(n)
        except ValueError:
            raise MangoAutomationError(*ERROR_MSG_0056)
        box = await locating.bounding_box()

        if box:
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.down()
            await self.base_data.page.mouse.move(box['x'] + box['width'] / 2 + n, box['y'] + box['height'] / 2)
            await self.base_data.page.mouse.up()

    @async_method_callback('web', '元素操作', 15, [
        MethodModel(f='locating'),
        MethodModel(f='path', p='请输入截图保存路径', d=True)])
    async def w_ele_screenshot(self, locating: Locator, path: str):
        """元素截图"""
        await locating.screenshot(path=path)

    @async_method_callback('web', '元素操作', 20, [
        MethodModel(f='locating1'),
        MethodModel(f='locating2')])
    async def w_drag_to(self, locating1: Locator, locating2: Locator):
        """拖动A元素到达B"""
        await locating1.drag_to(locating2)
