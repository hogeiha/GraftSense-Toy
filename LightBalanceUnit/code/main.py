# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2025/8/22 下午12:49
# @Author  : hogeiha
# @File    : main.py
# @Description : 城小智·视护光衡

# ======================================== 导入相关模块 =========================================

from machine import Pin, ADC, I2C
from gl5516 import GL5516
import time
from pcf8575 import PCF8575

# ======================================== 全局变量 =============================================

# ======================================== 功能函数 =============================================

# 函数待补：PCF8575DBR驱动控制16个led
def display_level(level: int) -> None:
    """
        根据 level 值点亮前 N 个 LED。
        
    """
    num=(1 << (level + 1)) - 1
    low_8bit = num & 0xFF  # 提取低8位（原始后8位）
    high_8bit = (num >> 8) & 0xFF  # 提取高8位（原始前8位）
    
    # 3. 互换位置：低8位左移8位（变高8位） + 高8位（变低8位）
    num_swapped = (low_8bit << 8) | high_8bit
    pcf8575.port = num_swapped
# ======================================== 自定义类 =============================================

# ======================================== 初始化配置 ===========================================

i2c: I2C = I2C(id=1, sda=Pin(10), scl=Pin(11), freq=400000)

# 开始扫描I2C总线上的设备，返回从机地址的列表
devices_list: list[int] = i2c.scan()
print('START I2C SCANNER')

# 若devices_list为空，则没有设备连接到I2C总线上
if len(devices_list) == 0:
    print("No i2c device !")
# 若非空，则打印从机设备地址
else:
    print('i2c devices found:', len(devices_list))
    # 遍历从机设备地址列表
    for device in devices_list:
        print("I2C hexadecimal address: ", hex(device))
        # 假设第一个找到的设备是PCF8575
        PCF8575_ADDRESS = device

# 创建PCF8575类实例
pcf8575 = PCF8575(i2c, PCF8575_ADDRESS)

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
    display_level(light_level)
    print("Calibrated Light Level: {}".format(light_level))
    time.sleep_ms(50)