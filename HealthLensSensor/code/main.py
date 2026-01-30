import time
import os
from machine import I2C, Pin, SoftI2C
from mlx90614 import MLX90614
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
from heart_rate_monitor import HeartRateMonitor
from ssd1306 import SSD1306_I2C


# 初始化I2C总线
# oled使用SoftI2C（引脚8,9）
i2c_for_oled = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)

# MLX90614使用硬件I2C（引脚2,3）
i2c_for_sensors = I2C(1, scl=11, sda=10, freq=100000)

# 初始化OLED显示
# 扫描I2C总线查找OLED地址
oled_address = None
devices_list = i2c_for_oled.scan()
for device in devices_list:
    if device == 0x3c or device == 0x3d:
        oled_address = device
        break

if oled_address is None:
    print("OLED未找到，请检查连接")
    oled = None
else:
    print(f"OLED地址: {hex(oled_address)}")
    oled = SSD1306_I2C(i2c_for_oled, oled_address, 128, 64, False)
    oled.fill(0)
    oled.text("系统启动中...", 10, 20)
    oled.show()

# 初始化MLX90614温度传感器
temp_sensor = MLX90614(i2c_for_sensors, 0x5A)

# 初始化MAX30102心率传感器
hr_sensor = MAX30102(i2c=i2c_for_sensors)
if hr_sensor.i2c_address not in i2c_for_sensors.scan() or not hr_sensor.check_part_id():
    print("MAX30102传感器未找到或识别失败")
    hr_sensor = None
else:
    print("心率传感器已连接")
    hr_sensor.setup_sensor()
    hr_sensor.set_sample_rate(400)
    hr_sensor.set_fifo_average(8)
    hr_sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

# 初始化心率监测器
actual_rate = 400 // 8
hr_monitor = HeartRateMonitor(sample_rate=actual_rate, window_size=actual_rate * 3)

# 心率计算间隔
hr_interval = 2
last_hr_time = time.ticks_ms()

# 显示更新间隔
display_interval = 1  # 每秒更新一次显示
last_display_time = time.ticks_ms()

print("开始读取温度和心率数据...")

# 显示初始信息
if oled:
    oled.fill(0)
    oled.text("等待数据...", 10, 25)
    oled.show()

try:
    while True:
        current_time = time.ticks_ms()
        
        # 处理MAX30102数据
        if hr_sensor:
            hr_sensor.check()
            if hr_sensor.available():
                red = hr_sensor.pop_red_from_storage()
                ir = hr_sensor.pop_ir_from_storage()
                hr_monitor.add_sample(ir)
        
        # 计算心率
        if hr_sensor and time.ticks_diff(current_time, last_hr_time) / 1000 > hr_interval:
            heart_rate = hr_monitor.calculate_heart_rate()
            last_hr_time = current_time
        if ir:
            blood_oxygen = 100 - 25 * (red / ir)
        
        # 更新OLED显示
        if oled and time.ticks_diff(current_time, last_display_time) / 1000 > display_interval:
            # 读取温度
            ambient = temp_sensor.read_ambient()
            body = temp_sensor.read_object()
            
            # 清屏
            oled.fill(0)
            
            # 显示标题
            oled.text("Health Monitoring System", 10, 0)
            oled.hline(0, 10, 128, 1)
            
            
            # 显示人体温度
            body_str = f"body: {body:.1f}C"
            oled.text(body_str, 0, 15)
            
            # 显示心率
            if hr_sensor and 'heart_rate' in locals() and heart_rate is not None:
                hr_str = f"heart_rate: {heart_rate:.0f} BPM"
            else:
                hr_str = "heart_rate: -- BPM"
            oled.text(hr_str, 0, 30)
            
            blood_oxygen = f"oxygen: {blood_oxygen:.1f}%"
            oled.text(blood_oxygen, 0, 45)
            # 显示分隔线
            oled.hline(0, 55, 128, 1)
            
            
            # 更新显示
            oled.show()
            
            # 打印到串口
            print(f"环境温度: {ambient:.1f}°C")
            print(f"人体温度: {body:.1f}°C")
            if hr_sensor and 'heart_rate' in locals() and heart_rate is not None:
                print(f"心率: {heart_rate:.0f} BPM")
            else:
                print("心率: 正在计算...")
            print("-" * 20)
            
            last_display_time = current_time
            

except KeyboardInterrupt:
    print("程序结束")
    if oled:
        oled.fill(0)
        oled.text("程序已停止", 10, 25)
        oled.show()
