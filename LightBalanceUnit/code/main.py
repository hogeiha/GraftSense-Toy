# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2025/8/22 下午12:49
# @Author  : hogeiha
# @File    : main.py
# @Description : 城小智·视护光衡

# ======================================== 导入相关模块 =========================================

from gl5516 import GL5516
import time

# ======================================== 全局变量 =============================================

# ======================================== 功能函数 =============================================

# 函数待补：PCF8575DBR驱动控制16个led
def display_level(level: int) -> None:
    """
        根据 level 值点亮前 N 个 LED。
    """
# ======================================== 自定义类 =============================================

# ======================================== 初始化配置 ===========================================

# 初始化 GL5516 光强度传感器，连接到 GPIO26 引脚
adc = GL5516(26)

# 校准光强度传感器
# 设置最小值
adc.min_light = 40585
print(f'min_light:{}')
# 设置最大值
adc.max_light = 2640
print(f'max_light:{}')
time.sleep(1)

# ======================================== 主程序 ===============================================

while True:
    # 读取光强度数据
    voltage, adc_value = adc.read_light_intensity()
    print("Light Intensity - Voltage: {} V, ADC Value: {}".format(voltage, adc_value))
    # 获取校准后的光强百分比
    light_level = int(adc.get_calibrated_light()*0.16)
    print("Calibrated Light Level: {}".format(light_level))
    time.sleep(2)