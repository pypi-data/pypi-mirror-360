import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import time
import os
import sys
import zipfile
import shutil
import subprocess
from datetime import datetime
import appdirs
import requests
from tqdm import tqdm
import netifaces
import ipaddress

from . import ErrorMessage
from . import Manager

appName = 'tac3d'

def download_with_progress(url, save_path):
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(save_path, 'wb') as f, tqdm(
            desc=save_path,
            total=total_size,
            unit='iB',
            unit_scale=True
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                size = f.write(chunk)
                bar.update(size)
            return True
    except Exception as e:
        print(f"Download failed: {str(e)}")
        return False

class ProcessorFrame:
    def __init__(self, parent):
        self.processorSettingsFrame = parent
        
        currRow = 0
        self.labelLocalIP = tk.Label(self.processorSettingsFrame, text='Local IP')
        self.labelLocalIP.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.comboLocalIP = ttk.Combobox(self.processorSettingsFrame)
        self.comboLocalIP.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        self.comboLocalIP.bind("<<ComboboxSelected>>", self.onSelectLocalIP)
        
        currRow += 1
        self.buttonDetect = tk.Button(self.processorSettingsFrame, text='Detect Processor', command=self.detectProcessor)
        self.buttonDetect.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.varTpSN = tk.StringVar()
        self.labelTpSN = tk.Label(self.processorSettingsFrame, text='Processor SN')
        self.labelTpSN.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.comboTpSN = ttk.Combobox(self.processorSettingsFrame, textvariable=self.varTpSN)
        self.comboTpSN.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        self.comboTpSN.bind("<<ComboboxSelected>>", self.tpSNChange)

        currRow += 1
        self.varProcIP = tk.StringVar()
        self.labelProcIP = tk.Label(self.processorSettingsFrame, text='Processor IP')
        self.labelProcIP.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entryProcIP = tk.Entry(self.processorSettingsFrame, textvariable=self.varProcIP)
        self.entryProcIP.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.varProcMask = tk.StringVar()
        self.labelProcMask = tk.Label(self.processorSettingsFrame, text='Processor Netmask')
        self.labelProcMask.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entryProcMask = tk.Entry(self.processorSettingsFrame, textvariable=self.varProcMask)
        self.entryProcMask.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.varProcGate = tk.StringVar()
        self.labelProcGate = tk.Label(self.processorSettingsFrame, text='Processor Gateway')
        self.labelProcGate.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entryProcGate = tk.Entry(self.processorSettingsFrame, textvariable=self.varProcGate)
        self.entryProcGate.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonUpdateNet = tk.Button(self.processorSettingsFrame, text='Apply Network Configuration', command=self.updateNet)
        self.buttonUpdateNet.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonConnect = tk.Button(self.processorSettingsFrame, text='Connect Processor', command=self.connectProcessor)
        self.buttonConnect.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonDisconnect = tk.Button(self.processorSettingsFrame, text='Disconnect', command=self.disconnect)
        self.buttonDisconnect.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonPowerOff = tk.Button(self.processorSettingsFrame, text='Power Off', command=self.powerOff)
        self.buttonPowerOff.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.labelTac3DSN = tk.Label(self.processorSettingsFrame, text='Tac3D SN')
        self.labelTac3DSN.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.comboTac3DSN = ttk.Combobox(self.processorSettingsFrame)
        self.comboTac3DSN.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.varSDKIP = tk.StringVar()
        self.labelSDKIP = tk.Label(self.processorSettingsFrame, text='SDK IP')
        self.labelSDKIP.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entrySDKIP = tk.Entry(self.processorSettingsFrame, textvariable=self.varSDKIP)
        self.entrySDKIP.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.varSDKPort = tk.StringVar()
        self.labelSDKPort = tk.Label(self.processorSettingsFrame, text='SDK Port')
        self.labelSDKPort.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entrySDKPort = tk.Entry(self.processorSettingsFrame, textvariable=self.varSDKPort)
        self.entrySDKPort.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonUpdate = tk.Button(self.processorSettingsFrame, text='Refresh', command=self.updateTac3DList)
        self.buttonUpdate.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonImport = tk.Button(self.processorSettingsFrame, text='Import Configuration File', command=self.importConfig)
        self.buttonImport.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonDelete = tk.Button(self.processorSettingsFrame, text='Delete Configuration File', command=self.deleteConfig)
        self.buttonDelete.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonStart = tk.Button(self.processorSettingsFrame, text='Start Sensor', command=self.startSensor)
        self.buttonStart.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonStop = tk.Button(self.processorSettingsFrame, text='Stop Sensor', command=self.stopSensor)
        self.buttonStop.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonExpLog = tk.Button(self.processorSettingsFrame, text='Export Log', command=self.exportLog)
        self.buttonExpLog.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        self.manager = None
        self.buttonState_Disconnect()
        self.getIPList()

    def onSelectLocalIP(self, event):
        selectedIP = self.comboLocalIP.get()
        self.detectProcessor()
        # print(selectedIP)

    def updateNet(self):
        self.manager.set_config_ip(self.comboTpSN.get(), self.varProcIP.get(), self.varProcMask.get(), self.varProcGate.get())
        self.manager.interface_restart(self.comboTpSN.get())
        messagebox.showinfo('Tac3D', 'Update successfully !')
        self.tpSNChange()
        
    def detectProcessor(self, msg = True):

        def btnState_Success():
            self.comboTpSN['state'] = 'readonly'
            self.comboTpSN['values'] = self.tpList
            if not self.comboTpSN.get() in self.tpList:
                self.comboTpSN.set(self.tpList[0])
            self.tpSNChange()
        
        def btnState_Fail():
            self.comboTpSN['state'] = 'disabled'
            self.comboTpSN['values'] = []
            self.comboTpSN.set('')
            self.tpSNChange()

        self.localIP = self.comboLocalIP.get()
        if self.localIP == '':
            btnState_Fail()
            return
        
        print('detect from: ', self.localIP)
        self.manager = Manager(self.localIP)
        num, self.tpList = self.manager.get_tp_id()
        print(self.tpList)

        if len(self.tpList) != 0:
            btnState_Success()
            if msg:
                messagebox.showinfo('Tac3D', '{} processor(s) detected !'.format(num))
        else:
            btnState_Fail()
            if msg:
                messagebox.showinfo('Tac3D', 'No processor detected !')
            
    def tpSNChange(self, *args):
        def ipState_Success():
            self.entryProcIP.configure(background="#FFFFFF") 
            self.entryProcGate.configure(background="#FFFFFF")

        def ipState_Fail():
            self.entryProcIP.configure(background="#EB7D7D") 
            self.entryProcGate.configure(background="#EB7D7D")

        if self.varTpSN.get() != '' and not self.manager is None:
            ip, netmask, gateway = self.manager.get_config_ip(self.varTpSN.get())
            self.varProcIP.set(ip)
            self.varProcMask.set(netmask)
            self.varProcGate.set(gateway)
            self.entryProcIP['state'] = 'normal'
            self.entryProcMask['state'] = 'normal'
            self.entryProcGate['state'] = 'normal'
            self.buttonUpdateNet['state'] = 'normal'

            network1 = ipaddress.IPv4Network(f"{self.localIP}/{netmask}", strict=False)
            network2 = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
            network3 = ipaddress.IPv4Network(f"{gateway}/{netmask}", strict=False)

            print(network1, network2, network3)
            if network1 == network2 and network1 == network3:
                ipState_Success()
                self.buttonConnect['state'] = 'normal'
            else:
                ipState_Fail()
                self.buttonConnect['state'] = 'disabled'

        else:
            self.varProcIP.set('')
            self.varProcMask.set('')
            self.varProcGate.set('')
            self.entryProcIP['state'] = 'disabled'
            self.entryProcMask['state'] = 'disabled'
            self.entryProcGate['state'] = 'disabled'
            self.buttonUpdateNet['state'] = 'disabled'
            ipState_Success()
            self.buttonConnect['state'] = 'disabled'

    def connectProcessor(self):
        self.processorSN = self.comboTpSN.get()
        if self.processorSN == '':
            return
        self.tpSNChange()
        self.manager.connect_server(self.varProcIP.get())
        self.manager.set_time(time.time())
        self.tac3dList = []
        self.buttonState_Connect()
        self.updateTac3DList()
    
    def disconnect(self):
        self.manager.disconnect_server()
        self.manager = None
        self.buttonState_Disconnect()
        self.getIPList()
        self.detectProcessor(False)


    def buttonState_Connect(self):
        self.comboLocalIP['state'] = 'disabled'
        self.buttonDetect['state'] = 'disabled'

        self.comboTpSN['state'] = 'disabled'
        self.entryProcIP['state'] = 'disabled'
        self.entryProcMask['state'] = 'disabled'
        self.entryProcGate['state'] = 'disabled'

        self.buttonUpdateNet['state'] = 'disabled'
        self.buttonConnect['state'] = 'disabled'
        self.buttonDisconnect['state'] = 'normal'
        self.buttonPowerOff['state'] = 'normal'

        self.comboTac3DSN['state'] = 'readonly'
        self.entrySDKPort['state'] = 'normal'
        self.entrySDKIP['state'] = 'normal'

        self.buttonUpdate['state'] = 'normal'
        self.buttonImport['state'] = 'normal'
        self.buttonDelete['state'] = 'normal'
        self.buttonStart['state'] = 'normal'
        self.buttonStop['state'] = 'normal'
        self.buttonExpLog['state'] = 'normal'
        self.varSDKIP.set(self.comboLocalIP.get())
        self.varSDKPort.set('9988')

    def buttonState_Disconnect(self):
        self.comboLocalIP['state'] = 'readonly'
        self.buttonDetect['state'] = 'normal'

        self.comboTpSN['state'] = 'disabled'
        self.entryProcIP['state'] = 'disabled'
        self.entryProcMask['state'] = 'disabled'
        self.entryProcGate['state'] = 'disabled'

        self.buttonUpdateNet['state'] = 'disabled'
        self.buttonConnect['state'] = 'disabled'
        self.buttonDisconnect['state'] = 'disabled'
        self.buttonPowerOff['state'] = 'disabled'

        self.comboTac3DSN['state'] = 'disabled'
        self.entrySDKPort['state'] = 'disabled'
        self.entrySDKIP['state'] = 'disabled'

        self.buttonUpdate['state'] = 'disabled'
        self.buttonImport['state'] = 'disabled'
        self.buttonDelete['state'] = 'disabled'
        self.buttonStart['state'] = 'disabled'
        self.buttonStop['state'] = 'disabled'
        self.buttonExpLog['state'] = 'disabled'

        self.comboTac3DSN.set('')
        self.varSDKIP.set('')
        self.varSDKPort.set('')

    def updateTac3DList(self):
        cfg_num, self.tac3dList, self.tac3dSNlist = self.manager.get_config()
        
        self.comboTac3DSN['values'] = self.tac3dList
        
        if len(self.tac3dList) != 0:
            if not self.comboTac3DSN.get() in self.tac3dList:
                self.comboTac3DSN.set(self.tac3dList[0])
        else:
            self.comboTac3DSN.set('')
        
    def importConfig(self):
        file_path = filedialog.askopenfilename(title='Choose a .tcfg file', filetypes=[('TCFG', '*.tcfg')])
        if file_path:
            self.manager.add_config(file_path)
            self.updateTac3DList()
            messagebox.showinfo('Tac3D', 'Import successfully !')
        
    def deleteConfig(self):
        if self.comboTac3DSN.get() in self.tac3dList:
            result = messagebox.askyesno('Tac3D', 'Confirm delete the configuration file')
            if result:
                self.manager.delete_config(self.comboTac3DSN.get())
                self.updateTac3DList()
                messagebox.showinfo('Tac3D', 'Delete successfully !')
        
    def getIPList(self):
        # hostname = socket.gethostname()
        # self.ipList = socket.gethostbyname_ex(hostname)[2]
        self.ipList = []
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
                self.ipList.extend(addr['addr'] for addr in addrs if not addr['addr'].startswith('127.'))
            except:
                print('[Warning] Unable to obtain the IP address of the network interface named "{}".'.format(interface))
        self.comboLocalIP['values'] = self.ipList

        if not self.comboLocalIP.get() in self.ipList:
            self.comboLocalIP.set('')
                
    def startSensor(self):
        self.manager.run_tac3d(self.comboTac3DSN.get(), self.entrySDKIP.get(), int(self.entrySDKPort.get()))
        if self.manager.stat_tac3d(self.comboTac3DSN.get()):
            messagebox.showinfo('Tac3D', 'Start successfully !')
        else:
            messagebox.showinfo('Tac3D', 'Failed !')
        
    def stopSensor(self):
        if self.manager.stat_tac3d(self.comboTac3DSN.get()):
            self.manager.stop_tac3d(self.comboTac3DSN.get())
        messagebox.showinfo('Tac3D', 'Sensor stoped ! ')

    def exportLog(self):
        logName = self.comboTac3DSN.get() + '_Log_' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.zip'
        self.manager.get_log(self.comboTac3DSN.get(), logName)
        
    def powerOff(self):
        result = messagebox.askyesno('Tac3D', 'Confirm Processor Shutdown')
        if result:
            self.manager.system_shutdown(self.varTpSN.get())
            self.disconnect()
        
    def update(self):
        pass

class LocalFrame:
    def __init__(self, parent):
        self.localSettingsFrame = parent
        self.processes = {}

        self.configDir = os.path.join(appdirs.user_data_dir(appName), 'config')
        self.configPath = os.path.join(self.configDir, 'local.cfg')
        self.coreDir = os.path.join(appdirs.user_data_dir(appName), 'core')
        self.logDir = appdirs.user_log_dir(appName)
        self.tmpDir = appdirs.user_cache_dir(appName)

        self.initFolders()

        if sys.platform.startswith('win'):
            self.pythonName = 'python'
            self.coreUrl = 'https://gitee.com/sxhzzlw/tac3d-utils/releases/download/v3.3.0/Tac3D.exe'
            self.corePath = os.path.join(self.coreDir, 'Tac3D.exe')
        elif sys.platform.startswith('linux'):
            self.pythonName = 'python3'
            self.coreUrl = 'https://gitee.com/sxhzzlw/tac3d-utils/releases/download/v3.3.0/Tac3D'
            self.corePath = os.path.join(self.coreDir, 'Tac3D')

        self.config = {
            'SDK_ip': [tk.StringVar(), '127.0.0.1'],
            'SDK_port': [tk.StringVar(), '9988'],
            }

        currRow = 0

        self.labelTac3DSN = tk.Label(self.localSettingsFrame, text='Tac3D SN')
        self.labelTac3DSN.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.comboLocalTac3DSN = ttk.Combobox(self.localSettingsFrame)
        self.comboLocalTac3DSN.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        self.comboLocalTac3DSN['state'] = 'readonly'

        currRow += 1
        self.labelSDKIP = tk.Label(self.localSettingsFrame, text='SDK IP')
        self.labelSDKIP.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entrySDKIP = tk.Entry(self.localSettingsFrame, textvariable=self.config['SDK_ip'][0])
        self.entrySDKIP.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.labelSDKPort = tk.Label(self.localSettingsFrame, text='SDK Port')
        self.labelSDKPort.grid(row=currRow,column=0, sticky='w e', padx=4, pady=4)
        self.entrySDKPort = tk.Entry(self.localSettingsFrame, textvariable=self.config['SDK_port'][0])
        self.entrySDKPort.grid(row=currRow,column=1, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonUpdate = tk.Button(self.localSettingsFrame, text='Refresh', command=self.updateTac3DList)
        self.buttonUpdate.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonImport = tk.Button(self.localSettingsFrame, text='Import Configuration File', command=self.importConfig)
        self.buttonImport.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonDelete = tk.Button(self.localSettingsFrame, text='Delete Configuration File', command=self.deleteConfig)
        self.buttonDelete.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonStart = tk.Button(self.localSettingsFrame, text='Start Sensor', command=self.startSensor)
        self.buttonStart.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonStop = tk.Button(self.localSettingsFrame, text='Stop Sensor', command=self.stopSensor)
        self.buttonStop.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)
        
        currRow += 1
        self.buttonDisplayer = tk.Button(self.localSettingsFrame, text='Run Displayer', command=self.runDisplayer)
        self.buttonDisplayer.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonExportLog = tk.Button(self.localSettingsFrame, text='Export Logs', command=self.exportLogs)
        self.buttonExportLog.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonCleanTmpFiles = tk.Button(self.localSettingsFrame, text='Clean Temporary Files', command=self.cleanTmpFiles)
        self.buttonCleanTmpFiles.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        currRow += 1
        self.buttonCleanAppData = tk.Button(self.localSettingsFrame, text='Clean App Data', command=self.cleanAppData)
        self.buttonCleanAppData.grid(row=currRow,column=0, columnspan=2, sticky='w e', padx=4, pady=4)

        self.loadConfig()
        self.updateTac3DList()
        
    def initFolders(self):
        if not os.path.isdir(self.configDir):
            os.makedirs(self.configDir)
        if not os.path.isdir(self.coreDir):
            os.makedirs(self.coreDir)
        if not os.path.isdir(self.logDir):
            os.makedirs(self.logDir)
        if not os.path.isdir(self.tmpDir):
            os.makedirs(self.tmpDir)

    def exportLogs(self):
        folder_path = filedialog.askdirectory(
            title='Choose a folder to export logs:',
            mustexist=True
        )
        if folder_path:
            lsDir = os.listdir(self.logDir)
            cnt = 0
            for item in lsDir:
                if os.path.isdir(os.path.join(self.logDir, item)):
                    shutil.copytree(os.path.join(self.logDir, item), os.path.join(folder_path, item))
                    cnt += 1
            messagebox.showinfo('Tac3D', '{} log(s) exported !'.format(cnt))

    def cleanAppData(self):
        result = messagebox.askyesno('Tac3D', 'Confirm to delete app data?\n(config files, Tac3D core, logs and cache)')
        if result:
            if os.path.isdir(self.configDir):
                shutil.rmtree(self.configDir)
            if os.path.isdir(self.coreDir):
                shutil.rmtree(self.coreDir)
            if os.path.isdir(self.logDir):
                shutil.rmtree(self.logDir)
            if os.path.isdir(self.tmpDir):
                shutil.rmtree(self.tmpDir)
            self.initFolders()
            self.updateTac3DList()
            messagebox.showinfo('Tac3D', 'The files have been cleared!')

    def cleanTmpFiles(self):
        result = messagebox.askyesno('Tac3D', 'Confirm to delete temporary files?\n(logs and cache)')
        if result:
            if os.path.isdir(self.logDir):
                shutil.rmtree(self.logDir)
            if os.path.isdir(self.tmpDir):
                shutil.rmtree(self.tmpDir)
            self.initFolders()
            messagebox.showinfo('Tac3D', 'The logs have been cleared!')

    def downloadCore(self):
        tmpPath = os.path.join(self.tmpDir, 'core')
        if os.path.isfile(self.corePath):
            return True
        
        result = messagebox.askyesno('Tac3D', 'Unable to find the Tac3D core program. Would you like to download it now?')
        if result:
            if download_with_progress(self.coreUrl, tmpPath):
                shutil.move(tmpPath, self.corePath)
                return True
            else:
                msg = 'Download failed. You can manually download the file from {} and move it to folder {} .'.format(self.coreUrl, self.coreDir)
                print(msg)
                messagebox.showinfo('Tac3D', msg)
                return False
            
        return False

    def updateTac3DList(self):
        lsDir = os.listdir(self.configDir)
        
        self.tac3dList = []
        tac3dList_status = []
        for item in lsDir:
            if os.path.isdir(os.path.join(self.configDir, item)) and os.path.isfile(os.path.join(self.configDir, item, 'sensor.yaml')):
                if item in self.processes.keys():
                    status = " (running)"
                else:
                    status = " (stopped)"
                self.tac3dList.append(item)
                tac3dList_status.append(item + status)
        self.comboLocalTac3DSN['values'] = tac3dList_status

        if len(tac3dList_status) != 0:
            SN = self.comboLocalTac3DSN.get().split(' ')[0]
            for i in range(len(tac3dList_status)):
                if SN == self.tac3dList[i]:
                    self.comboLocalTac3DSN.set(tac3dList_status[i])
                    return
            self.comboLocalTac3DSN.set(tac3dList_status[0])
        else:
            self.comboLocalTac3DSN.set('')
        
    def importConfig(self):
        file_path = filedialog.askopenfilename(title='Choose a .tcfg file', filetypes=[('TCFG', '*.tcfg')])
        if file_path:
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.configDir)
                messagebox.showinfo('Tac3D', 'Import successfully !')
            except:
                messagebox.showinfo('Tac3D', 'Import Failed !')
        self.updateTac3DList()
        
    def deleteConfig(self):
        SN = self.comboLocalTac3DSN.get().split(' ')[0]
        if SN in self.tac3dList:
            result = messagebox.askyesno('Tac3D', 'Confirm to delete the configuration file')
            if result:
                try:
                    shutil.rmtree(os.path.join(self.configDir, SN))
                    messagebox.showinfo('Tac3D', 'Delete successfully !')
                except:
                    messagebox.showinfo('Tac3D', 'Delete Failed !')
        self.updateTac3DList()
        
    def startSensor(self):
        self.saveConfig()
        SN = self.comboLocalTac3DSN.get().split(' ')[0]

        config_path = os.path.join(self.configDir, SN)
        if self.processes.get(SN) != None:
            messagebox.showinfo('Tac3D', 'Sensor {} is running !'.format(SN))
            return
        
        if not self.downloadCore():
            messagebox.showerror('Error', 'Executable file `{}` is not found.'.format(self.corePath))
            return
        
        if not os.path.isfile(config_path+'/sensor.yaml'):
            messagebox.showerror('Error', '`{}` is not a valid configuration file.'.format(config_path))
            return
        
        if sys.platform.startswith('linux'):
            os.chmod(self.corePath, mode=0o755)
        self.processes[SN] = subprocess.Popen([self.corePath, '-c', config_path, '-i', self.config['SDK_ip'][0].get(), '-p', self.config['SDK_port'][0].get()],
                                              cwd=self.logDir)
        self.updateTac3DList()
        
    def stopSensor(self):
        SN = self.comboLocalTac3DSN.get().split(' ')[0]
        proc = self.processes.get(SN)
        if not proc is None:
            print('stop sensor:', SN)
            del self.processes[SN]
            proc.kill()
            messagebox.showinfo('Tac3D', 'Sensor '+SN+' stopped.')
        self.updateTac3DList()
        
    def runDisplayer(self):
        self.saveConfig()
        name = 'Displayer'
        if self.processes.get(name) == None:
            self.processes[name] = subprocess.Popen([self.pythonName, '-m', 'PyTac3D.GUI_Displayer', self.config['SDK_port'][0].get()])

    def saveConfig(self):
        with open(self.configPath, 'w') as f:
            for key, val in self.config.items():
                f.write(key+': '+val[0].get()+'\n')
        
    def loadConfig(self):
        for var, default in self.config.values():
            var.set(default)
        try:
            with open(self.configPath, 'r') as f:
                while True:
                    item = f.readline().split(': ')
                    if len(item) == 2:
                        self.config[item[0]][0].set(item[1][:-1])
                        break
        except:
            print('Fail to load local.cfg. Default values are used.')
            self.saveConfig()
        
    def update(self):
        delList = []
        for SN, proc in self.processes.items():
            poll = proc.poll()
            if not poll is None:
                delList.append(SN)
                if not SN.startswith('Displayer'):
                    messagebox.showinfo('Tac3D', 'Sensor '+SN+' stopped\n' + ErrorMessage.getErrMsg(poll, 'en'))
                    
        for SN in delList:
            del self.processes[SN]
            self.updateTac3DList()
        
