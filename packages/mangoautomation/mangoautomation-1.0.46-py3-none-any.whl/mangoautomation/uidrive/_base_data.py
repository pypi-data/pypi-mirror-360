# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-02-04 10:43
# @Author : 毛鹏
from typing import Optional
from unittest.mock import MagicMock

import sys
from uiautomator2 import Device

from mangoautomation.enums import DriveTypeEnum
from mangoautomation.exceptions import MangoAutomationError
from mangoautomation.exceptions._error_msg import ERROR_MSG_0010, ERROR_MSG_0007
from mangotools.data_processor import DataProcessor
from mangotools.database import MysqlConnect
from mangotools.enums import StatusEnum
from mangotools.models import MysqlConingModel

if not sys.platform.startswith('win32'):
    WindowControl = MagicMock()
    print("警告: uiautomation 仅支持 Windows，当前环境已自动跳过")
else:
    from uiautomation import WindowControl


class BaseData:

    def __init__(self, test_data: DataProcessor, log):
        super().__init__()
        self.test_data = test_data
        self.log = log
        self.download_path: Optional[str | None] = None
        self.screenshot_path: Optional[str | None] = None

        self.mysql_config: Optional[MysqlConingModel | None] = None
        self.mysql_connect: Optional[MysqlConnect | None] = None

        self.url: Optional[str | None] = None
        self.is_open_url = False
        self.page = None
        self.context = None

        self.package_name: Optional[str | None] = None
        self.android: Optional[Device | None] = None
        self.is_open_app = False

        self.window: Optional[None | WindowControl] = None

    def set_file_path(self, download_path, screenshot_path):
        self.download_path = download_path
        self.screenshot_path = screenshot_path
        return self

    def set_url(self, url: str):
        self.url = url
        return self

    def set_page_context(self, page, context):
        self.page = page
        self.context = context
        return self

    def set_package_name(self, package_name: str):
        self.package_name = package_name
        return self

    def set_android(self, android: Device):
        self.android = android
        return self

    def setup(self) -> None:
        self.url = None
        self.page = None
        self.context = None

        self.package_name = None
        self.android = None
        self.mysql_connect = None
        self.mysql_config = None

    async def async_base_close(self):
        if self.context:
            await self.context.close()
        if self.page:
            await self.page.close()
        if self.mysql_connect:
            self.mysql_connect.close()
        self.setup()

    def sync_base_close(self):
        if self.context:
            self.context.close()
        if self.page:
            self.page.close()
        if self.mysql_connect:
            self.mysql_connect.close()
        self.setup()

    def set_mysql(self, db_c_status, db_rud_status, mysql_config: MysqlConingModel):
        self.mysql_config = mysql_config
        if StatusEnum.SUCCESS.value in [db_c_status, db_rud_status]:
            self.mysql_connect = MysqlConnect(mysql_config,
                                              bool(db_c_status),
                                              bool(db_rud_status))
        return self

    def verify_equipment(self, drive_type: int):
        if drive_type == DriveTypeEnum.WEB.value:
            if not self.page or not self.context:
                raise MangoAutomationError(*ERROR_MSG_0010)
        elif drive_type == DriveTypeEnum.ANDROID.value:
            if not self.android:
                raise MangoAutomationError(*ERROR_MSG_0007)
        else:
            pass
