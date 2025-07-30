# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏

from uiautomator2 import UiObject, UiObjectNotFoundError
from uiautomator2.exceptions import XPathElementNotFoundError
from uiautomator2.xpath import XPathSelector

from mangotools.assertion import MangoAssertion
from ..android._application import AndroidApplication
from ..android._assertion import AndroidAssertion
from ..android._customization import AndroidCustomization
from ..android._element import AndroidElement
from ..android._equipment import AndroidEquipment
from ..android._page import AndroidPage
from ...enums import ElementExpEnum
from ...exceptions import MangoAutomationError
from ...exceptions._error_msg import *

__all__ = [
    'AndroidApplication',
    'AndroidAssertion',
    'AndroidElement',
    'AndroidCustomization',
    'AndroidEquipment',
    'AndroidPage',
    'AndroidDriver',
]

from mangotools.mangos import Mango


class AndroidDriver(AndroidPage,
                    AndroidElement,
                    AndroidEquipment,
                    AndroidCustomization,
                    AndroidApplication):

    def __init__(self, base_data):
        super().__init__(base_data)

    def open_app(self):
        if not self.base_data.is_open_app:
            self.base_data.is_open_app = True
            self.a_press_home()
            self.a_app_stop_all()
            if self.base_data.android and self.base_data.package_name:
                self.a_start_app(self.base_data.package_name)

    def a_action_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'操作元素，名称：{name},key:{ope_key},value:{ope_value}')
        try:
            Mango.s_e(self, ope_key, ope_value)
        except ValueError as error:
            self.base_data.log.error(f'安卓自动化失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0012)
        except UiObjectNotFoundError as error:
            self.base_data.log.error(f'安卓自动化失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0032, value=(name,))
        except XPathElementNotFoundError as error:
            self.base_data.log.error(f'安卓自动化失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0050, value=(name,))

    def a_assertion_element(self, name, ope_key, ope_value):
        self.base_data.log.debug(f'断言元素，名称：{name},key:{ope_key},value:{ope_value}')
        is_method = callable(getattr(AndroidAssertion(self.base_data), ope_key, None))
        if is_method and ope_value.get('actual') is None:
            raise MangoAutomationError(*ERROR_MSG_0031, value=(name,))

        try:
            if is_method:
                self.base_data.log.debug(f'开始断言-1，方法：{ope_key}，断言值：{ope_value}')
                Mango.s_e(AndroidAssertion(self.base_data), ope_key, ope_value)
            else:
                self.base_data.log.debug(f'开始断言-2，方法：{ope_key}，断言值：{ope_value}')
                MangoAssertion(self.base_data.mysql_connect).ass(ope_key, ope_value.get('actual'), ope_value.get('expect'))
        except AssertionError as error:
            self.base_data.log.error(f'安卓自动化失败-1，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0017, value=error.args)
        except AttributeError as error:
            self.base_data.log.error(f'安卓自动化失败-2，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0030, )
        except ValueError as error:
            self.base_data.log.error(f'安卓自动化失败-3，类型：{type(error)}，失败详情：{error}')
            raise MangoAutomationError(*ERROR_MSG_0005, )

    def a_find_ele(self, name, _type, exp, loc, sub) -> tuple[UiObject, int, str] | tuple[XPathSelector, int, str]:
        self.base_data.log.debug(
            f'查找元素，名称：{name},_type:{_type},exp:{exp},loc:{loc},sub:{sub}')
        match exp:
            case ElementExpEnum.LOCATOR.value:
                try:
                    if loc[:5] == 'xpath':
                        loc = eval(f"self.android.{loc}")
                    else:
                        loc = eval(f"self.android{loc}")
                except SyntaxError:
                    raise MangoAutomationError(*ERROR_MSG_0022)
            case ElementExpEnum.XPATH.value:
                loc = self.base_data.android.xpath(loc)
            case ElementExpEnum.BOUNDS.value:
                loc = self.base_data.android(text=loc)
            case ElementExpEnum.DESCRIPTION.value:
                loc = self.base_data.android(description=loc)
            case ElementExpEnum.RESOURCE_ID.value:
                loc = self.base_data.android(resourceId=loc)
            case _:
                raise MangoAutomationError(*ERROR_MSG_0020)
        text = None
        try:
            text = self.a_get_text(loc)
        except Exception:
            pass
        if exp == ElementExpEnum.XPATH.value:
            count = len(loc.all())
        else:
            count = loc.count
        return loc, count, text
