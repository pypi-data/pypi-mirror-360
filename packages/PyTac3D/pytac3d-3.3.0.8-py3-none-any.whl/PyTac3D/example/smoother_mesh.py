'''
Example: smoother_mesh.py

This example demonstrates how to modify visualization module configurations to display smoother surface mesh.

The main implementation steps include:
1. Loading locally stored recorded data using PyTac3D.DataLoader
2. Obtaining visualization settings with PyTac3D.SensorView.getConfig()
3. Adjusting the visualization mesh upsample rate by modifying `mesh_upsample` parameter
4. Updating visualization settings with PyTac3D.SensorView.setConfig()
5. Visualizing tactile data using PyTac3D.Sensor and PyTac3D.Displayer

Note: 
Excessively high mesh upsample rates may cause lagging in the visualization interface.
For routines that acquire data frames from sensors in real time, please refer to:
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py

本示例主要展示如何修改可视化模块的配置以显示更平滑的表面网格

主要实现过程包括：
1. 使用PyTac3D.DataLoader加载本地保存的录制数据
2. 使用PyTac3D.SensorView.getConfig()获得可视化设置
3. 通过修改`mesh_upsample`调整可视化时的网格上采样倍率
4. 使用PyTac3D.SensorView.setConfig()修改可视化设置
5. 使用PyTac3D.Sensor和PyTac3D.Displayer可视化触觉数据

注：
过高的网格上采样倍率可能导致可视化界面卡顿
实时从传感器获取数据帧的例程请参阅：
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
import copy
import os

# Define data path using the example data
# 设置读取数据路径为示例数据
path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'example_data/example_1')

# Sensor SN of the recorded data
# 录制数据的传感器SN
SN1 = 'AD2-0065L'

# Define an additional SN (serial number) to facilitate simultaneous display of two SensorViews within the same Displayer.
# 定义另一个SN以便于在同一个Displayer中展示两个SensorView的视图
SN2 = SN1 + '-smooth'

# Create DataLoader to load data from example_data/example_1 directory with specified SN
# 创建DataLoader用于加载example_data/example_1目录下指定SN传感器录制的数据
loader = PyTac3D.DataLoader(path, SN1, skip=0)

# Create Analyzer instance for processing tactile data
# 创建Analyzer用于数据处理
analyzer= PyTac3D.Analyzer(SN1)

# Create sensor view with default color preset
# view1 displays the original mesh (20x20)
# 创建一个SensorView用于数据可视化
# view1展示原始的网格（20x20）
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
view1.setTranslation([-15, 0, -10])

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

# Create another sensor view for upsampled mesh
# 创建另一个SensorView用于展示上采样时候的网格
view2 = PyTac3D.SensorView(SN2, PyTac3D.Presets.Mesh_Color_1)

# Set display rotation matrix for view2 (identity matrix = no rotation)
# 设置数据展示位置的旋转变换矩阵（单位矩阵表示不旋转）
view2.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )

# Set display position for view2
# 设置数据展示位置的平移变换
view2.setTranslation([15, 0,-10])

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

####################################################
# Key Settings:
# 关键设置：

## Acquire the configuration of view2
## 获得view2的显示设置
config = view2.getConfig()

## Set mesh upsampling to 3x
## 设置网格上采样为3倍
config['mesh_upsample'] = 3

## Update the view2 configuration.
## 更新view2的显示设置
view2.setConfig(config)
####################################################

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
        loader.reset()
        # Get first frame data
        # 获取第一帧数据
        frame, t, endFlag = loader.get()
        # Reset start time reference
        # 重置起始时间
        startTime = time.time() - t
        restartFlag = False

    # Calculate current time in data timeline
    # 计算当前回放的时间点
    currentTime = time.time() - startTime

    # Synchronize data with actual time
    # 读取数据帧的时间对齐到当前时间点
    while not endFlag and t < currentTime:
        frame, t, endFlag = loader.get()

    # Restart when reaching the end of data
    # 到达最后一帧时重新开始回放
    if endFlag:
        restartFlag = True

    # Process and display current frames if available
    # 如果成功获取到数据帧，则进行处理和展示
    if frame:
        # Detect contact before visualization
        # 在可视化之前检测接触区域
        # ref: help(PyTac3D.Analyzer.detectContact)
        analyzer.detectContact(frame)

        # Update 3D visualization (original mesh)
        # 更新3D可视化画面（原始的网格）
        view1.put(frame)

        # Create a deep copy of frame1 as frame2.
        # 创建一个frame1的深拷贝副本frame2
        frame2 = copy.deepcopy(frame)

        # Modify the SN of frame2 (views within the same displayer must have different SNs).
        # 更改frame2的SN （同一个displayer中的view必须具有不同的SN）
        frame2["SN"] = SN2

        # Update 3D visualization (smoother mesh)
        # 更新3D可视化画面（更平滑的网格）
        view2.put(frame2)

    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(dt)

