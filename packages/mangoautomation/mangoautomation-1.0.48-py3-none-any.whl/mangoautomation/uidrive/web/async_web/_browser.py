# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-04-25 22:33
# @Author : 毛鹏
import asyncio
import json
import os.path
import traceback
from urllib.parse import urlparse

from playwright._impl._errors import TimeoutError, Error, TargetClosedError

from mangotools.decorator import async_method_callback
from mangotools.models import MethodModel
from ..._base_data import BaseData
from ....exceptions import MangoAutomationError
from ....exceptions._error_msg import ERROR_MSG_0049, ERROR_MSG_0013, ERROR_MSG_0058, ERROR_MSG_0059, ERROR_MSG_0010
from ....tools import Meta


class AsyncWebBrowser(metaclass=Meta):
    """浏览器操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @async_method_callback('web', '浏览器操作', 0, [
        MethodModel(f='_time', p='请输入等待时间', d=True)])
    async def w_wait_for_timeout(self, _time: int):
        """强制等待"""
        await asyncio.sleep(int(_time))

    @async_method_callback('web', '浏览器操作', 1, [
        MethodModel(f='url', p='请输入URL', d=True)])
    async def w_goto(self, url: str):
        """打开URL"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise MangoAutomationError(*ERROR_MSG_0049)
            await self.base_data.page.goto(url, timeout=60000)
            await asyncio.sleep(2)
        except TimeoutError as error:
            self.base_data.log.debug(f'打开URL失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0013, value=(url,))
        except TargetClosedError as error:
            self.base_data.setup()
            self.base_data.log.debug(f'打开URL失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0010, value=(url,))
        except Error as error:
            self.base_data.log.debug(
                f'打开URL失败-2，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            raise MangoAutomationError(*ERROR_MSG_0058, value=(url,))

    @async_method_callback('web', '浏览器操作', 2, [
        MethodModel(f='path', p='请输入截图保存路径', d=True)])
    async def w_screenshot(self, path: str):
        """整个页面截图"""
        try:
            await self.base_data.page.screenshot(path=path, full_page=True)
        except (TargetClosedError, TimeoutError) as error:
            self.base_data.log.debug(
                f'截图出现异常失败-1，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            self.base_data.setup()
            raise MangoAutomationError(*ERROR_MSG_0010)
        except AttributeError as error:
            self.base_data.log.debug(
                f'截图出现异常失败-2，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            self.base_data.setup()
            raise MangoAutomationError(*ERROR_MSG_0010)

    @async_method_callback('web', '浏览器操作', 3)
    async def w_alert(self):
        """设置弹窗不予处理"""
        self.base_data.page.on("dialog", lambda dialog: dialog.accept())

    @async_method_callback('web', '浏览器操作', 4)
    async def w_get_cookie(self):
        """获取cookie"""
        with open(os.path.join(self.base_data.download_path, 'storage_state.json'), 'w') as file:
            file.write(json.dumps(await self.base_data.context.storage_state()))

    @async_method_callback('web', '浏览器操作', 5, [
        MethodModel(f='storage_state', p='请输入获取cookie方法中获取的内容', d=True)])
    async def w_set_cookie(self, storage_state: str):
        """设置cookie"""
        if isinstance(storage_state, str):
            storage_state = json.loads(storage_state)
        else:
            raise MangoAutomationError(*ERROR_MSG_0059)
        await self.base_data.context.add_cookies(storage_state['cookies'])
        for storage in storage_state['origins']:
            local_storage = storage.get('localStorage', [])
            session_storage = storage.get('sessionStorage', [])
            for item in local_storage:
                await self.base_data.context.add_init_script(
                    f"window.localStorage.setItem('{item['name']}', '{item['value']}');")
            for item in session_storage:
                await self.base_data.context.add_init_script(
                    f"window.sessionStorage.setItem('{item['name']}', '{item['value']}');")
        await self.base_data.page.reload()

    @async_method_callback('web', '浏览器操作', 6)
    async def w_clear_cookies(self):
        """清除所有cookie"""
        await self.base_data.context.clear_cookies()

    @async_method_callback('web', '浏览器操作', 7)
    async def w_clear_storage(self):
        """清除本地存储和会话存储"""
        await self.base_data.page.evaluate("() => localStorage.clear()")
        await self.base_data.page.evaluate("() => sessionStorage.clear()")
