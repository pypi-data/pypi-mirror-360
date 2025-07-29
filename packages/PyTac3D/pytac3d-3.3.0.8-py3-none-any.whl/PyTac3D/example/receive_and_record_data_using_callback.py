'''
Example: receive_and_record_data_using_callback.py

This example demonstrates how to use callback functions to record data from a running Tac3D tactile sensor in real time and save it to a local computer.

The main implementation process includes:
1. Using PyTac3D.Sensor's callback function to receive data frames from the Tac3D main program in real time
2. Recording and saving data frames using PyTac3D.DataRecorder
3. Visualizing tactile data with PyTac3D.Sensor and PyTac3D.Displayer

Note: 
PyTac3D.Sensor only has the capability to receive Tac3D data frames. When using this example, please ensure:
- The Tac3D main program is already running
- The SDK receiving port is set to 9988 (the port used in this example)
Refer to the Tac3D Tactile Sensor User Manual for instructions on launching the Tac3D main program.

本示例主要展示如何使用回调函数实时地从运行中的Tac3D触觉传感器记录数据并保存到本地计算机

主要实现过程包括：
1. 使用PyTac3D.Sensor的回调函数实时接收Tac3D主程序发送的触觉数据帧
2. 使用PyTac3D.DataRecorder记录和保存数据帧
3. 使用PyTac3D.Sensor和PyTac3D.Displayer可视化触觉数据

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

# Directory path to save recorded data
# 保存录制数据的路径
path = 'example_save_data'
# Prompt user to input sensor SN
# 提示用户输入所使用的触觉传感器的SN
SN = PyTac3D.Presets.inputSN()

# Initialize DataRecorder for recording sensor data
# 初始化DataRecorder用于录制传感器数据
recorder = PyTac3D.DataRecorder(SN)

# Define callback function for receiving incoming data frames
# Using callback instead of Sensor.getFrame() helps prevent frame loss during recording.
# Ensure the callback function completes execution promptly (before the next frame arrives). Otherwise, it may still cause frame drops.
# 定义用于接受传感器数据帧的回调函数
# 相比使用Sensor.getFrame()，使用回调函数获取数据帧能够最大可能避免丢帧
# 但需要确保回调函数中的代码必须及时执行完毕（在下一帧数据到来前），否则仍会导致丢帧
def callback(frame, param):
    """
    Frame processing callback function.

    Args:
        frame: Dictionary containing sensor frame data
        param: Custom additional parameters (not used in this example, can be specified using PyTac3D.Sensor(..., callbackParam=xxx))

    数据帧接收回调函数，会在每次接收到触觉数据帧时自动调用。

    参数：
        frame: 包含触觉传感器数据的Dict
        param: 自定义的额外参数 (本例程中没有使用，可使用PyTac3D.Sensor(..., callbackParam=xxx)指定)
    """

    # Only process frames from target sensor
    if frame['SN'] == SN:
        # Save frame to recorder
        recorder.put(frame)

# Initialize PyTac3D.Sensor instance with callback and port configuration
# Port 9988 is commonly used for Tac3D sensor communication
# 创建PyTac3D.Sensor实例并指定接收回调函数和数据接收端口
# 端口9988是Tac3D传感器默认使用的数据传输端口
sensor = PyTac3D.Sensor(recvCallback=callback, port=9988)

# Wait until the first frame from the specified tactile sensor is received
# 等待接收来自指定触觉传感器的数据
sensor.waitForFrame(SN)

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
# 设置可视化的内容
## Enable mesh display
## 打开网格展示
view.enable_Mesh = True
## Disable point cloud display
## 关闭点云展示
view.enable_Pointcloud = False
## Disable contact visualization
## 关闭接触展示
view.enable_Contact = False
## Disable displacements visualization
## 关闭位移场展示
view.enable_Displacements = False
## Disable surface normals visualization
## 关闭表面法线展示
view.enable_Normals = False
## Enable distributed forces visualization
## 打开分布力展示
view.enable_Forces = True
## Disable object visualization
## 关闭物体（接触区3D形状估计）展示
view.enable_Object = False
## Enable resultant force display
## 打开合力展示
view.enable_3D_ResForce = True
## Enable resultant moment display
## 打开合力矩展示
view.enable_3D_ResMoment = True

# Button callback function definitions
# 按钮回调函数定义
def buttonCallback_Restart():
    # Placeholder for restart function (only required when replay the recorded data.)
    # 重新回放函数（只在回放录制数据时需要）
    pass

def buttonCallback_Calibrate():
    # Send a calibration signal to the main program of the Tac3D sensor.
    # 向Tac3D主程序发送校准信号
    sensor.calibrate(SN)

# Create Displayer with lighting preset
# 创建显示窗口Displayer，使用预设的光源设置
displayer = PyTac3D.Displayer(PyTac3D.Presets.Lights_1)
displayer.buttonCallback_Restart = buttonCallback_Restart
displayer.buttonCallback_Calibrate = buttonCallback_Calibrate

# Add configured view to the displayer
# 将设置好的SenserView视角添加到显示窗口
displayer.addView(view)

# Main display loop
# 主显示循环
while displayer.isRunning():
    # Retrieve a frame of data from the receive buffer; return None if the buffer is empty.
    # 从接收缓冲区中获取一帧数据；如果缓冲区中没有数据帧则返回None
    frame = sensor.getFrame(SN)

    # Process and display current frame if available
    # 如果成功获取到数据帧，则进行处理和展示
    if frame:
        # Update 3D visualization
        # 更新3D可视化画面
        view.put(frame)

    # Wait for next update cycle
    # 等待下一次更新
    time.sleep(0.03)

# Save recorded data to specified path when displayer exits
# 在displayer退出时，将录制的数据保存到指定路径
recorder.save(path)

# Clear recorder buffer after saving
# 保存后清理录制缓冲区
recorder.clear()

