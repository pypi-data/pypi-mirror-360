'''
Example: analyze_frame_data.py

This example demonstrates how to use PyTac3D.Analyzer for analyzing and converting tactile data.

Main contents include:
1. Loading locally recorded data using PyTac3D.DataLoader
2. Calculating contact area information in data frames using PyTac3D.Analyzer.detectContact()
3. Estimating 3D geometric shape of contact areas using PyTac3D.Analyzer.detectObjects()
4. Converting point-set tactile data into image format using PyTac3D.Analyzer.points2matrix()
5. Resampling point-set tactile data using PyTac3D.Analyzer.resample()
6. Visualizing tactile data using PyTac3D.Sensor and PyTac3D.Displayer

Note: For routines that acquire data frames from sensors in real time, please refer to:
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py

本示例主要展示如何使用PyTac3D.Analyzer对触觉数据进行分析和转换

主要内容包括：
1. 使用PyTac3D.DataLoader加载本地保存的录制数据
2. 使用PyTac3D.Analyzer.detectContact()函数计算数据帧中的接触区域信息
3. 使用PyTac3D.Analyzer.detectObjects()函数估计接触区域的3D几何形状
4. 使用PyTac3D.Analyzer.points2matrix()函数将点集形式的触觉数据转换为图像形式
5. 使用PyTac3D.Analyzer.resample()函数将点集形式的触觉数据进行重采样
6. 使用PyTac3D.Sensor和PyTac3D.Displayer可视化触觉数据

注：实时从传感器获取数据帧的例程请参阅：
real_time_object_detect.py
receive_and_record_data_using_callback.py
receive_from_multiple_sensors.py
receive_from_single_sensor.py
'''

# Library for Tac3D Sensor
# Tac3D传感器的库
import PyTac3D

import time
import numpy as np
import cv2
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
analyzer= PyTac3D.Analyzer(SN)

# Create sensor view with default color preset for visualization
# 创建一个SensorView用于数据可视化
view  = PyTac3D.SensorView(SN, PyTac3D.Presets.Mesh_Color_1)

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

# Set display position for this view
# 设置数据展示位置的平移变换
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

# Create OpenCV windows for displaying data in image format
cv2.namedWindow('force', 0)
cv2.namedWindow('displacements', 0)
cv2.namedWindow('resample_force', 0)

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
        print()
        print('Frame index:', frame['index'])

        # Contact detection analysis
        print('  ==Before detectContact==')
        print('    ContactRegion:', type(frame.get('ContactRegion')))
        print('    ContactRegions:', type(frame.get('ContactRegions')))
        
        # Detect contact regions in current frame
        # 检测当前帧中的接触区域
        # ref: help(PyTac3D.Analyzer.detectContact)
        analyzer.detectContact(frame)
        print('  ==After detectContact==')
        print('    ContactRegion:', type(frame.get('ContactRegion')))
        print('    ContactRegions:', type(frame.get('ContactRegions')))

        # Object (plane, sphere and cylinder) detection analysis
        # 接触物体（平面、球体和圆柱体）检测
        # ref: help(PyTac3D.Analyzer.detectContact)
        print('  ==Before detectObjects==')
        regions = frame.get('ContactRegions')
        for region in regions:    
            print('    object:', type(region.get('object')))

        # Detect geometry
        # 检测几何体接触物体（接触区3D形状）检测
        # ref: help(PyTac3D.Analyzer.detectObjects)
        analyzer.detectObjects(frame)
        print('  ==After detectObjects==')
        regions = frame.get('ContactRegions')
        for region in regions:    
            print('    object:', region.get('object'))

        # Convert 3D displacement and force data to OpenCV image format
        # 将3D变形场和分布力转换为OpenCV的图像形式
        Dmat = analyzer.points2matrix(frame['3D_Displacements'])
        Fmat = analyzer.points2matrix(frame['3D_Forces'])

        # Display force and displacement matrices as images
        # 以图像形式展示分布力和
        cv2.imshow('force', Fmat * 10.0 + 0.5)
        cv2.imshow('displacements', Dmat * 1.0 + 0.5)

        # Resample the initial 20x20 sample point distribution force to 40x40 (this operation improves visual quality but alters the hardware resolution)
        # 将初始为20x20采样点的分布力重采样为40x40（此操作可改善视觉效果，但会改变硬件的分辨率）
        resampleShape = (40, 40) 
        F_resample = analyzer.resample(frame['3D_Forces'], shape_out=resampleShape)
        Fmat_resample = analyzer.points2matrix(F_resample, shape=resampleShape)
        cv2.imshow('resample_force', Fmat_resample * 10.0 + 0.5)

        # Update 3D visualization
        # 更新3D可视化画面
        view.put(frame)

        # Wait for next update cycle
        # 等待下一次更新
        cv2.waitKey(int(dt*1000))
    else:
        # Wait for next update cycle
        # 等待下一次更新
        time.sleep(dt)

