# MicroPython v1.23.0
# -*- coding: utf-8 -*-   
# @Time    : 2025/8/24 下午3:37
# @Author  : hogeiha
# @File    : main.py
# @Description : uv紫外线

# ======================================== 导入相关模块 =========================================

import machine
import tm1637
import time
from guva_s12sd import GUVA_S12SD


# ======================================== 全局变量 =============================================

# 功能状态
sleep_flag = False

# ======================================== 功能函数 =============================================

def key2_handler(pin):
    """key2按下：关闭功能"""
    global sleep_flag
    sleep_flag = True
    print("关闭功能")

def key1_handler(pin):
    """key1按下：打开检测"""
    global sleep_flag
    sleep_flag = False
    print("打开检测！")

# ======================================== 自定义类 =============================================

# ========================================初始化配置 =============================================


# 初始化按键
# 唤醒键
key1 = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_UP)  
# 睡眠键
key2 = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)
# 紫外线传感器
sensor = GUVA_S12SD(26)
# 数码管
tm = tm1637.TM1637(clk=machine.Pin(11), dio=machine.Pin(10))

# 设置中断
key1.irq(trigger=machine.Pin.IRQ_FALLING, handler=key1_handler)
key2.irq(trigger=machine.Pin.IRQ_FALLING, handler=key2_handler)

# ======================================== 主程序 ===============================================

while True:
    if sleep_flag :
         machine.idle()
    else:
        voltage = sensor.voltage
        v=int(voltage / 3.3 * 1000)
        tm.number(v)
        print(voltage)
    time.sleep_ms(100)
    