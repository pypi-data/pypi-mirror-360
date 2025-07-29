# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-05-23 15:05
# @Author : 毛鹏

from typing import Optional

import uiautomator2 as u2
from adbutils import AdbTimeout
from uiautomator2 import ConnectError

from ...exceptions import MangoAutomationError
from ...exceptions._error_msg import ERROR_MSG_0042, ERROR_MSG_0045, ERROR_MSG_0040

"""
python -m uiautomator2 init
python -m weditor

"""


class NewAndroid:

    def __init__(self, and_equipment):
        self.and_equipment = and_equipment
        self.info: Optional[dict | None] = None
        self.example_dict = []

    def new_android(self):
        if self.and_equipment is None:
            raise MangoAutomationError(*ERROR_MSG_0042)
        try:

            android = u2.connect(self.and_equipment)
            self.info = android.info
            # msg = f"设备启动成功！产品名称：{self.info.get('productName')}"
            self.example_dict.append({
                'config': self.and_equipment,
                'info': self.info,
                'android': android
            })
        except ConnectError:
            raise MangoAutomationError(*ERROR_MSG_0040, value=(self.and_equipment,))
        except RuntimeError:
            raise MangoAutomationError(*ERROR_MSG_0045, value=(self.and_equipment,))
        except (AdbTimeout, TimeoutError):
            raise MangoAutomationError(*ERROR_MSG_0040, value=(self.and_equipment,))
        else:
            android.implicitly_wait(10)
            return android

    def close_android(self):
        pass
