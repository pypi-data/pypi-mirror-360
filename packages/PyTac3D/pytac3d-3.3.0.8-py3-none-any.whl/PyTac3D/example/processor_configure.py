'''
Example: processor_configure.py

This example demonstrates how to use `PyTac3D.Manager` to modify the network configuration of Tac3D Processors.

Main implementation steps include:
1. Using `PyTac3D.Manager` to detect processors in the network of a specified network interface
2. Reading the network configuration of a processor with specified ID
3. Writing new network configuration to a processor with specified ID
4. Restarting the interface to apply changes

Note: Processors are optional devices that can run the Tac3D main program to reduce CPU load on computers.

本示例主要展示如何使用`PyTac3D.Manager`更改处理模块的网络配置

主要实现过程包括：
1. 使用`PyTac3D.Manager`检测指定网卡所在的网络中的处理模块
2. 读取指定ID的处理模块的网络配置
3. 向指定ID的处理模块写入新的网络配置
4. 重启网络配置使更改生效

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
# `manager.get_tp_id()`返回可连接的处理模块列表
# `tp_num`为检测到的可用的处理模块的数量
# `tp_list`为检测到的可用的处理模块的序列号的列表
# 当计算机和多个处理模块连接在同一个交换机上时，可同时检测到多个处理模块
tp_num, tp_list = manager.get_tp_id()
print('{} processor(s) detected {}.'.format(tp_num, str(tp_list)))


# Retrieve the serial number of the first detected processors from the list
# 从列表中取出检测到的第一个处理模块的序列号
tp_id = tp_list[0]

# Obtain the network configuration information of the processors
# Includes IP address, subnet mask, and gateway
# 获取处理模块的网络配置信息
# 包括IP地址、子网掩码和网关
ip, netmask, gateway = manager.get_run_ip(tp_id)

# Set new network configuration for the processor corresponding to tp_id:
# This operation is required when:
# 1. There are network address conflicts among processors (e.g., multiple processors have the same factory-default IP address 192.168.2.100 in the same LAN)
# 2. The processor's IP address and the computer's network interface are not on the same subnet
# 为tp_id对应序列号的处理模块设置新的网络配置：
# 当处理模块的网络地址存在冲突（如多个处理模块出厂默认IP地址均为192.168.2.100，但又需要连接在用一个局域网内）
# 或处理模块的IP地址与本地计算机网卡的IP地址不处于同一网段时需要进行此设置
new_ip = "192.168.2.100"
new_netmask = "255.255.255.0"
new_gateway = "192.168.2.1"
manager.set_config_ip(tp_id, new_ip, new_netmask, new_gateway)

# After modifying the network configuration, the processor's network interface must be restarted
# 更给处理模块的网络配置后需要让处理模块重启网络接口
manager.interface_restart(tp_id)

# To obtain the new IP address and other network configuration settings.
# 重新获取IP地址和其他网络配置
ip, netmask, gateway = manager.get_run_ip(tp_id)

