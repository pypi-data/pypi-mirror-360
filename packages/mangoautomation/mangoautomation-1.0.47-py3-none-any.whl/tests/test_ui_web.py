# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-12 17:31
# @Author : 毛鹏
import asyncio
import unittest

from mangoautomation.models import ElementModel
from mangoautomation.uidrive import AsyncElement, BaseData, DriverObject, SyncElement
from mangotools.data_processor import DataProcessor
from mangotools.log_collector import set_log

log = set_log('D:\GitCode\mango_automation\logs')
test_data = DataProcessor()
element_model_1 = ElementModel(**{
    "id": 9,
    "type": 0,
    "name": "搜索结果",
    "loc": "get_by_role(\"link\", name=\"芒果自动化测试平台: 芒果测试平台是UI和API的自动化测试\")",
    "exp": 2,
    "sleep": None,
    "sub": None,
    "is_iframe": 0,
    "ope_key": "w_open_new_tab_and_switch",
    "ope_value": [
        {
            "f": "locating",
            "p": None,
            "d": False,
            "v": ""
        }
    ],
    "key_list": None,
    "sql": None,
    "key": None,
    "value": None
})
element_model_2 = ElementModel(**{
    "id": 10, "type": 2, "name": "结果内容", "loc": "get_by_role(\"heading\", name=\"芒果测试平台是集UI，API\")",
    "exp": 0,
    "sleep": None, "sub": None, "is_iframe": 0, "ope_key": "w_get_text",
    "ope_value": [{"f": "locating", "p": None, "d": False, "v": ""},
                  {"f": "set_cache_key", "p": None, "d": True, "v": "结果内容"}]
})


class TestUi(unittest.IsolatedAsyncioTestCase):
    async def test_a(self):
        driver_object = DriverObject(True)
        driver_object.set_web(0, r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        base_data = BaseData(test_data, log)
        base_data.log = log
        base_data.url = 'https://www.baidu.com/'

        base_data.context, base_data.page = await driver_object.web.new_web_page()
        element = AsyncElement(base_data, element_model_1, 0)
        await element.open_url()
        await asyncio.sleep(5)
        await element.element_main()
        print(element.element_result_model.model_dump())
        element = AsyncElement(base_data, element_model_2, 0)
        await element.element_main()
        print(element.element_result_model.model_dump())


class TestUi2(unittest.TestCase):

    def test_s(self):
        driver_object = DriverObject()
        driver_object.set_web(0, r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        base_data = BaseData(test_data, log)
        base_data.url = 'https://www.baidu.com/'
        base_data.context, base_data.page = driver_object.web.new_web_page()
        element = SyncElement(base_data, element_model_1, 0)
        element.open_url()
        element.element_main()
