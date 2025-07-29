'''
Example: get_contact_info.py

This example demonstrates how to extract contact region information from Tac3D tactile sensor data frames.

Main contents include:
1. Loading locally saved recorded data using PyTac3D.DataLoader
2. Calculating contact region information in data frames using PyTac3D.Analyzer.detectContact() function
3. Retrieving information about the total contact area and individual contact regions (including contact points and contact area) from the data frame through frame['ContactRegion'] and frame['ContactRegions']
4. Visualizing tactile data using PyTac3D.Sensor and PyTac3D.Displayer

Note: For routines that acquire data frames from sensors in real time, please refer to:
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py

本示例主要展示如何从Tac3D触觉传感器的数据帧中获取接触区域信息

主要实现过程包括：
1. 使用PyTac3D.DataLoader加载本地保存的录制数据
2. 使用PyTac3D.Analyzer.detectContact()函数计算数据帧中的接触区域信息
3. 从数据帧中通过frame['ContactRegion']和frame['ContactRegions']获取总接触区域和各独立接触区域的信息，包括：接触点和接触面积
4. 使用PyTac3D.Sensor和PyTac3D.Displayer可视化触觉数据

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
path = os.path.join(os.path.split(PyTac3D.__file__)[0], 'example_data/example_1')

# Sensor SN of the recorded data
# 录制数据的传感器SN
SN = 'AD2-0065L'

# Create DataLoader to load data from example_data/example_1 directory with specified SN
# 创建DataLoader用于加载example_data/example_1目录下指定SN传感器录制的数据
loader = PyTac3D.DataLoader(path, SN, skip=0)

# Create Analyzer instance for processing tactile data
# 创建Analyzer用于数据处理
analyzer = PyTac3D.Analyzer(SN)

# Create sensor view with default color preset for visualization
# 创建一个SensorView用于数据可视化
view = PyTac3D.SensorView(SN, PyTac3D.Presets.Mesh_Color_1)

# Set display rotation matrix for this view (identity matrix = no rotation)
# 设置数据展示位置的旋转变换矩阵（单位矩阵表示不旋转）
view.setRotation(
    np.matrix( [[1,0,0],
                [0,1,0],
                [0,0,1],
                ], np.float64)
    )

# Set display position for this view
# 设置数据展示位置的平移变换
view.setTranslation([0,0,-10])

# Configure visualization toggles
# 设置可视化的内容
## Enable mesh display
## 打开网格展示
view.enable_Mesh = True
## Disable point cloud display
## 关闭点云展示
view.enable_Pointcloud = False
## Enable contact visualization
## 打开接触展示
view.enable_Contact = True
## Disable displacements visualization
## 关闭位移场展示
view.enable_Displacements = False
## Disable surface normals visualization
## 关闭表面法线展示
view.enable_Normals = False
## Enable distributed forces visualization
## 打开分布力展示
view.enable_Forces = True
## Enable object visualization
## 打开物体（接触区3D形状估计）展示
view.enable_Object = True
## Disable resultant force display
## 关闭合力展示
view.enable_3D_ResForce = False
## Disable resultant moment display
## 关闭合力矩展示
view.enable_3D_ResMoment = False

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

# Add configured view to the displayer
# 将设置好的SenserView视角添加到显示窗口
displayer.addView(view)

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
        # Reset loader to start of data
        # 重置DataLoader到起始位置
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

    # Process and display current frame if available
    # 如果成功获取到数据帧，则进行处理和展示
    if frame:
        # Detect contact regions in current frame
        # 检测当前帧中的接触区域
        # ref: help(PyTac3D.Analyzer.detectContact)
        analyzer.detectContact(frame)

        # Update 3D visualization
        # 更新3D可视化画面
        view.put(frame) 

        # Extract and print contact information
        # 获取并打印接触信息
        ## Boolean array of contacted points
        ## bool类型的数组，表示每个点是否为接触状态
        pointsIsContacted = np.squeeze(frame['ContactRegion']['region'])
        ## Total number of contacted points
        ## 接触点的总数
        contactPointsNum = frame['ContactRegion']['area']

        print('=========================================')
        print('Contact points number: %d' % contactPointsNum)
        print('%d contact regions detected.' % len(frame['ContactRegions']))

        ## The following lines are commented out but could show detailed contact info:
        ## 以下代码可获取和展示接触点的具体数据：
        # print('Contact points positions:', frame['3D_Positions'][pointsIsContacted,:])
        # print('Contact points displacements:', frame['3D_Displacements'][pointsIsContacted,:])
        # print('Contact points forces:', frame['3D_Forces'][pointsIsContacted,:])
        # print('Contact points localforces:', frame['LocalForces'][pointsIsContacted,:])

        # Print information for each contact region
        # 打印每一个独立接触区域的信息
        for i in range(len(frame['ContactRegions'])):
            region = frame['ContactRegions'][i]
            print('  region %d:' % (i+1))
            ## Boolean array of contacted points in this region
            ## bool类型的数组，表示每个点是否在当前接触区内
            pointsIsContacted_in_this_region = np.squeeze(region['region'])
            ## Number of contacted points in this region
            ## 当前接触区域的接触点数
            contactPointsNum_in_this_region = np.squeeze(region['area'])
            print('    Contact points number: %d' % contactPointsNum_in_this_region)

            ## Similar detailed info for this specific region:
            ## 以下代码可获取和展示接触点的具体数据：
            # print('    Contact points:', frame['3D_Positions'][pointsIsContacted_in_this_region,:])
            # print('    Contact points displacements:', frame['3D_Displacements'][pointsIsContacted_in_this_region,:])
            # print('    Contact points forces:', frame['3D_Forces'][pointsIsContacted_in_this_region,:])
            # print('    Contact points localforces:', frame['LocalForces'][pointsIsContacted_in_this_region,:])
    
    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(dt)

