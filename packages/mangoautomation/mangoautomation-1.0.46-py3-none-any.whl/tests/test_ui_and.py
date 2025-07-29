# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-05-03 10:02
# @Author : 毛鹏
import traceback


#
# driver_object = DriverObject()
# driver_object.set_android('ed789e3b')
# test_data = DataProcessor()
# base_data = BaseData(test_data)
# base_data.android = driver_object.android.new_android()
# android_driver = AndroidDriver(base_data)
# android_driver.a_close_app('aaasdsadawdwadwa')
#


def a_ass(a, b):
    assert a == b, f'断言A=B失败, a的值:{a}, b的值:{b}'


try:
    a_ass(1, 2)
except AssertionError as error:
    print(error.args[1])
    print(type(error))
    traceback.print_exc()
