# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-07-01 10:43
# @Author : 毛鹏

import subprocess

import time

uiautodev_process = None


def start_uiautodev():
    """启动 uiautodev 服务"""
    global uiautodev_process
    if uiautodev_process is not None:
        return "uiautodev 服务已在运行！"
    try:
        # 启动 uiautodev 服务（后台运行）
        uiautodev_process = subprocess.Popen(
            ['uiauto.dev'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("uiautodev 服务启动成功！PID:", uiautodev_process.pid)
        return 'https://uiauto.devsleep.com/'
    except Exception as e:
        return f"启动 uiautodev 服务失败:{e}"


def stop_uiautodev():
    """关闭 uiautodev 服务"""
    global uiautodev_process

    if uiautodev_process is None:
        return "uiautodev 服务未运行！"
    try:
        uiautodev_process.terminate()
        uiautodev_process.wait(timeout=5)
        return  "uiautodev 服务已关闭"
    except subprocess.TimeoutExpired:
        uiautodev_process.kill()
        return "uiautodev 服务被强制终止"
    except Exception as e:
        return f"关闭 uiautodev 服务失败:{e}"
    finally:
        uiautodev_process = None
