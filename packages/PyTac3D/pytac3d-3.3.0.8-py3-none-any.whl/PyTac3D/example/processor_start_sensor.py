'''
Example: processor_start_sensor.py

This example demonstrates how to use `PyTac3D.Manager` to launch the Tac3D sensor's main program on a processor.

The main implementation process includes:
1. Using `PyTac3D.Manager` to detect processors in the network where the specified network adapter resides
2. Establishing a command connection with processor of the specified ID
3. Writing the Tac3D tactile sensor's configuration file to the processor
4. Launching the Tac3D sensor's main program on the processor

Note: Processors are optional devices that can run the Tac3D main program to reduce CPU load on computers.

本示例主要展示如何使用`PyTac3D.Manager`在处理模块上启动Tac3D传感器的主程序

主要实现过程包括：
1. 使用`PyTac3D.Manager`检测指定网卡所在的网络中的处理模块
2. 与指定ID的处理模块建立指令连接
3. 向处理模块写入Tac3D触觉传感器的配置文件
4. 在处理模块上启动Tac3D传感器的主程序

注：处理模块为选配产品，可用于运行Tac3D触觉传感器的主程序，以降低计算机的CPU负荷。
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

# Add new Tac3D configuration file to the processor
# The input string should be a local path to a .tcfg configuration file！！
# 向处理模块中添加新的Tac3D配置文件
# 传入的字符串为.tcfg格式的配置文件在本机的路径
# manager.add_config("path/to/your/config/file/DL1-0001.tcfg")

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

# Start the Tac3D sensor main program using the specified configuration file
# Ensure the sensor with corresponding SN is connected to the processer before starting
# Input parameters:
# - Configuration file name (usually matches the sensor SN)
# - IP address for SDK data reception
# - Port for SDK data reception (default: 9988)
# 使用指定的配置文件启动Tac3D传感器主程序，启动时需确保对应SN的传感器连接在处理模块上
# 传入的参数分别为：
# - 配置文件名称（一般情况下与传感器SN相同）
# - SDK接收数据的IP地址
# - SDK接收数据的端口，默认为9988
manager.run_tac3d(cfg_list[2], "192.168.2.10", 9988)

# Check if the Tac3D sensor main program is running on the processer
# 检查处理模块上Tac3D传感器主程序是否正在运行
idx = 2
print(manager.stat_tac3d(cfg_list[idx]))

###########################################################
# At this point, the Tac3D main program startup process on the processer is complete
# 至此，处理模块上的Tac3D主程序启动流程完成
###########################################################
