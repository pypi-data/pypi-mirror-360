'''
Example: receive_from_multiple_sensors.py

This example demonstrates how to real-time receive tactile data frames from multiple running Tac3D tactile sensors.

The main implementation process includes:
1. Using PyTac3D.Sensor.getFrame() to retrieve data frames from multiple Tac3D tactile sensors in real time
2. Calculating contact area information in data frames using PyTac3D.Analyzer.detectContact()
3. Visualizing multiple sets of tactile data simultaneously using PyTac3D.Sensor and PyTac3D.Displayer

Note: 
PyTac3D.Sensor only has the capability to receive Tac3D data frames. When using this example, please ensure:
- The Tac3D main program is already running
- The SDK receiving port is set to 9988 (the port used in this example)
Refer to the Tac3D Tactile Sensor User Manual for instructions on launching the Tac3D main program.

本示例主要展示如何实时地接收多个运行中的Tac3D触觉传感器的触觉数据帧

主要实现过程包括：
1. 使用PyTac3D.Sensor.getFrame()函数实时地获取多个Tac3D触觉传感器的数据帧
2. 使用PyTac3D.Analyzer.detectContact()函数计算数据帧中的接触区域信息
3. 使用PyTac3D.Sensor和PyTac3D.Displayer同时可视化多组触觉数据

注： 
PyTac3D.Sensor只具有接收Tac3D数据帧的功能，在使用本例程时请确保
- Tac3D主程序已经启动
- SDK接收端口设置为9988（本例程使用的端口）
启动Tac3D主程序的方法请参阅Tac3D触觉传感器使用手册
'''

# Library for Tac3D Sensor
# Tac3D传感器的库
import PyTac3D

import time
import numpy as np

# Prompt user to input sensor SN
# 提示用户输入所使用的触觉传感器的SN
print('For the first Tac3D sensor:')
SN1 = PyTac3D.Presets.inputSN()
print('For the second Tac3D sensor:')
SN2 = PyTac3D.Presets.inputSN()

# Initialize PyTac3D.Sensor instance with port configuration
# Port 9988 is commonly used for Tac3D sensor communication
# 创建PyTac3D.Sensor实例并指定数据接收端口
# 端口9988是Tac3D传感器默认使用的数据传输端口
sensor = PyTac3D.Sensor(port=9988)

# Wait until the first frame from the specified tactile sensor is received
# 等待接收来自指定触觉传感器的数据
sensor.waitForFrame(SN1)
sensor.waitForFrame(SN2)

# Create analyzers instance for processing tactile data
# 创建Analyzer用于数据处理
analyzer1 = PyTac3D.Analyzer(SN1)
analyzer2 = PyTac3D.Analyzer(SN2)

# Create sensor view with default color preset for visualization
# 创建一个SensorView用于数据可视化
view1 = PyTac3D.SensorView(SN1, PyTac3D.Presets.Mesh_Color_1)

# Set display rotation matrix for view1 (identity matrix = no rotation)
# 设置数据展示位置的旋转变换矩阵（单位矩阵表示不旋转）
view1.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )

# Set display position for view1
# 设置数据展示位置的平移变换
view1.setTranslation([0,0,-15])

# Configure visualization toggles
## Enable mesh display
## 打开网格展示
view1.enable_Mesh = True
## Disable point cloud display
## 关闭点云展示
view1.enable_Pointcloud = False
## Enable contact visualization
## 打开接触展示
view1.enable_Contact = True
## Disable displacements visualization
## 关闭位移场展示
view1.enable_Displacements = False
## Disable surface normals visualization
## 关闭表面法线展示
view1.enable_Normals = False
## Enable distributed forces visualization
## 打开分布力展示
view1.enable_Forces = True
## Disable object visualization
## 关闭物体（接触区3D形状估计）展示
view1.enable_Object = False
## Disable resultant force display
## 关闭合力展示
view1.enable_3D_ResForce = False
## Disable resultant moment display
## 关闭合力矩展示
view1.enable_3D_ResMoment = False

# Create sensor view with default color preset for visualization
# 创建一个SensorView用于数据可视化
view2 = PyTac3D.SensorView(SN2, PyTac3D.Presets.Mesh_Color_1)

# Set display rotation matrix for view2
# 设置数据展示位置的旋转变换矩阵
view2.setRotation(
    np.matrix( [[1,0,0],
                [0,-1,0],
                [0,0,-1],
                ], np.float64)
    )

# Set display position for view2
# 设置数据展示位置的平移变换
view2.setTranslation([0,0,15])

# Configure visualization toggles
## Enable mesh display
## 打开网格展示
view2.enable_Mesh = True
## Disable point cloud display
## 关闭点云展示
view2.enable_Pointcloud = False
## Enable contact visualization
## 打开接触展示
view2.enable_Contact = True
## Disable displacements visualization
## 关闭位移场展示
view2.enable_Displacements = False
## Disable surface normals visualization
## 关闭表面法线展示
view2.enable_Normals = False
## Enable distributed forces visualization
## 打开分布力展示
view2.enable_Forces = True
## Disable object visualization
## 关闭物体（接触区3D形状估计）展示
view2.enable_Object = False
## Disable resultant force display
## 关闭合力展示
view2.enable_3D_ResForce = False
## Disable resultant moment display
## 关闭合力矩展示
view2.enable_3D_ResMoment = False

# Button callback function definitions
# 按钮回调函数定义
def buttonCallback_Restart():
    # Placeholder for restart function (only required when replay the recorded data.)
    # 重新回放函数（只在回放录制数据时需要）
    pass

def buttonCallback_Calibrate():
    # Send calibration signals to the main program of the Tac3D sensors.
    # 向Tac3D主程序发送校准信号
    sensor.calibrate(SN1)
    sensor.calibrate(SN2)

# Create Displayer with lighting preset
# 创建显示窗口Displayer，使用预设的光源设置
displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate

# Add configured views to the displayer
# 将设置好的SenserView视角添加到显示窗口
displayer.addView(view1)
displayer.addView(view2)

# Main display loop
# 主显示循环
while displayer.isRunning():
    # Retrieve a frame of data from the receive buffer; return None if the buffer is empty.
    # 从接收缓冲区中获取一帧数据；如果缓冲区中没有数据帧则返回None
    frame1 = sensor.getFrame(SN1)
    frame2 = sensor.getFrame(SN2)

    # Process and display current frame if available
    # 如果成功获取到数据帧，则进行处理和展示
    if frame1:
        # Detect contact regions in current frame
        # 检测当前帧中的接触区域
        # ref: help(PyTac3D.Analyzer.detectContact)
        analyzer1.detectContact(frame1)

        # Update 3D visualization
        # 更新3D可视化画面
        view1.put(frame1)

    if frame2:
        # Detect contact regions
        analyzer2.detectContact(frame2)
        # Update 3D visualization
        # 更新3D可视化画面
        view2.put(frame2)
        
    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(0.03)
