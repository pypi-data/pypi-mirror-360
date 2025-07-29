'''
Example: get_force_and_displacement_data.py

This example demonstrates how to extract contact distribution forces and deformation field data from Tac3D tactile sensor frames.

Main contents include:
1. Loading locally recorded sensor data using PyTac3D.DataLoader
2. Retrieving various data types from frames using frame.get(), including: basic frame information, surface point positions, surface normals, deformation fields, contact distribution forces, resultant contact forces, and resultant moments.
3. Visualizing tactile data using PyTac3D.Sensor and PyTac3D.Displayer

Note: For routines that acquire data frames from sensors in real time, please refer to:
- real_time_object_detect.py
- receive_and_record_data_using_callback.py
- receive_from_multiple_sensors.py
- receive_from_single_sensor.py

本示例主要展示如何从Tac3D触觉传感器的数据帧中获取接触分布力和变形场数据

主要实现过程包括：
1. 使用PyTac3D.DataLoader加载本地保存的录制数据
2. 使用frame.get()从数据帧中获取数据，包括：基本帧信息、表面点位置、表面法线、变形场、接触分布力、接触合力以及合力矩等。
3. 使用PyTac3D.Sensor和PyTac3D.Displayer可视化触觉数据

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

# Configure visualization toggles
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
    restartFlag = True # Set flag to restart playback

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
        # Update 3D visualization
        # 更新3D可视化画面
        view.put(frame)

        # Get the sensor's SN, which can be used to distinguish which Tac3D sensor the tactile information comes from
        # 获取传感器的SN。SN可用于区分产生此帧数据的触觉传感器
        SN = frame['SN']
        print()
        # Print sensor SN
        # 打印传感器SN
        print('Sensor SN:', SN)
        
        # Get and print frame metadata
        # 获取帧的基本数据
        ## Frame index
        ## 帧的编号
        frameIndex = frame['index']
        print('Frame index:', frameIndex)

        ## Send time stamp (Start timing when the Tac3D main program initializes)
        ## 发送时间戳（从Tac3D主程序启动开始计时）
        sendTimestamp = frame['sendTimestamp']
        ## Receive time stamp (Start timing when the creation of a PyTac3D.Sensor instance)
        ## 接收时间戳（从PyTac3D.Sensor实例创建开始计时）
        recvTimestamp = frame['recvTimestamp']

        # Use the frame.get function to obtain the 3D shape in the numpy.array type through the data name "3D_Positions"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # Each row of the matrix corresponds to a sensing point
        # 使用frame.get函数通过数据名称"3D_Positions"获得numpy.array类型的三维形貌数据
        # 矩阵的3列分别为x,y,z方向的分量
        # 矩阵的每行对应一个测量点
        P = frame.get('3D_Positions')
        print('shape of P:', P.shape)

        # Use the frame.get function to obtain the surface normal in the numpy.array type through the data name "3D_Normals"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # Each row of the matrix corresponds to a sensing point
        # 使用frame.get函数通过数据名称"3D_Normals"获得numpy.array类型的表面法线数据
        # 矩阵的3列分别为x,y,z方向的分量
        # 矩阵的每行对应一个测量点
        N = frame.get('3D_Normals')
        print('shape of N:', N.shape)

        # Use the frame.get function to obtain the displacement field in the numpy.array type through the data name "3D_Displacements"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # Each row of the matrix corresponds to a sensing point
        # 使用frame.get函数通过数据名称"3D_Displacements"获得numpy.array类型的三维变形场数据
        # 矩阵的3列分别为x,y,z方向的分量
        # 矩阵的每行对应一个测量点
        D = frame.get('3D_Displacements')
        print('shape of D:', D.shape)

        # Use the frame.get function to obtain the distributed force in the numpy.array type through the data name "3D_Forces"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # Each row of the matrix corresponds to a sensing point
        # 使用frame.get函数通过数据名称"3D_Forces"获得numpy.array类型的三维分布力数据
        # 矩阵的3列分别为x,y,z方向的分量
        # 矩阵的每行对应一个测量点
        F = frame.get('3D_Forces')
        print('shape of F:', F.shape)

        # Use the frame.get function to obtain the resultant force in the numpy.array type through the data name "3D_ResultantForce"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # 使用frame.get函数通过数据名称"3D_ResultantForce"获得numpy.array类型的三维合力的数据指针
        # 矩阵的3列分别为x,y,z方向的分量
        Fr = frame.get('3D_ResultantForce')
        print('shape of Fr:', Fr.shape)
        print('Resultant Force:', Fr)

        # Use the frame.get function to obtain the resultant moment in the numpy.array type through the data name "3D_ResultantMoment"
        # The three columns of the matrix are the components in the x, y, and z directions, respectively
        # 使用frame.get函数通过数据名称"3D_ResultantMoment"获得numpy.array类型的三维合力的数据指针
        # 矩阵的3列分别为x,y,z方向的分量
        Mr = frame.get('3D_ResultantMoment')
        print('shape of Mr:', Mr.shape)
        print('Resultant Moment:', Mr)

    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(dt)