class MainWindow:
    def __init__(self):
        print('Welcome to the pytac3d-gui tool.')
        print('For more usage instructions, please visit: https://gitee.com/sxhzzlw/tac3d-utils/tree/master/Tac3D_Manager')
        self.root = tk.Tk()
        # self.root.tk.call('tk', 'scaling', 2.0)
        self.root.title('PyTac3D GUI Tool v3.3.0.6')
        self.root.resizable(0,0)
        self.root.minsize(width=600, height=200)
        self.root.protocol('WM_DELETE_WINDOW', self.stop)
        self.root.columnconfigure(0, minsize=300)
        self.root.columnconfigure(1, minsize=300)
        
        # 处理模块操作
        self.processorSettingsFrame = tk.LabelFrame(self.root, text='Processor Settings')
        self.processorSettingsFrame.grid(row=0,column=1, padx=4, pady=4, sticky='w e s n')
        self.processorSettingsFrame.grid_columnconfigure(1, weight=1)
        self.processorFrame = ProcessorFrame(self.processorSettingsFrame)

        # 本机操作
        self.localSettingsFrame = tk.LabelFrame(self.root, text='Local Settings')
        self.localSettingsFrame.grid(row=0,column=0, padx=4, pady=4, sticky='w e s n')
        self.localSettingsFrame.grid_columnconfigure(1, weight=1)
        self.localFrame = LocalFrame(self.localSettingsFrame)
        self.running = True
        
    def run(self):
        # 手动处理事件循环
        while self.running:
            self.root.update()
            self.processorFrame.update()
            self.localFrame.update()
            time.sleep(0.03)

    def stop(self):
        self.running = False
        for SN, proc in self.localFrame.processes.items():
            proc.kill()

        try:
            self.root.destroy()
        except:
            pass

if __name__ == '__main__':
    window = MainWindow()
    window.run()
    window.stop()

