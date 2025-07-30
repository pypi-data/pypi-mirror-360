# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-30 13:12
# @Author : 毛鹏
import subprocess
from typing import Optional

import sys
import time

if not sys.platform.startswith('win32'):
    print("警告: uiautomation 仅支持 Windows，当前环境已自动跳过")


    class Auto:
        pass


    auto = Auto()


    class Control:
        pass
else:

    from uiautomation import Control, WindowControl
    import uiautomation


class NewWindows:

    def __init__(self, win_path: str, win_title: str, timeout=10):
        self.win_path = win_path
        self.win_title = win_title
        self.timeout = timeout
        self.window: Optional[None | WindowControl] = None

    def new_windows(self, retry=3):
        subprocess.Popen(self.win_path)
        for _ in range(retry):
            self.window = uiautomation.WindowControl(
                searchDepth=1,
                Name=self.win_title,
                Timeout=self.timeout * 1000
            )
            if self.window.Exists():
                return self.window
            time.sleep(1)

    def find_control(self,
                     parent=None,
                     control_type: str = "Control",
                     name: str = None,
                     automation_id: str = None,
                     **kwargs) -> Control:
        """
        查找控件（支持多条件组合）
        :param parent: 父控件（默认从窗口开始查找）
        :param control_type: 控件类型（如 Button、Edit、ListItem）
        :param name: 控件名称（Name 属性）
        :param automation_id: AutomationId 属性
        :return: Control 对象
        """
        search_params = {
            "searchDepth": 2,
            "Timeout": self.timeout * 1000,
            **kwargs
        }
        if name:
            search_params["Name"] = name
        if automation_id:
            search_params["AutomationId"] = automation_id

        parent = parent or self.window
        control = getattr(uiautomation, f"{control_type}Control")(parent=parent, **search_params)
        if not control.Exists():
            raise Exception(f"未找到控件: {control_type}/{name}/{automation_id}")
        return control
