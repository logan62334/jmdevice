#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    apptoolkit
    ~~~~~~~~~~~~

    This module is the main apptoolkit.

    :copyright: (c) 2017 by Ma Fei.
"""

import json
import os
import subprocess

__version__ = '0.0.4'


class Shell:
    def __init__(self):
        pass

    @staticmethod
    def invoke(cmd):
        output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        o = output.decode("utf-8")
        return o


# 判断是否设置环境变量ANDROID_HOME
if "ANDROID_HOME" in os.environ:
    command = os.path.join(
        os.environ["ANDROID_HOME"],
        "platform-tools",
        "adb")
else:
    raise EnvironmentError(
        "Adb not found in $ANDROID_HOME path: %s." %
        os.environ["ANDROID_HOME"])


class ADB(object):
    """
      参数:  device_id
    """

    def __init__(self, device_id=""):

        if device_id == "":
            self.device_id = ""
        else:
            self.device_id = "-s %s" % device_id

    def adb(self, args):
        cmd = "%s %s %s" % (command, self.device_id, str(args))
        return Shell.invoke(cmd)

    def shell(self, args):
        cmd = "%s %s shell %s" % (command, self.device_id, str(args),)
        return Shell.invoke(cmd)

    def get_device_state(self):
        """
        获取设备状态： offline | bootloader | device
        """
        return self.adb("get-state").stdout.read().strip()

    def get_device_id(self):
        """
        获取设备id号，return serialNo
        """
        return self.adb("get-serialno").stdout.read().strip()

    def get_android_version(self):
        """
        获取设备中的Android版本号，如4.2.2
        """
        return self.shell(
            "getprop ro.build.version.release").strip()

    def get_sdk_version(self):
        """
        获取设备SDK版本号，如：24
        """
        return self.shell("getprop ro.build.version.sdk").strip()

    def get_product_brand(self):
        """
        获取设备品牌，如：HUAWEI
        """
        return self.shell("getprop ro.product.brand").strip()

    def get_product_model(self):
        """
        获取设备型号，如：MHA-AL00
        """
        return self.shell("getprop ro.product.model").strip()

    def get_product_rom(self):
        """
        获取设备ROM名，如：MHA-AL00C00B213
        """
        return self.shell("getprop ro.build.display.id").strip()


class DeviceInfo:
    def __init__(self, uid, os_type, os_version, sdk_version, brand, model, rom_version):
        self.uid = uid
        self.os_type = os_type
        self.os_version = os_version
        self.sdk_version = sdk_version
        self.brand = brand
        self.model = model
        self.rom_version = rom_version


class Device:
    def __init__(self):
        pass

    @staticmethod
    def get_android_devices():
        android_devices_list = []
        android_devices_infos = []
        for device in Shell.invoke('adb devices').splitlines():
            if 'device' in device and 'devices' not in device:
                device = device.split('\t')[0]
                android_devices_list.append(device)
        for device_uid in android_devices_list:
            device_info = DeviceInfo(device_uid, "Android", ADB(device_uid).get_android_version(),
                                     ADB(device_uid).get_sdk_version(),
                                     ADB(device_uid).get_product_brand(), ADB(device_uid).get_product_model(),
                                     ADB(device_uid).get_product_rom())
            android_devices_infos.append(device_info.__dict__)
        return android_devices_infos

    @staticmethod
    def get_ios_devices():
        devices = []
        output = Shell.invoke('idevice_id -l')
        config_file = os.path.join(os.path.dirname(__file__), 'ios_mapping.json')
        with open(config_file, 'r') as f:
            config = json.loads(f.read())

        if len(output) > 0:
            udids = output.strip('\n').split('\t')
            for udid in udids:
                dic = {"os_type": 'iOS', "uid": udid}
                output = Shell.invoke('ideviceinfo -u %s -k ProductType' % udid)
                device_type = config[output.strip('\n')]
                brand = ''
                # -1表示找不到 0表示下标
                if device_type.find("iPhone") != -1:
                    brand = 'iPhone'
                elif device_type.find("iPad") != -1:
                    brand = 'iPad'
                elif device_type.find("iPod") != -1:
                    brand = 'iPod'

                dic['brand'] = brand
                dic['model'] = device_type

                output = Shell.invoke('ideviceinfo -u %s -k ProductVersion' % udid)
                dic['os_type'] = 'iOS'
                dic['os_version'] = output.strip('\n')
                dic['rom_version'] = output.strip('\n')

                output = Shell.invoke('idevicename -u %s' % udid)
                dic['device_name'] = output
                devices.append(dic)
        return devices
