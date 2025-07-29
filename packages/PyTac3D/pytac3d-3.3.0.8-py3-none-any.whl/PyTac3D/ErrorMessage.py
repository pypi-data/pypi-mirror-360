
# version: 3.3.0

errMsgDict_zh = {0x00:  '',
                 0x41: '配置文件无效',
                 0x42: '核心程序无法建立网络连接（配置错误）',
                 0x43: '核心程序无法建立网络连接（配置错误）',
                 0x44: '核心程序无法建立网络连接（端口无效）',
                 0x45: '核心程序无法建立网络连接（数据接收地址无效）',
                 0x46: '命令行参数错误',
                 0x47: '连接传感器失败（无法获取图像输入）',
                 0x48: '初始帧特征匹配失败，请检查配置文件和传感器的SN是否对应，并确保启动时弹性体未被接触',
                 0x49: '内部错误（缓存数据命名冲突）',
                 0x4A: '与传感器的连接断开',
                 0x4B: '内部错误（RKMPP初始化失败）',
                 0x4C: '内部错误（RKMPP运行时错误）',
                 0x4D: '配置文件版本不在支持的范围内，请升级应用程序',
                 0x4E: '连接传感器失败（未检测到与配置文件匹配的传感器设备）',
                 0xFF: '未知错误',
                    }

errMsgDict_en = {0x00:  '',
                 0x41: 'Invalid configuration file',
                 0x42: 'Core program failed to establish network connection (configuration error)',
                 0x43: 'Core program failed to establish network connection (configuration error)',
                 0x44: 'Core program failed to establish network connection (invalid port)',
                 0x45: 'Core program failed to establish network connection (invalid data reception address)',
                 0x46: 'Command line parameter error',
                 0x47: 'Failed to connect to sensor (unable to acquire image input)',
                 0x48: 'Excessive feature matching errors - please verify the configuration file matches the sensor SN and ensure the elastomer is not contacted during startup',
                 0x49: 'Internal error (cache data naming conflict)',
                 0x4A: 'Connection to sensor lost',
                 0x4B: 'Internal error (RKMPP initialization failed)',
                 0x4C: 'Internal error (RKMPP runtime error)',
                 0x4D: 'Configuration file version not supported - please upgrade the application',
                 0x4E: 'Failed to connect to sensor (no matching sensor device detected for the configuration)',
                 0xFF: 'Unknown error',
                }


def getErrMsg(errCode, language='zh'):
    if language == 'zh':
        msgDict = errMsgDict_zh
    elif language == 'en':
        msgDict = errMsgDict_en

    msg = msgDict.get(errCode)
    if msg is None:
        msg = msgDict.get(0xFF)
    return msg
    
if __name__ == '__main__':
    print(getErrMsg(0xF99))
    print(getErrMsg(0x43))
    print(getErrMsg(0xF99, 'zh'))
    print(getErrMsg(0x43, 'zh'))
    print(getErrMsg(0xF99, 'en'))
    print(getErrMsg(0x43, 'en'))
    print(getErrMsg(0xF99, 'en'))
    print(getErrMsg(0x43, 'en'))
