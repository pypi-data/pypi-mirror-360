'''
Example: processor_stop_sensor.py

This example mainly demonstrates how to use `PyTac3D.Manager` to stop the Tac3D sensor's main program on the processor.

The key implementation steps include:
1. Using PyTac3D.Manager to detect processors on the network of the specified network interface
2. Establishing a command connection with the processor of the specified ID
3. Stopping the Tac3D sensor's main program currently running on the processor
4. Retrieving the logs of the Tac3D sensor from the processor

Note: 
- Processors are optional devices that can run the Tac3D main program to reduce CPU load on computers.
- Before starting or stopping the Tac3D sensor's main program running on the processor, ensure that the correct network configuration has been completed by referring to `processor_configure.py`
- The example for starting the Tac3D sensor's main program on the processor is provided in `processor_start_sensor.py`

本示例主要展示如何使用`PyTac3D.Manager`在处理模块上停止Tac3D传感器的主程序

主要实现过程包括：
1. 使用PyTac3D.Manager检测指定网卡所在的网络中的处理模块
2. 与指定ID的处理模块建立指令连接
3. 停止在处理模块上正在运行的Tac3D传感器的主程序
4. 获取处理模块上指定SN的传感器的运行日志

注：
- 处理模块为选配产品，可用于运行Tac3D触觉传感器的主程序，以降低计算机的CPU负荷
- 在启动和停止运行在处理模块上的Tac3D传感器的主程序之前，请确保已参照`processor_configure.py`完成了正确的网络设置
- 在处理模块上启动Tac3D传感器的主程序的例程见`processor_start_sensor.py`
'''

# Library for Tac3D Sensor
# Tac3D传感器的库
import PyTac3D

# GUI Tool: https://gitee.com/sxhzzlw/tac3d-utils/tree/master/Tac3D_Simple_GUI
# GUI工具：https://gitee.com/sxhzzlw/tac3d-utils/tree/master/Tac3D_Simple_GUI

# PyTac3D.Manager primarily handles communication with Tac3D Processor,
# modify the network configuration, and starts/stops sensors connected to the processor
# PyTac3D.Manager的主要功能是与处理模块（Tac3D Processor）通信
# 更改处理模块的参数设置，启动或停止处理模块上连接的传感器

# Initialize PyTac3D.Manager
# The IP address passed here belongs to the network interface connecting the local computer to the processor
# This IP address must be manually configured as a static IP
# 初始化PyTac3D.Manager
# 此处传入的IP地址为本地计算机与处理模块连接的网卡的IP地址
# 此IP地址需要手动设置为静态IP
manager = PyTac3D.Manager("192.168.2.10")

# `manager.get_tp_id()` retrieve list of connectable processors
# `tp_num` is the number of available processors detected
# `tp_list` is a list of serial numbers for the available processors detected
# When computers and multiple processors are connected within the same local area network, these processors can be detected simultaneously
# `manager.get_tp_id()` 返回可连接的处理模块列表
# `tp_num`为检测到的可用的处理模块的数量
# `tp_list`为检测到的可用的处理模块的序列号的列表
# 当计算机和多个处理模块连接在同一个交换机上时，可同时检测到多个处理模块
tp_num, tp_list = manager.get_tp_id()

# Retrieve the serial number of the first detected processors from the list
# 从列表中取出检测到的第一个处理模块的序列号
tp_id = tp_list[0]

# Obtain the network configuration information of the processors
# Includes IP address, subnet mask, and gateway
# 获取处理模块的网络配置信息
# 包括IP地址、子网掩码和网关
ip, netmask, gateway = manager.get_run_ip(tp_id)
        
# Establish command connection with specified processor via IP address for Tac3D sensor operations
# 通过指定IP地址，与指定的处理模块建立指令连接，以执行有关Tac3D传感器的操作
manager.connect_server(ip)

# `manager.get_config()` returns the list of imported configuration files
# `cfg_num` is the number of configuration files imported in the processor
# `cfg_list` contains the names of configuration files imported in the processor
# `sn_list` contains the sensor SNs corresponding to the imported configuration files
# Normally the contents of `cfg_list` and `sn_list` are identical
# `manager.get_config()`返回已导入的配置文件列表
# `cfg_num`为处理模块中已导入的配置文件数量
# `cfg_list`为处理模块中已导入的配置文件名称的列表
# `sn_list`为处理模块中已导入的配置文件对应的传感器SN的列表
# 通常情况下`cfg_list`与`sn_list`的内容是相同的
cfg_num, cfg_list, sn_list = manager.get_config()
print('{} configuration file(s) found on the processor {}.'.format(cfg_num, str(sn_list)))

# Check if the Tac3D sensor main program is running on the processer
# 检查处理模块上Tac3D传感器主程序是否正在运行
idx = 0
isSensorRunning = manager.stat_tac3d(cfg_list[idx])
print('isSensorRunning: ', isSensorRunning)

###########################################################
# The following code is to terminate the Tac3D main program, export logs, and shut down the processor power
# 以下代码功能为中止Tac3D主程序、导出日志并关闭处理模块电源
###########################################################

# Terminates the Tac3D sensor main program with specified SN on the process哦人
# 中止处理模块上指定SN的Tac3D传感器主程序
manager.stop_tac3d(cfg_list[idx])

# Extracts the runtime logs of the Tac3D sensor main program with specified SN from the processor. When sensor startup or operation exceptions occur, please provide this log to technical personnel for troubleshooting
# 从处理模块中提取指定SN的Tac3D传感器主程序运行日志，在传感器启动或运行异常时，请向技术人员提供此日志以排查故障原因
manager.get_log(sn_list[idx], sn_list[idx] + "_log.zip")

# Disconnects from the processor. This operation only terminates the command connection between the manager and the processor; it does not stop the Tac3D main program from running
# 断开与处理模块的连接，此操作只会断开manager与处理模块的命令连接，不会停止Tac3D主程序的运行
manager.disconnect_server()

# Powers off the specified processor (requires pressing the power button to restart)
# 关闭指定的处理模块（需要按电源键才能再次开机）
# manager.system_shutdown(tp_id)
