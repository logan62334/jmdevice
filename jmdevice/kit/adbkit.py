import logging
import os
import platform

from jmdevice import app_path
from jmdevice.kit import DeviceInfo
from jmdevice.tools.cmdkit import CmdKit


class ADBKit(object):
    os_name = None
    adb_path = None

    def __init__(self, sn: str = None, device_proxy_ip: str = None):
        self.device_proxy_ip = device_proxy_ip
        self._adb_path = ADBKit.get_adb_path()
        self._sn = sn
        if self._sn is None:
            devices = self.list_device()
            if len(devices) > 0:
                self._sn = devices[0]
        self._os_name = None
        self._properties = {}
        self.logger = logging

    def _log(self, info):
        self.logger.info("%s: %s" % (self._sn, info))

    @property
    def prop(self) -> "Property":
        return Property(self)

    @property
    def sn(self):
        return self._sn

    @staticmethod
    def get_adb_path():
        if ADBKit.adb_path:
            return ADBKit.adb_path
        ADBKit.adb_path = os.environ.get('ADB_PATH')
        if ADBKit.adb_path is not None and ADBKit.adb_path.endswith('adb'):
            return ADBKit.adb_path
        # 判断系统默认adb是否可用，如果系统有配，默认优先用系统的，避免5037端口冲突
        result = CmdKit.run_sysCmd('adb devices')
        if not isinstance(result, str):
            result = str(result, 'utf-8')
        # 说明自带adb  windows上返回结果不是这样 另外有可能第一次执行，adb会不正常
        if result and "command not found" not in result:
            ADBKit.adb_path = "adb"
            return ADBKit.adb_path
        static_path = app_path() + '/device/static/adb'
        ADBKit.os_name = platform.system()
        if ADBKit.os_name == "Windows":
            ADBKit.adb_path = os.path.join(static_path, "windows", "adb.exe")
        elif ADBKit.os_name == "Darwin":
            ADBKit.adb_path = os.path.join(static_path, "mac", "adb")
        else:
            ADBKit.adb_path = os.path.join(static_path, "linux", "adb")
        return ADBKit.adb_path

    @staticmethod
    def get_os_name():
        if ADBKit.os_name:
            return ADBKit.os_name
        ADBKit.os_name = platform.system()
        return ADBKit.os_name

    def list_device(self):
        result = self.run_adb_cmd('devices')
        if not isinstance(result, str):
            result = result.decode('utf-8')
        result = result.replace('\r', '').splitlines()
        device_list = []
        for device in result[1:]:
            if len(device) <= 1 or '\t' not in device:
                continue
            if device.split('\t')[1] == 'device':
                # 只获取连接正常的
                device_list.append(device.split('\t')[0])
        return device_list

    @property
    def info(self):
        try:
            device_info = DeviceInfo(sn=self._sn, os_type="Android", os_version=self.get_android_version(),
                                     sdk_version=self.get_sdk_version(),
                                     brand=self.get_product_brand(), model=self.get_product_model(),
                                     rom_version=self.get_product_rom(), cpu_abi=self.get_cpu_abi(),
                                     cpu_hardware=self.get_cpu_hardware(), display=self.get_wm_size())
            return device_info
        except Exception as e:
            self._log(e)

    def _run_cmd_once(self, cmd, *argv, **kwds):
        if self._sn:
            if self.device_proxy_ip:
                cmdlet = [self._adb_path, '-H', self.device_proxy_ip, '-P 5037', '-s', self._sn, cmd]
            else:
                cmdlet = [self._adb_path, '-s', self._sn, cmd]
        else:
            if self.device_proxy_ip:
                cmdlet = [self._adb_path, '-H', self.device_proxy_ip, '-P 5037', cmd]
            else:
                cmdlet = [self._adb_path, cmd]
        for i in range(len(argv)):
            arg = argv[i]
            if not isinstance(argv[i], str):
                arg = arg.decode('utf8')
            cmdlet.append(arg)
        cmd = " ".join(cmdlet)
        timeout = 60
        if "timeout" in kwds:
            timeout = kwds['timeout']
        out = CmdKit.run_sysCmd(cmd, timeout=timeout)
        return out

    def run_adb_cmd(self, cmd, *argv, **kwds):
        retry_count = 3  # 默认最多重试3次
        if "retry_count" in kwds:
            retry_count = kwds['retry_count']
        while retry_count > 0:
            ret = self._run_cmd_once(cmd, *argv, **kwds)
            if ret is not None:
                return ret
            retry_count = retry_count - 1

    def run_shell_cmd(self, cmd, **kwds):
        ret = self.run_adb_cmd('shell', '%s' % cmd, **kwds)
        if ret is None:
            self._log(u'adb cmd failed:%s ' % cmd)
        return ret

    def get_android_version(self):
        """获取系统版本，如：4.1.2
        """
        return self.prop.get("ro.build.version.release").strip()

    def get_sdk_version(self):
        """获取SDK版本，如：16
        """
        try:
            res = self.prop.get('ro.build.version.sdk').strip()
            if 'Error' in res or res == '':
                return 25
            else:
                return res
        except Exception as e:
            self._log(e)

    def get_product_brand(self):
        """获取手机品牌  如：Mi Samsung OnePlus
        """
        return self.prop.get('ro.product.brand').strip()

    def get_product_model(self):
        """获取手机型号  如：A0001 M2S
        """
        return self.prop.get('ro.product.model').strip()

    def get_product_rom(self):
        """
        获取设备ROM名，如：MHA-AL00C00B213
        """
        return self.prop.get("ro.build.display.id").strip()

    def get_screen_size(self):
        """获取屏幕大小  如：5.5 可能获取不到
        """
        return self.prop.get('ro.product.screensize').strip()

    def get_wm_size(self):
        """获取屏幕分辨率  如：Physical size:1080*1920
        """
        try:
            self.run_shell_cmd("wm size reset")
            res = self.run_shell_cmd("wm size | awk 'NR==1' | awk -F': ' '{print $2}'").strip()
            if 'x' in res:
                return res
            else:
                return "暂无"
        except Exception as e:
            self._log(e)
            return "暂无"

    def get_cpu_abi(self):
        """
        获取设备CPU架构，如：arm64-v8a,armeabi-v7a,armeabi
        """
        if int(self.get_sdk_version()) >= 21:
            return self.prop.get("ro.product.cpu.abilist").strip()
        else:
            return self.prop.get("ro.product.cpu.abi").strip()

    def get_cpu_hardware(self):
        """
        获取设备CPU Hardware，如：Hisilicon Kirin990
        """

        try:
            return self.prop.get("ro.hardware").strip()
        except Exception as e:
            self._log(e)
            return ""

    def get_size(self):
        """ get screen size, return value looks like (1080, 1920) """
        result_str = self.get_wm_size()
        width, height = result_str.replace('\n', '').replace('\r', '').split(' ')[-1].split('x')
        return width, height


class Property:
    def __init__(self, d: ADBKit):
        self._d = d

    def get(self, name: str, cache=True) -> str:
        try:
            if cache and name in self._d._properties:
                return self._d._properties[name]
            value = self._d._properties[name] = self._d.run_shell_cmd('getprop {0}'.format(name)).strip()
            return value
        except Exception as e:
            self._d._log(e)
            return ""
