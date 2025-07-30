# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-04 21:42
# @Author : 毛鹏
import re
import traceback

from playwright._impl._errors import TimeoutError, Error
from playwright.async_api._generated import Locator

from mangotools.assertion import MangoAssertion
from mangotools.enums import StatusEnum
from mangotools.mangos import Mango
from ....enums import ElementExpEnum, ElementOperationEnum
from ....exceptions import MangoAutomationError
from ....exceptions._error_msg import *
from ....uidrive._base_data import BaseData
from ....uidrive.web.async_web._assertion import AsyncWebAssertion
from ....uidrive.web.async_web._browser import AsyncWebBrowser
from ....uidrive.web.async_web._customization import AsyncWebCustomization
from ....uidrive.web.async_web._element import AsyncWebElement
from ....uidrive.web.async_web._input_device import AsyncWebDeviceInput
from ....uidrive.web.async_web._page import AsyncWebPage

re = re
__all__ = [
    'AsyncWebPage',
    'AsyncWebElement',
    'AsyncWebDeviceInput',
    'AsyncWebCustomization',
    'AsyncWebBrowser',
    'AsyncWebAssertion',
    'AsyncWebDevice',
]


class AsyncWebDevice(AsyncWebBrowser,
                     AsyncWebPage,
                     AsyncWebElement,
                     AsyncWebDeviceInput,
                     AsyncWebCustomization):

    def __init__(self, base_data: BaseData):
        super().__init__(base_data)

    async def open_url(self, is_open: bool = False):
        if not self.base_data.is_open_url or is_open:
            self.base_data.log.debug(f'打开url，is_open_url：{self.base_data.is_open_url},url:{self.base_data.url}')
            await self.w_goto(self.base_data.url)
            self.base_data.is_open_url = True

    async def web_action_element(self, name, ope_key, ope_value, ):
        self.base_data.log.debug(f'操作元素，名称：{name},key:{ope_key},value:{ope_value}')
        try:
            await Mango.a_e(self, ope_key, ope_value)
        except TimeoutError as error:
            self.base_data.log.error(f'WEB自动化操作失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0011, value=(name,))
        except Error as error:
            self.base_data.log.error(f'WEB自动化操作失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0032, value=(name,))
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化操作失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0012)

    async def web_assertion_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'断言元素，名称：{name},key:{ope_key},value:{ope_value}')
        is_method = callable(getattr(AsyncWebAssertion, ope_key, None))
        try:
            if is_method:
                if ope_value.get('actual', None) is None:
                    traceback.print_exc()
                    raise MangoAutomationError(*ERROR_MSG_0031, value=(name,))
                self.base_data.log.debug(f'开始断言-1，方法：{ope_key}，断言值：{ope_value}')
                await Mango.a_e(AsyncWebAssertion(self.base_data), ope_key, ope_value)
            else:
                self.base_data.log.debug(f'开始断言-2，方法：{ope_key}，断言值：{ope_value}')
                MangoAssertion(self.base_data.mysql_connect).ass(ope_key, ope_value.get('actual'), ope_value.get('expect'))
        except AssertionError as error:
            self.base_data.log.debug(f'WEB自动化断言失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0017, value=error.args)
        except AttributeError as error:
            self.base_data.log.error(f'WEB自动化断言失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0048)
        except ValueError as error:
            self.base_data.log.error(f'WEB自动化断言失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0005)

        except Error as error:
            self.base_data.log.error(f'WEB自动化断言失败-4，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0052, value=(name,), )

    async def web_find_ele(self, name, _type, exp, loc, sub, is_iframe) \
            -> tuple[Locator, int, str] | tuple[list[Locator], int, str]:
        self.base_data.log.debug(
            f'查找元素，名称：{name},_type:{_type},exp:{exp},loc:{loc},sub:{sub},is_iframe:{is_iframe}')
        if is_iframe != StatusEnum.SUCCESS.value:
            locator: Locator = await self.__find_ele(self.base_data.page, exp, loc)
            try:
                count = await locator.count()
                loc = locator.nth(sub - 1) if sub else locator
                try:
                    text = await self.w_get_text(loc)
                except Exception:
                    text = None
                return loc, count, text
            except Error as error:
                self.base_data.log.debug(
                    f'WEB自动化查找元素失败-1，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
                raise MangoAutomationError(*ERROR_MSG_0041, value=(name, loc))
        else:
            ele_list: list[Locator] = []
            for i in self.base_data.page.frames:
                locator: Locator = await self.__find_ele(i, exp, loc)
                try:
                    count = await locator.count()
                except Error as error:
                    self.base_data.log.debug(
                        f'WEB自动化查找元素失败-2，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
                    raise MangoAutomationError(*ERROR_MSG_0041, )
                if count > 0:
                    for nth in range(0, count):
                        ele_list.append(locator.nth(nth))
                else:
                    raise MangoAutomationError(*ERROR_MSG_0023)
            if not ele_list:
                raise MangoAutomationError(*ERROR_MSG_0023)
            if not ele_list and _type == ElementOperationEnum.OPE.value:
                raise MangoAutomationError(*ERROR_MSG_0029, value=(name, loc))
            try:
                count = len(ele_list)
                loc = ele_list[sub - 1] if sub else ele_list
                try:
                    text = await self.w_get_text(loc)
                except Exception:
                    text = None
                return loc, count, text
            except IndexError:
                raise MangoAutomationError(*ERROR_MSG_0025, value=(len(ele_list),))

    async def __find_ele(self, page, exp, loc) -> Locator:
        match exp:
            case ElementExpEnum.LOCATOR.value:
                try:
                    return eval(f"await page.{loc}")
                except SyntaxError:
                    try:
                        return eval(f"page.{loc}")
                    except SyntaxError as error:
                        self.base_data.log.error(f'WEB自动化查找元素失败-3，类型：{type(error)}，失败详情：{error}')
                        raise MangoAutomationError(*ERROR_MSG_0022)
                    except NameError as error:
                        self.base_data.log.error(f'WEB自动化查找元素失败-4，类型：{type(error)}，失败详情：{error}')
                        raise MangoAutomationError(*ERROR_MSG_0060)
            case ElementExpEnum.XPATH.value:
                return page.locator(f'xpath={loc}')
            case ElementExpEnum.CSS.value:
                return page.locator(loc)
            case ElementExpEnum.TEXT.value:
                return page.get_by_text(loc, exact=True)
            case ElementExpEnum.PLACEHOLDER.value:
                return page.get_by_placeholder(loc)
            case _:
                raise MangoAutomationError(*ERROR_MSG_0020)
