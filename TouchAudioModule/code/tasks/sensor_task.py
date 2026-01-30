# Python env   : MicroPython v1.23.0
# -*- coding: utf-8 -*-
# @Time    : 2025/10/10 上午11:00
# @Author  : 侯钧瀚
# @File    : sensor_task.py
# @Description :   传感器任务，每200秒读取MQ-2 DO(低=检测到烟雾)火焰 DO（低=检测到火焰）。
# @License : CC BY-NC 4.0

# ======================================== 导入相关模块 =========================================

# 导入时间相关模块
import time

# ======================================== 全局变量 ============================================

# ======================================== 功能函数 ============================================

# ======================================== 自定义类 ============================================

class musicTask:
    """
    该类用于控制DHT11温湿度传感器、雾化器和风扇。
    主要功能：每次调用tick方法时，读取两次温湿度数据，根据温度≥30℃或湿度≥70%来控制风扇转速和雾化器开关，
    并可选打印当前温湿度。 、
    """
    def __init__(self, VibrationSensor, DYSV19T, debug=True):
        self.VibrationSensor = VibrationSensor
        self.DYSV19T = DYSV19T
        self.debug = debug
        self.count = 0
        self.time_segment = 0



    def tick(self):
        print("count:", self.count)
        if self.count != 0:
            self.time_segment += 1
            if self.time_segment >= 25:
                self.time_segment = 0
                self.count = 0


        if self.count >=3:
            self.count = 0
            if self.DYSV19T.query_status() == 1:
                self.DYSV19T.stop()
                if self.debug:
                    print("Detected Vibration! Playing music...")
            else:
                self.DYSV19T.play()
                if self.debug:
                    print("No Vibration. Music stopped.")



# ======================================== 初始化配置 ==========================================

# ========================================  主程序  ===========================================