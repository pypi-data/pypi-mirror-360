# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-05-23 15:04
# @Author : 毛鹏
# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-24 10:43
# @Author : 毛鹏
import ctypes
import os
import string
import threading
import traceback
from typing import Optional

import time
from playwright._impl._errors import Error
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser, Playwright, Request, Route

from ....enums import BrowserTypeEnum
from ....exceptions import MangoAutomationError
from ....exceptions._error_msg import ERROR_MSG_0057, ERROR_MSG_0008, ERROR_MSG_0062, ERROR_MSG_0009, ERROR_MSG_0055



class SyncWebNewBrowser:

    def __init__(self,
                 web_type: int,
                 web_path: str | None = None,
                 web_max=False,
                 web_headers=False,
                 web_recording=False,
                 web_h5=None,
                 is_header_intercept=False,
                 web_is_default=False,
                 videos_path=None
                 ):
        self.lock = threading.Lock()
        self.web_type = web_type
        self.web_path = web_path
        self.web_max = web_max
        self.web_headers = web_headers
        self.web_recording = web_recording
        self.web_h5 = web_h5
        self.web_is_default = web_is_default
        self.videos_path = videos_path
        self.is_header_intercept = is_header_intercept
        self.browser_path = ['chrome.exe', 'msedge.exe', 'firefox.exe', '苹果', '360se.exe']
        self.browser: Optional[None | Browser] = None
        self.playwright: Optional[None | Playwright] = None

    def new_web_page(self, count=0) -> tuple[BrowserContext, Page]:
        if self.browser is None:
            with self.lock:
                self.browser = self.new_browser()
                time.sleep(1)
        try:
            context = self.new_context()
            page = self.new_page(context)
            return context, page
        except Exception as error:
            self.browser = None
            traceback.format_exc()
            if count >= 3:
                raise MangoAutomationError(*ERROR_MSG_0057)
            else:
                return self.new_web_page(count=count + 1)

    def new_browser(self) -> Browser:
        self.playwright = sync_playwright().start()
        if self.web_type == BrowserTypeEnum.CHROMIUM.value or self.web_type == BrowserTypeEnum.EDGE.value:
            browser = self.playwright.chromium
        elif self.web_type == BrowserTypeEnum.FIREFOX.value:
            browser = self.playwright.firefox
        elif self.web_type == BrowserTypeEnum.WEBKIT.value:
            browser = self.playwright.webkit
        else:
            raise MangoAutomationError(*ERROR_MSG_0008)
        if self.web_is_default:
            try:
                return browser.launch()
            except Error:
                raise MangoAutomationError(*ERROR_MSG_0062)
        else:
            try:
                if self.web_max:
                    return browser.launch(
                        headless=self.web_headers,
                        executable_path=self.web_path if self.web_path else self.__search_path(),
                        args=['--start-maximized']
                    )
                else:
                    return browser.launch(
                        headless=self.web_headers,
                        executable_path=self.web_path if self.web_path else self.__search_path()
                    )
            except Error:
                raise MangoAutomationError(*ERROR_MSG_0009, value=(self.web_path,))

    def new_context(self) -> BrowserContext:
        args_dict = {}
        if self.web_is_default:
            args_dict["viewport"] = {"width": 1920, "height": 1080}
        if self.web_h5:
            args_dict.update(self.playwright.devices[self.web_h5])
        if not (self.web_is_default or self.web_h5):
            args_dict["no_viewport"] = True
        if self.web_recording and self.videos_path:
            args_dict["record_video_dir"] = self.videos_path
        return self.browser.new_context(**args_dict)

    def new_page(self, context: BrowserContext) -> Page:
        try:
            page = context.new_page()
            if self.is_header_intercept:
                page.route("**/*", self.wen_intercept_request)  # 应用拦截函数到页面的所有请求
            return page
        except Error:
            raise MangoAutomationError(*ERROR_MSG_0009, value=(self.web_path,))

    def close(self):
        if self.browser:
            self.browser.close()

    def __search_path(self, ):
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(drive) == 3:
                drives.append(drive)
        for i in drives:
            for root, dirs, files in os.walk(i):
                if self.browser_path[self.web_type] in files:
                    return os.path.join(root, self.browser_path[self.web_type])

        raise MangoAutomationError(*ERROR_MSG_0055)

    def wen_intercept_request(self, route: Route, request: Request):
        pass

    def wen_recording_api(self, request: Request, project_product: int):
        pass
