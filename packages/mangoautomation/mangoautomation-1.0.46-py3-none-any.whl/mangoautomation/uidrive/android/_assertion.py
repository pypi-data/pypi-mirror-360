# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-09-09 23:17
# @Author : 毛鹏
from uiautomator2 import UiObject

from mangoautomation.tools import Meta
from mangoautomation.uidrive._base_data import BaseData
from mangotools.decorator import sync_method_callback
from mangotools.models import MethodModel


class AndroidAssertion(metaclass=Meta):
    """元素断言"""

    def __init__(self, base_data: BaseData):
        self.base_data = base_data

    @sync_method_callback('ass_android', '元素断言', 1,[
        MethodModel(f='actual')])
    def a_assert_ele_exists(self, actual: UiObject):
        """元素存在"""
        assert actual.count

    @sync_method_callback('ass_android', '元素断言', 2,[
        MethodModel(f='actual'),
        MethodModel(f='expect', p='请输入预期内容', d=True)])
    def a_assert_ele_count(self, actual: UiObject, expect):
        """元素计数"""
        assert int(actual.count) == int(expect)

    @sync_method_callback('ass_android', '元素断言', 3,[
        MethodModel(f='actual'),
        MethodModel(f='expect', p='请输入预期文本', d=True)])
    def a_assert_ele_text(self, actual: UiObject, expect: str):
        """元素文本内容"""
        assert actual.get_text() == expect, \
            f"实际='{actual.get_text()}', 预期='{expect}'"

    @sync_method_callback('ass_android', '元素断言', 4,[
        MethodModel(f='actual')])
    def a_assert_ele_clickable_true(self, actual: UiObject):
        """元素可点击"""
        assert actual.info['clickable'], \
            f"实际={actual.info['clickable']}, 预期=可点击"

    @sync_method_callback('ass_android', '元素断言', 5,[
        MethodModel(f='actual')])
    def a_assert_ele_clickable_false(self, actual: UiObject):
        """元素不可点击"""
        assert not actual.info['clickable'], \
            f"实际={actual.info['clickable']}, 预期=元素不可点击"

    @sync_method_callback('ass_android', '元素断言', 6,[
        MethodModel(f='actual')])
    def a_assert_ele_visible_true(self, actual: UiObject):
        """元素可见"""
        assert actual.exists and actual.info['visible'], \
            f"实际={actual.info['visible']}, 预期=元素可见"

    @sync_method_callback('ass_android', '元素断言', 7,[
        MethodModel(f='actual')])
    def a_assert_ele_visible_false(self, actual: UiObject):
        """元素不可见"""
        assert actual.exists and not actual.info['visible'], \
            f"实际={actual.info['visible']}, 预期=元素不可见"

    @sync_method_callback('ass_android', '元素断言', 8,[
        MethodModel(f='expect', p='请输入弹窗标题文本', d=False)])
    def a_assert_dialog_exists(self, expect: str):
        """弹窗存在"""
        dialog = self.base_data.android(text=expect) if expect else self.base_data.android(
            className="android.app.AlertDialog")
        assert dialog.exists, "未找到预期弹窗"

    @sync_method_callback('ass_android', '元素断言', 9,[
        MethodModel(f='actual'),
        MethodModel(f='expect', p='请输入断言目标文本', d=True)])
    def a_assert_ele_in_list(self, actual: UiObject, expect: str):
        """列表滑动后目标元素存在"""
        if not actual.exists:
            raise AssertionError("传入的元素不是可滑动的列表")
        actual.scroll.vert.to(text=expect)
        assert self.base_data.android(text=expect).exists, f"列表中未找到文本: {expect}"
