# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: # @Time   : 2023-07-15 12:02
# @Author : 毛鹏
from typing import Optional

import sys

if not sys.platform.startswith('win32'):
    print("警告: uiautomation 仅支持 Windows，当前环境已自动跳过")


    class Auto:
        pass


    auto = Auto()


    class Control:
        pass
else:

    from uiautomation import Control
    import uiautomation

from mangoautomation.uidrive._base_data import BaseData
from mangoautomation.uidrive.pc.element import WinElement
from mangoautomation.uidrive.pc.input_device import WinDeviceInput


class WinDriver(WinElement, WinDeviceInput):
    def __init__(self, base_data: BaseData):
        super().__init__(base_data)

    def find_element(
            self,
            *,
            control_type: str = "Control",
            name: Optional[str] = None,
            automation_id: Optional[str] = None,
            depth: int = 2,
            parent: Optional[Control] = None,
            **extra_attrs
    ) -> Control:

        if not any([name, automation_id, extra_attrs]):
            raise ValueError("必须提供至少一个定位参数(name/automation_id/其他属性)")

        # 设置默认父控件
        parent = parent or self.base_data.window.GetParentControl()

        # 构造搜索参数
        search_params = {
            "searchDepth": depth,
            "Timeout": 10 * 1000,
            **{
                key.capitalize() if key != "className" else "ClassName": value
                for key, value in {
                    "name": name,
                    "automationId": automation_id,
                    **extra_attrs
                }.items()
                if value is not None
            }
        }

        # 获取控件类并查找
        control_class = getattr(uiautomation, f"{control_type}Control", Control)
        control = control_class(parent=parent, **search_params)

        if not control.Exists():
            raise ElementNotFoundError(
                f"未找到控件: type={control_type}, params={search_params}"
            )
        return control


class ElementNotFoundError(Exception):
    pass
