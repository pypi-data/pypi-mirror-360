#! /usr/bin/python3
import ipaddress
import os
import socket
import struct
import threading
import time


class UDP_MC_Manager:
    def __init__(self, callback=None, isSender=False, ip="", group="224.0.0.1", port=8083, frequency=1000):
        self.callback = callback

        self.isSender = isSender
        self.interval = 1.0 / frequency

        self.af_inet = None
        if group is not None and group != "" and ipaddress.ip_address(group) in ipaddress.ip_network("224.0.0.0/4"):
            self.group = group
        elif self.isSender:
            print("[UDP Manager] Invalid multicast group address, should be in 224.0.0.0/4")
            return
        else:
            self.group = ""

        self.ip = ip
        self.port = port
        self.addr = (self.group, self.port)
        self.running = False

    def start(self):
        self.af_inet = socket.AF_INET  # ipv4
        self.sockUDP = socket.socket(self.af_inet, socket.SOCK_DGRAM)

        if self.isSender:
            self.roleName = "Sender"
            self.sockUDP.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            self.sockUDP.bind((self.ip, 0))
        else:
            self.roleName = "Receiver"
            self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)
            self.sockUDP.bind(("", self.port))
            mreq = struct.pack("4s4s", socket.inet_aton(self.group), socket.inet_aton(self.get_interface_ip(self.ip)))
            self.sockUDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # print("[UDP Manager]", self.roleName, "at:", self.group, ":", self.port)

        self.running = True
        if not self.isSender and self.callback is not None:
            self.thread = threading.Thread(target=self.receive, args=())
            self.thread.daemon = True
            self.thread.start()  # 打开收数据的线程

    def receive(self):
        while self.running:
            time.sleep(self.interval)
            while self.running:
                try:
                    recvData, recvAddr = self.sockUDP.recvfrom(65535)  # 等待接受数据
                except:
                    break
                if not recvData:
                    break
                self.callback(recvData, recvAddr)

    def send(self, data):
        if self.isSender:
            self.sockUDP.sendto(data, self.addr)

    def close(self):
        self.running = False
        self.sockUDP.close()

    def get_interface_ip(self, ip):
        s = socket.socket(self.af_inet, socket.SOCK_DGRAM)
        s.connect((ip, 0))
        addr = s.getsockname()
        s.close()
        return addr[0]


class TCP_Client_Manager:
    def __init__(self, callback=None, ip="", port=8083, frequency=1000):
        self.callback = callback
        self.interval = 1.0 / frequency

        self.af_inet = None
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)
        self.running = False

    def start(self):
        self.af_inet = socket.AF_INET  # ipv4
        self.sockTCP = socket.socket(self.af_inet, socket.SOCK_STREAM)
        self.sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)

        self.roleName = "Client"
        self.sockTCP.connect(self.addr)

        print("[TCP Manager]", self.roleName, "at:", self.ip, ":", self.port)

        self.running = True
        if self.callback is not None:
            self.thread = threading.Thread(target=self.receive, args=())
            self.thread.daemon = True
            self.thread.start()  # 打开收数据的线程

    def receive(self):
        while self.running:
            time.sleep(self.interval)
            while self.running:
                try:
                    recvData, recvAddr = self.sockTCP.recvfrom(65535)  # 等待接受数据
                except:
                    break
                if not recvData:
                    break
                self.callback(recvData, recvAddr)

    def send(self, data):
        self.sockTCP.sendto(data, self.addr)

    def close(self):
        self.sockTCP.shutdown(socket.SHUT_RDWR)
        self.sockTCP.close()
        self.running = False


_CRC16_TABLE = None


def _generate_crc16_table():
    table = []
    for byte in range(256):
        crc = byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
        table.append(crc)
    return table


def crc16(data: bytes) -> int:
    global _CRC16_TABLE
    if _CRC16_TABLE is None:
        _CRC16_TABLE = _generate_crc16_table()
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ _CRC16_TABLE[(crc ^ byte) & 0xFF]
    return crc & 0xFFFF


