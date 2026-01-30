from max9814_mic import MAX9814Mic
from machine import Pin, ADC, I2C
from ulab import numpy as np
from ulab import scipy as spy
from pcf8575 import PCF8575
import time
import math

FS = 200.0                    # 采样率
CHUNK_SIZE = 50              # 缓冲区大小
F0 = 50.0                    # 陷波频率
Q = 50.0                     # 品质因数
ENVELOPE_ALPHA = 0.1         # 包络平滑系数（0-1，越小越平滑）


# 函数待补：PCF8575DBR驱动控制16个led
def display_level(level: int) -> None:
    """
        根据 level 值点亮前 N 个 LED。
        
    """
    pcf8575.port = x=(1 << (level + 1)) - 1
        

# 50Hz陷波滤波器系数（二阶节形式）
sos_notch_50hz = np.array([
    [0.970588235, 0.0, 0.970588235, 1.0, 0.0, 0.94117647]
], dtype=np.float)

print("=== 增强版包络检测 ===")

adc = ADC(26)
mic = MAX9814Mic(adc)

# 滤波器状态
zi = np.array([[0.0, 0.0]], dtype=np.float)

# 缓冲区
buffer = []

# 包络检测参数
prev_samples = []
window_size = 10          # 用于包络检测的窗口大小
sample_count = 0



i2c: I2C = I2C(id=1, sda=Pin(14), scl=Pin(15), freq=400000)

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

try:
    while True:
        raw_voltage = mic.read()
        buffer.append(raw_voltage)
        
        if len(buffer) >= CHUNK_SIZE:
            buffer_np = np.array(buffer, dtype=np.float)
            
            # 陷波滤波
            filtered_np, zi = spy.signal.sosfilt(sos_notch_50hz, buffer_np, zi=zi)
            
            # 包络检测（使用峰值检测方法）
            for i in range(len(buffer)):
                # 方法1：峰值保持包络检测
                rectified = abs(filtered_np[i])
                
                # 简单的峰值检测
                prev_samples.append(rectified)
                if len(prev_samples) > window_size:
                    prev_samples.pop(0)
                
                # 取窗口内的最大值作为包络
                envelope = max(prev_samples) if prev_samples else rectified
                envelope = max(25000, min(60000, envelope))
                level = int((envelope - 25000) / (60000 - 25000) * 16)

                # 输出
                #print(f"{buffer[i]:.4f},{filtered_np[i]:.4f},{envelope:.4f}")
                print(level)
                display_level(level)
                sample_count += 1
            
            buffer = []
        
        time.sleep(1.0 / FS)
        
except KeyboardInterrupt:
    print("采集停止")