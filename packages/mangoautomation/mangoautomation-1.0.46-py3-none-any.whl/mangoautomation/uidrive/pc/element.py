from ...tools import Meta
from ...uidrive._base_data import BaseData


class WinElement(metaclass=Meta):
    """元素操作"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    def click(self, control):
        """点击控件"""
        control.Click()

    def input_text(self, control, text: str):
        """输入文本"""
        control.SendKeys(text)

    def get_text(self, control) -> str:
        """获取控件文本"""
        return control.Name
