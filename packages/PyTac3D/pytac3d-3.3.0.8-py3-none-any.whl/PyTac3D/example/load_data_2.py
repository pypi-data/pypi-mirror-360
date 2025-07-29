'''
Example: load_data_2.py

This example demonstrates how to simultaneously read and visualize locally recorded data from multiple Tac3D tactile sensors.

The main implementation process includes:
1. Loading multiple sets of locally recorded data using PyTac3D.DataLoader
2. Time-aligning the read data frames according to their timestamps
3. Simultaneously visualizing multiple sets of tactile data using PyTac3D.Sensor and PyTac3D.Displayer

Note: For routines that acquire data frames from sensors in real time, please refer to:
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py

本示例主要展示如何同时读取并可视化本地录制的多个Tac3D触觉传感器数据

主要实现过程包括：
1. 使用PyTac3D.DataLoader加载本地保存的多组录制数据
2. 根据数据帧的时间戳使读取的数据帧时间对齐
3. 使用PyTac3D.Sensor和PyTac3D.Displayer同时可视化展示多组触觉数据

注：实时从传感器获取数据帧的例程请参阅：
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py
'''

# Library for Tac3D Sensor
# Tac3D传感器的库
import PyTac3D

import time
import numpy as np
import os

# Define data path using the example data
# 设置读取数据路径为示例数据
path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'example_data/example_2')
SN1 = 'HDL1-GWH0021'  # Sensor SN of the recorded data
SN2 = 'HDL1-GWH0022'  # Sensor SN of the recorded data

# Create data loaders to load data from example_data/example_2 directory with specified SN
# 创建DataLoader用于加载example_data/example_2目录下指定SN传感器录制的数据
loader1 = PyTac3D.DataLoader(path, SN1, skip=0)
loader2 = PyTac3D.DataLoader(path, SN2, skip=0)

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
view1.setTranslation([0,0,-15.5])

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
## Enable object visualization
## 打开物体（接触区3D形状估计）展示
view1.enable_Object = True
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
view2.setTranslation([0,0,15.5])


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
    global restartFlag
    # Set flag to restart playback
    # 设置重新回放标志
    restartFlag = True

def buttonCallback_Calibrate():
    # Placeholder for calibration function (only required when receiving data from a sensor)
    # 传感器校准功能（只在接受来自传感器的数据时需要）
    pass

# Create Displayer with lighting preset
# 创建显示窗口Displayer，使用预设的光源设置
displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate

# Add configured views to the displayer
# 将设置好的SenserView视角添加到显示窗口
displayer.addView(view1)
displayer.addView(view2)


# Parameters for the display loop
# 显示循环参数
## Time step for display (seconds)
## 渲染周期（秒）
dt = 0.03
## Flag to control data playback restart
## 设置重新回放标志
restartFlag = True

# Main display loop
# 主显示循环
while displayer.isRunning():
    if restartFlag:
        # Reset loaders to start of data
        loader1.reset()
        loader2.reset()
        # Get first frame data
        # 获取第一帧数据
        frame1, t1, endFlag1 = loader1.get()
        frame2, t2, endFlag2 = loader2.get()
        # Reset start time reference
        # 重置起始时间
        startTime = time.time() - max(t1, t2)
        restartFlag = False

    # Calculate current time in data timeline
    # 计算当前回放的时间点
    currentTime = time.time() - startTime

    # Synchronize data with actual time
    # 读取数据帧的时间对齐到当前时间点
    while not endFlag1 and t1 < currentTime:
        frame1, t1, endFlag1 = loader1.get()

    while not endFlag2 and t2 < currentTime:
        frame2, t2, endFlag2 = loader2.get()
    
    # Restart when reaching the end of data
    # 到达最后一帧时重新开始回放
    if endFlag1 or endFlag2:
        restartFlag = True

    # Process and display current frame if available
    # 如果成功获取到数据帧，则进行处理和展示
    if frame1:
        # Detect objects before visualization
        analyzer1.detectObjects(frame1)
        # Update 3D visualization
        # 更新3D可视化画面
        view1.put(frame1)

    if frame2:
        # Detect contact before visualization
        analyzer2.detectContact(frame2)
        # Update 3D visualization
        # 更新3D可视化画面
        view2.put(frame2)

    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(dt)

