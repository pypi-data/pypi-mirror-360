# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-05-28 18:40
# @Author : 毛鹏

from pydantic import BaseModel

from mangotools.models import MysqlConingModel, MethodModel


class EnvironmentConfigModel(BaseModel):
    id: int
    test_object_value: str
    db_c_status: bool
    db_rud_status: bool
    mysql_config: MysqlConingModel | None = None


class ElementModel(BaseModel):
    id: int
    type: int
    name: str | None
    loc: str | None
    exp: int | None
    sleep: int | None
    sub: int | None
    is_iframe: int | None
    ope_key: str | None
    ope_value: list[MethodModel] | None
    key_list: list | None = None
    sql: str | None = None
    key: str | None = None
    value: str | None = None


class ElementResultModel(BaseModel):
    id: int
    name: str | None = None
    loc: str | None = None
    exp: int | None = None
    sleep: int | None = None
    sub: int | None = None

    type: int
    ope_key: str | None = None
    ope_value: dict = {}
    expect: str | None = None
    actual: str | None = None
    sql: str | None = None
    key_list: str | None = None
    key: str | None = None
    value: str | None = None

    ele_quantity: int = 0
    element_text: str | None = None

    status: int = 0
    error_message: str | None = None
    picture_path: str | None = None
    picture_name: str | None = None