class Manager:
    CMD_NONE = 0
    CMD_GET_ID = 1
    CMD_GET_RUN_IP = 2
    CMD_GET_CONF_IP = 3
    CMD_SET_CONF_IP = 4
    CMD_GET_TIME = 5
    CMD_SET_TIME = 6
    CMD_IF_RESTART = 11
    CMD_SYS_SHUTDOWN = 12
    CMD_SYS_RESTART = 13
    CMD_GET_CONF = 21
    CMD_ADD_CONF = 22
    CMD_DEL_CONF = 23
    CMD_RUN_TAC3D = 24
    CMD_STAT_TAC3D = 25
    CMD_STOP_TAC3D = 26
    CMD_GET_LOG = 27
    CMD_CLEAR_LOG = 28
    CMD_PING = 255

    TIMEOUT = 1.0

    def __init__(self, ip):
        """
        ip: ip of interface
        """
        self.r_ctx = UDP_MC_Manager(self._recv_cb, False, ip, "239.0.2.102", 60033)
        self.r_ctx.start()
        self.t_ctx = UDP_MC_Manager(None, True, ip, "239.0.2.101", 60032)
        self.t_ctx.start()
        self.connected = False
        self.pack_list = []
        self.sn_list = []

    def connect_server(self, ip):
        """
        ip: get from get_run_ip
        """
        self.c_ctx = TCP_Client_Manager(self._recv_cb, ip, 60030)
        self.c_ctx.start()
        self.connected = True

    def disconnect_server(self):
        if self.connected:
            self.c_ctx.close()
            self.c_ctx = None
        self.connected = False

    def _recv_cb(self, recv_data: bytes, recv_addr):
        if len(recv_data) < 8:
            return
        # split
        head = recv_data[0:8]
        data = recv_data[8:]
        # unpack header
        cmd, sub_cnt, size, _crc16 = struct.unpack("<HHHH", head)
        # check size
        if size + 8 != len(recv_data):
            print("size is not equal: %d vs %d" % (size + 8, len(recv_data)))
            print(data)
            return
        # check crc16
        __crc16 = crc16(data)
        if _crc16 != __crc16:
            print("crc16 is not equal: %d vs %d" % (__crc16, _crc16))
            return
        # fill output
        self.pack_list.append((cmd, sub_cnt, data))

    def get_tp_id(self):
        # make pack
        data = struct.pack("<")
        # send
        self.send_pack(self.t_ctx, self.CMD_GET_ID, 0, data)
        # receive
        num = 0
        tp_list = []
        while True:
            pack = self.wait_pack(self.CMD_GET_ID, 0, self.TIMEOUT)
            if pack is None:
                return (num, tp_list)
            # unpack
            pcmd, pcnt, pdata = pack
            tp = pdata[0:64].split(b"\x00", 1)[0].decode()
            print(tp)
            tp_list.append(tp)
            num += 1

    def get_config(self):
        # make pack
        data = struct.pack("<")
        # send
        self.send_pack(self.c_ctx, self.CMD_GET_CONF, 0, data)
        # receive
        sub_cnt = 0
        num = 0
        cfg_num = 0
        cfg_list = []
        sn_list = []
        while True:
            pack = self.wait_pack(self.CMD_GET_CONF, sub_cnt, self.TIMEOUT)
            if pack is None:
                return (-1, [], [])
            # unpack
            pcmd, pcnt, pdata = pack
            if sub_cnt == 0:
                head = pdata[0:4]
                (cfg_num,) = struct.unpack("<i", head)
                # print("number %d" % cfg_num)
                pdata = pdata[4:]
            s_num = int(len(pdata) / 128)
            for i in range(0, s_num):
                cfg = pdata[0:64].split(b"\x00", 1)[0].decode()
                # print(cfg)
                cfg_list.append(cfg)
                pdata = pdata[64:]
                sn = pdata[0:64].split(b"\x00", 1)[0].decode()
                # print(sn)
                sn_list.append(sn)
                pdata = pdata[64:]
                num += 1
            sub_cnt += 1
            # check num to stop
            if num >= cfg_num:
                return (cfg_num, cfg_list, sn_list)

    def add_config(self, fn: str):
        # open config
        file = open(fn, "rb")
        file_size = os.path.getsize(fn)
        fdata = file.read(1388)
        sub_cnt = 0
        print("file size %d" % file_size)
        while fdata:
            # make pack
            if sub_cnt == 0:
                data = struct.pack("<i", file_size) + fdata
            else:
                data = fdata
            # send
            self.send_pack(self.c_ctx, self.CMD_ADD_CONF, sub_cnt, data)
            # next pack
            sub_cnt += 1
            fdata = file.read(1392)
        # receive
        self.wait_reply(self.CMD_ADD_CONF, sub_cnt - 1, self.TIMEOUT)
        file.close()

    def delete_config(self, cfg: str):
        # make pack
        data = struct.pack("<64s", cfg.encode())
        # send
        self.send_pack(self.c_ctx, self.CMD_DEL_CONF, 0, data)
        # receive
        self.wait_reply(self.CMD_DEL_CONF, 0, self.TIMEOUT)

    def get_run_ip(self, tp_id: str):
        # make pack
        data = struct.pack("<64s", tp_id.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_GET_RUN_IP, 0, data)
        # receive
        pack = self.wait_pack(self.CMD_GET_RUN_IP, 0, self.TIMEOUT)
        if pack is None:
            return ("", "", "")
        # unpack
        pcmd, pcnt, pdata = pack
        ip = pdata[0:16].split(b"\x00", 1)[0].decode()
        netmask = pdata[16:32].split(b"\x00", 1)[0].decode()
        gateway = pdata[32:48].split(b"\x00", 1)[0].decode()
        print("IP: %s, netmask: %s, gateway: %s" % (ip, netmask, gateway))
        return (ip, netmask, gateway)

    def get_config_ip(self, tp_id: str):
        # make pack
        data = struct.pack("<64s", tp_id.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_GET_CONF_IP, 0, data)
        # receive
        pack = self.wait_pack(self.CMD_GET_CONF_IP, 0, self.TIMEOUT)
        if pack is None:
            return ("", "", "")
        # unpack
        pcmd, pcnt, pdata = pack
        ip = pdata[0:16].split(b"\x00", 1)[0].decode()
        netmask = pdata[16:32].split(b"\x00", 1)[0].decode()
        gateway = pdata[32:48].split(b"\x00", 1)[0].decode()
        print("IP: %s, netmask: %s, gateway: %s" % (ip, netmask, gateway))
        return (ip, netmask, gateway)

    def set_config_ip(self, tp_id: str, ip: str, netmask: str, gateway: str):
        # make pack
        data = struct.pack("<64s16s16s16s", tp_id.encode(), ip.encode(), netmask.encode(), gateway.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_SET_CONF_IP, 0, data)
        # receive
        self.wait_reply(self.CMD_SET_CONF_IP, 0, self.TIMEOUT)

    def interface_restart(self, tp_id: str):
        # make pack
        data = struct.pack("<64s", tp_id.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_IF_RESTART, 0, data)
        # this command will not send back data, we need ping to check connection
        time.sleep(1.0)
        # receive
        cnt = 0
        while True:
            # ping
            self.send_pack(self.t_ctx, self.CMD_PING, 0, data)
            if self.wait_reply(self.CMD_PING, 0, self.TIMEOUT) == True:
                return
            else:
                cnt = cnt + 1
            if cnt > 20:
                print("Can not reconnect interface")
                return

    def system_shutdown(self, tp_id: str):
        """
        user should stop the program after this command as the server is shutdown
        """
        # make pack
        data = struct.pack("<64s", tp_id.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_SYS_SHUTDOWN, 0, data)
        # this command will not send back data, just return
        time.sleep(1.0)

    def system_restart(self, tp_id: str):
        """
        user should re-init the client after this command as the connection will be down for a while
        """
        # make pack
        data = struct.pack("<64s", tp_id.encode())
        # send
        self.send_pack(self.t_ctx, self.CMD_SYS_RESTART, 0, data)
        # this command will not send back data, just return
        time.sleep(1.0)

    def get_time(self):
        # make pack
        data = struct.pack("<")
        # send
        self.send_pack(self.c_ctx, self.CMD_GET_TIME, 0, data)
        # receive
        pack = self.wait_pack(self.CMD_GET_TIME, 0, self.TIMEOUT)
        if pack is None:
            return 0.0
        # unpack
        pcmd, pcnt, pdata = pack
        (local_time,) = struct.unpack("<d", pdata[0:8])
        print("time: %f" % local_time)
        return local_time

    def set_time(self, local_time: float):
        # make pack
        data = struct.pack("<d", local_time)
        # send
        self.send_pack(self.c_ctx, self.CMD_SET_TIME, 0, data)
        # receive
        self.wait_reply(self.CMD_SET_TIME, 0, self.TIMEOUT)

    def run_tac3d(self, cfg: str, ip: str, port: int):
        # make pack
        data = struct.pack("<H64s64s", port, cfg.encode(), ip.encode())
        # send
        self.send_pack(self.c_ctx, self.CMD_RUN_TAC3D, 0, data)
        # receive
        pack = self.wait_pack(self.CMD_RUN_TAC3D, 0, self.TIMEOUT * 10)
        if pack is None:
            return -1
        # unpack
        pcmd, pcnt, pdata = pack
        (video_id,) = struct.unpack("<i", pdata[0:4])
        print("video_id %d" % video_id)
        return video_id

    def stat_tac3d(self, cfg: str):
        # make pack
        data = struct.pack("<64s", cfg.encode())
        # send
        self.send_pack(self.c_ctx, self.CMD_STAT_TAC3D, 0, data)
        # receive
        pack = self.wait_pack(self.CMD_STAT_TAC3D, 0, self.TIMEOUT)
        if pack is None:
            return -1
        # unpack
        pcmd, pcnt, pdata = pack
        (stat,) = struct.unpack("<i", pdata[0:4])
        print("state %d" % stat)
        return bool(stat)

    def stop_tac3d(self, cfg: str):
        # make pack
        data = struct.pack("<64s", cfg.encode())
        # send
        self.send_pack(self.c_ctx, self.CMD_STOP_TAC3D, 0, data)
        # receive
        self.wait_reply(self.CMD_STOP_TAC3D, 0, self.TIMEOUT * 2)

    def get_log(self, SN: str, fn: str):
        # make pack
        data = struct.pack("<64s", SN.encode())
        # send
        self.send_pack(self.c_ctx, self.CMD_GET_LOG, 0, data)
        # open log
        file = open(fn, "wb")
        file_size = 0
        # receive
        sub_cnt = 0
        file_pos = 0
        while True:
            pack = self.wait_pack(self.CMD_GET_LOG, sub_cnt, self.TIMEOUT)
            if pack is None:
                break
            # unpack
            pcmd, pcnt, pdata = pack
            if sub_cnt == 0:
                head = pdata[0:4]
                (file_size,) = struct.unpack("<i", head)
                print("Log export to %s" % fn)
                # print("file size %d" % file_size)
                pdata = pdata[4:]
            file.write(pdata)
            file_pos += len(pdata)
            sub_cnt += 1
            # check num to stop
            if file_pos >= file_size:
                break
        file.close()

    def clear_log(self):
        # make pack
        data = struct.pack("<")
        # send
        self.send_pack(self.c_ctx, self.CMD_CLEAR_LOG, 0, data)
        # receive
        self.wait_reply(self.CMD_CLEAR_LOG, 0, self.TIMEOUT)

    def send_pack(self, ctx, cmd: int, sub_cnt: int, data: bytes):
        head = struct.pack("<HHHH", cmd, sub_cnt, len(data), crc16(data))
        ctx.send(head + data)

    def wait_reply(self, cmd: int, sub_cnt: int, timeout: float):
        tstart = time.time()
        while True:
            # search all packs
            for pack in self.pack_list:
                # check cmd and sub_count
                pcmd, pcnt, pdata = pack
                if cmd == pcmd and sub_cnt == pcnt:
                    # remove unpacked data and stop
                    self.pack_list.remove(pack)
                    return True
            # wait
            time.sleep(0.01)
            if tstart + timeout <= time.time():
                print("timeout")
                return False

    def wait_pack(self, cmd: int, sub_cnt: int, timeout: float):
        tstart = time.time()
        while True:
            # search all packs
            for pack in self.pack_list:
                # check cmd and sub_count
                pcmd, pcnt, pdata = pack
                if cmd == pcmd and sub_cnt == pcnt:
                    # remove unpacked data and stop
                    self.pack_list.remove(pack)
                    return pack
            # wait
            time.sleep(0.01)
            if tstart + timeout <= time.time():
                print("timeout")
                return None


if __name__ == "__main__":
    tac3d_manager = Manager("192.168.2.1")
    tp_num, tp_list = tac3d_manager.get_tp_id()
    tp_id = tp_list[0]
    # IP config
    ip, netmask, gateway = tac3d_manager.get_run_ip(tp_id)
    tac3d_manager.connect_server(ip)
    # Tac3D config
    tac3d_manager.add_config("test_conf.tcfg")
    cfg_num, cfg_list, sn_list = tac3d_manager.get_config()
    # tac3d
    tac3d_manager.run_tac3d(cfg_list[0], "192.168.2.1", 9988)
    tac3d_manager.stat_tac3d(cfg_list[0])
    time.sleep(30)
    tac3d_manager.stop_tac3d(cfg_list[0])
    tac3d_manager.get_log(sn_list[0], "log.zip")
    tac3d_manager.disconnect_server()
