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
import platform
import re
import subprocess
import tempfile
import xml.etree.cElementTree as ET
from time import sleep

import keycode

__version__ = '0.0.9'

PATH = lambda p: os.path.abspath(p)

# 判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
else:
    find_util = "grep"


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
    if system == "Windows":
        command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
    else:
        command = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
else:
    print("Adb not found in $ANDROID_HOME path")


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

    def get_pid(self, packageName):
        """
        获取进程pid
        args:
        - packageName -: 应用包名
        usage: getPid("com.android.settings")
        """
        if system is "Windows":
            pidinfo = self.shell("ps | findstr %s$" % packageName).stdout.read()
        else:
            pidinfo = self.shell("ps | grep -w %s" % packageName).stdout.read()

        if pidinfo == '':
            return "the process doesn't exist."

        pattern = re.compile(r"\d+")
        result = pidinfo.split(" ")
        result.remove(result[0])

        return pattern.findall(" ".join(result))[0]

    def kill_process(self, pid):
        """
        杀死应用进程
        args:
        - pid -: 进程pid值
        usage: killProcess(154)
        注：杀死系统应用进程需要root权限
        """
        if self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1] == "":
            return "kill success"
        else:
            return self.shell("kill %s" % str(pid)).stdout.read().split(": ")[-1]

    def quit_app(self, packageName):
        """
        退出app，类似于kill掉进程
        usage: quitApp("com.android.settings")
        """
        self.shell("am force-stop %s" % packageName)

    def get_focused_package_and_activity(self):
        """
        获取当前应用界面的包名和Activity，返回的字符串格式为：packageName/activityName
        """
        pattern = re.compile(r"[a-zA-Z0-9\.]+/.[a-zA-Z0-9\.]+")
        out = self.shell("dumpsys window w | %s \/ | %s name=" % (find_util, find_util)).stdout.read()

        return pattern.findall(out)[0]

    def get_current_package_name(self):
        """
        获取当前运行的应用的包名
        """
        return self.get_focused_package_and_activity().split("/")[0]

    def get_current_activity(self):
        """
        获取当前运行应用的activity
        """
        return self.get_focused_package_and_activity().split("/")[-1]

    def get_battery_level(self):
        """
        获取电池电量
        """
        level = self.shell("dumpsys battery | %s level" % find_util).stdout.read().split(": ")[-1]

        return int(level)

    def get_battery_status(self):
        """
        获取电池充电状态
        BATTERY_STATUS_UNKNOWN：未知状态
        BATTERY_STATUS_CHARGING: 充电状态
        BATTERY_STATUS_DISCHARGING: 放电状态
        BATTERY_STATUS_NOT_CHARGING：未充电
        BATTERY_STATUS_FULL: 充电已满
        """
        statusDict = {1: "BATTERY_STATUS_UNKNOWN",
                      2: "BATTERY_STATUS_CHARGING",
                      3: "BATTERY_STATUS_DISCHARGING",
                      4: "BATTERY_STATUS_NOT_CHARGING",
                      5: "BATTERY_STATUS_FULL"}
        status = self.shell("dumpsys battery | %s status" % find_util).stdout.read().split(": ")[-1]

        return statusDict[int(status)]

    def get_battery_temp(self):
        """
        获取电池温度
        """
        temp = self.shell("dumpsys battery | %s temperature" % find_util).stdout.read().split(": ")[-1]

        return int(temp) / 10.0

    def get_screen_resolution(self):
        """
        获取设备屏幕分辨率，return (width, high)
        """
        pattern = re.compile(r"\d+")
        out = self.shell("dumpsys display | %s PhysicalDisplayInfo" % find_util).stdout.read()
        display = ""
        if out:
            display = pattern.findall(out)
        elif int(self.get_sdk_version()) >= 18:
            display = self.shell("wm size").stdout.read().split(":")[-1].strip().split("x")
        else:
            raise Exception("get screen resolution failed!")
        return int(display[0]), int(display[1])

    def reboot(self):
        """
        重启设备
        """
        self.adb("reboot")

    def fastboot(self):
        """
        进入fastboot模式
        """
        self.adb("reboot bootloader")

    def get_system_applist(self):
        """
        获取设备中安装的系统应用包名列表
        """
        sysApp = []
        for packages in self.shell("pm list packages -s").stdout.readlines():
            sysApp.append(packages.split(":")[-1].splitlines()[0])

        return sysApp

    def get_third_applist(self):
        """
        获取设备中安装的第三方应用包名列表
        """
        thirdApp = []
        for packages in self.shell("pm list packages -3").stdout.readlines():
            thirdApp.append(packages.split(":")[-1].splitlines()[0])

        return thirdApp

    def get_matching_applist(self, keyword):
        """
        模糊查询与keyword匹配的应用包名列表
        usage: getMatchingAppList("qq")
        """
        matApp = []
        for packages in self.shell("pm list packages %s" % keyword).stdout.readlines():
            matApp.append(packages.split(":")[-1].splitlines()[0])

        return matApp

    def get_app_starttotaltime(self, component):
        """
        获取启动应用所花时间
        usage: getAppStartTotalTime("com.android.settings/.Settings")
        """
        time = self.shell("am start -W %s | %s TotalTime" % (component, find_util)) \
            .stdout.read().split(": ")[-1]
        return int(time)

    def install_app(self, appFile):
        """
        安装app，app名字不能含中文字符
        args:
        - appFile -: app路径
        usage: install("d:\\apps\\Weico.apk")
        """
        self.adb("install %s" % appFile)

    def is_install(self, packageName):
        """
        判断应用是否安装，已安装返回True，否则返回False
        usage: isInstall("com.example.apidemo")
        """
        if self.get_matching_applist(packageName):
            return True
        else:
            return False

    def remove_app(self, packageName):
        """
        卸载应用
        args:
        - packageName -:应用包名，非apk名
        """
        self.adb("uninstall %s" % packageName)

    def clear_appdata(self, packageName):
        """
        清除应用用户数据
        usage: clearAppData("com.android.contacts")
        """
        if "Success" in self.shell("pm clear %s" % packageName).stdout.read().splitlines():
            return "clear user data success "
        else:
            return "make sure package exist"

    def reset_currentapp(self):
        """
        重置当前应用
        """
        packageName = self.get_current_package_name()
        component = self.get_focused_package_and_activity()
        self.clear_appdata(packageName)
        self.start_activity(component)

    def start_activity(self, component):
        """
        启动一个Activity
        usage: startActivity(component = "com.android.settinrs/.Settings")
        """
        self.shell("am start -n %s" % component)

    def start_webpage(self, url):
        """
        使用系统默认浏览器打开一个网页
        usage: startWebpage("http://www.baidu.com")
        """
        self.shell("am start -a android.intent.action.VIEW -d %s" % url)

    def call_phone(self, number):
        """
        启动拨号器拨打电话
        usage: callPhone(10086)
        """
        self.shell("am start -a android.intent.action.CALL -d tel:%s" % str(number))

    def send_keyevent(self, keycode):
        """
        发送一个按键事件
        args:
        - keycode -:
        http://developer.android.com/reference/android/view/KeyEvent.html
        usage: sendKeyEvent(keycode.HOME)
        """
        self.shell("input keyevent %s" % str(keycode))
        sleep(0.5)

    def long_presskey(self, keycode):
        """
        发送一个按键长按事件，Android 4.4以上
        usage: longPressKey(keycode.HOME)
        """
        self.shell("input keyevent --longpress %s" % str(keycode))
        sleep(0.5)

    def touch(self, e=None, x=None, y=None):
        """
        触摸事件
        usage: touch(e), touch(x=0.5,y=0.5)
        """
        if e is not None:
            x = e[0]
            y = e[1]
        if 0 < x < 1:
            x = x * self.width
        if 0 < y < 1:
            y = y * self.high

        self.shell("input tap %s %s" % (str(x), str(y)))
        sleep(0.5)

    def touch_by_element(self, element):
        """
        点击元素
        usage: touchByElement(Element().findElementByName(u"计算器"))
        """
        self.shell("input tap %s %s" % (str(element[0]), str(element[1])))
        sleep(0.5)

    def touch_by_ratio(self, ratioWidth, ratioHigh):
        """
        通过比例发送触摸事件
        args:
        - ratioWidth -:width占比, 0<ratioWidth<1
        - ratioHigh -: high占比, 0<ratioHigh<1
        usage: touchByRatio(0.5, 0.5) 点击屏幕中心位置
        """
        self.shell("input tap %s %s" % (
            str(ratioWidth * self.get_screen_resolution()[0]), str(ratioHigh * self.get_screen_resolution()[1])))
        sleep(0.5)

    def swipe_by_coord(self, start_x, start_y, end_x, end_y, duration=" "):
        """
        滑动事件，Android 4.4以上可选duration(ms)
        usage: swipe(800, 500, 200, 500)
        """
        self.shell("input swipe %s %s %s %s %s" % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))
        sleep(0.5)

    def swipe(self, e1=None, e2=None, start_x=None, start_y=None, end_x=None, end_y=None, duration=" "):
        """
        滑动事件，Android 4.4以上可选duration(ms)
        usage: swipe(e1, e2)
               swipe(e1, end_x=200, end_y=500)
               swipe(start_x=0.5, start_y=0.5, e2)
        """
        if e1 is not None:
            start_x = e1[0]
            start_y = e1[1]
        if e2 is not None:
            end_x = e2[0]
            end_y = e2[1]
        if 0 < start_x < 1:
            start_x = start_x * self.width
        if 0 < start_y < 1:
            start_y = start_y * self.high
        if 0 < end_x < 1:
            end_x = end_x * self.width
        if 0 < end_y < 1:
            end_y = end_y * self.high

        self.shell("input swipe %s %s %s %s %s" % (str(start_x), str(start_y), str(end_x), str(end_y), str(duration)))
        sleep(0.5)

    def swipe_by_ratio(self, start_ratioWidth, start_ratioHigh, end_ratioWidth, end_ratioHigh, duration=" "):
        """
        通过比例发送滑动事件，Android 4.4以上可选duration(ms)
        usage: swipeByRatio(0.9, 0.5, 0.1, 0.5) 左滑
        """
        self.shell("input swipe %s %s %s %s %s" % (
            str(start_ratioWidth * self.get_screen_resolution()[0]),
            str(start_ratioHigh * self.get_screen_resolution()[1]),
            str(end_ratioWidth * self.get_screen_resolution()[0]), str(end_ratioHigh * self.get_screen_resolution()[1]),
            str(duration)))
        sleep(0.5)

    def swipe_to_left(self):
        """
        左滑屏幕
        """
        self.swipe_by_ratio(0.8, 0.5, 0.2, 0.5)

    def swipe_to_right(self):
        """
        右滑屏幕
        """
        self.swipe_by_ratio(0.2, 0.5, 0.8, 0.5)

    def swipe_to_up(self):
        """
        上滑屏幕
        """
        self.swipe_by_ratio(0.5, 0.8, 0.5, 0.2)

    def swipe_to_down(self):
        """
        下滑屏幕
        """
        self.swipe_by_ratio(0.5, 0.2, 0.5, 0.8)

    def long_press(self, e=None, x=None, y=None):
        """
        长按屏幕的某个坐标位置, Android 4.4
        usage: longPress(e)
               longPress(x=0.5, y=0.5)
        """
        self.swipe(e1=e, e2=e, start_x=x, start_y=y, end_x=x, end_y=y, duration=2000)

    def long_press_element(self, e):
        """
       长按元素, Android 4.4
        """
        self.shell("input swipe %s %s %s %s %s" % (str(e[0]), str(e[1]), str(e[0]), str(e[1]), str(2000)))
        sleep(0.5)

    def long_press_by_ratio(self, ratioWidth, ratioHigh):
        """
        通过比例长按屏幕某个位置, Android.4.4
        usage: longPressByRatio(0.5, 0.5) 长按屏幕中心位置
        """
        self.swipe_by_ratio(ratioWidth, ratioHigh, ratioWidth, ratioHigh, duration=2000)

    def send_text(self, string):
        """
        发送一段文本，只能包含英文字符和空格，多个空格视为一个空格
        usage: sendText("i am unique")
        """
        text = str(string).split(" ")
        out = []
        for i in text:
            if i != "":
                out.append(i)
        length = len(out)
        for i in xrange(length):
            self.shell("input text %s" % out[i])
            if i != length - 1:
                self.send_keyevent(keycode.SPACE)
        sleep(0.5)


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
            udids = output.split('\n')
            udids.pop()
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
                dic['device_name'] = output.strip('\n')
                devices.append(dic)
        return devices


class Element(object):
    """
    通过元素定位
    """

    def __init__(self, device_id=""):
        """
        初始化，获取系统临时文件存储目录，定义匹配数字模式
        """
        self.utils = ADB(device_id)

        self.tempFile = tempfile.gettempdir()
        self.pattern = re.compile(r"\d+")

    def __uidump(self):
        """
        获取当前Activity的控件树
        """
        if int(self.utils.get_sdk_version()) >= 19:
            self.utils.shell("uiautomator dump --compressed /data/local/tmp/uidump.xml").wait()
        else:
            self.utils.shell("uiautomator dump /data/local/tmp/uidump.xml").wait()
        self.utils.adb("pull data/local/tmp/uidump.xml %s" % self.tempFile).wait()
        self.utils.shell("rm /data/local/tmp/uidump.xml").wait()

    def __element(self, attrib, name):
        """
        同属性单个元素，返回单个坐标元组，(x, y)
        :args:
        - attrib - node节点中某个属性
        - name - node节点中某个属性对应的值
        """
        Xpoint = None
        Ypoint = None

        self.__uidump()
        tree = ET.ElementTree(file=PATH("%s/uidump.xml" % self.tempFile))
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                # 获取元素所占区域坐标[x, y][x, y]
                bounds = elem.attrib["bounds"]

                # 通过正则获取坐标列表
                coord = self.pattern.findall(bounds)

                # 求取元素区域中心点坐标
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                break

        if Xpoint is None or Ypoint is None:
            raise Exception("Not found this element(%s) in current activity" % name)

        return Xpoint, Ypoint

    def __elements(self, attrib, name):
        """
        同属性多个元素，返回坐标元组列表，[(x1, y1), (x2, y2)]
        """
        pointList = []
        self.__uidump()
        tree = ET.ElementTree(file=PATH("%s/uidump.xml" % self.tempFile))
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])

                # 将匹配的元素区域的中心点添加进pointList中
                pointList.append((Xpoint, Ypoint))

        return pointList

    def __bound(self, attrib, name):
        """
        同属性单个元素，返回单个坐标区域元组,(x1, y1, x2, y2)
        """
        coord = []

        self.__uidump()
        tree = ET.ElementTree(file=PATH("%s/uidump.xml" % self.tempFile))
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)

        if not coord:
            raise Exception("Not found this element(%s) in current activity" % name)

        return int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3])

    def __bounds(self, attrib, name):
        """
        同属性多个元素，返回坐标区域列表，[(x1, y1, x2, y2), (x3, y3, x4, y4)]
        """

        pointList = []
        self.__uidump()
        tree = ET.ElementTree(file=PATH("%s/uidump.xml" % self.tempFile))
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                bounds = elem.attrib["bounds"]
                coord = self.pattern.findall(bounds)
                pointList.append((int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3])))

        return pointList

    def __checked(self, attrib, name):
        """
        返回布尔值列表
        """
        boolList = []
        self.__uidump()
        tree = ET.ElementTree(file=PATH("%s/uidump.xml" % self.tempFile))
        treeIter = tree.iter(tag="node")
        for elem in treeIter:
            if elem.attrib[attrib] == name:
                checked = elem.attrib["checked"]
                if checked == "true":
                    boolList.append(True)
                else:
                    boolList.append(False)

        return boolList

    def find_element_by_name(self, name):
        """
        通过元素名称定位单个元素
        usage: findElementByName(u"设置")
        """
        return self.__element("text", name)

    def find_elements_by_name(self, name):
        """
        通过元素名称定位多个相同text的元素
        """
        return self.__elements("text", name)

    def find_element_by_class(self, className):
        """
        通过元素类名定位单个元素
        usage: findElementByClass("android.widget.TextView")
        """
        return self.__element("class", className)

    def find_elements_by_class(self, className):
        """
        通过元素类名定位多个相同class的元素
        """
        return self.__elements("class", className)

    def find_element_by_id(self, resource_id):
        """
        通过元素的resource-id定位单个元素
        usage: findElementsById("com.android.deskclock:id/imageview")
        """
        return self.__element("resource-id", resource_id)

    def find_elements_by_id(self, resource_id):
        """
        通过元素的resource-id定位多个相同id的元素
        """
        return self.__elements("resource-id", resource_id)

    def find_element_by_content_desc(self, contentDesc):
        """
        通过元素的content-desc定位单个元素
        """
        return self.__element("content-desc", contentDesc)

    def find_elements_by_content_desc(self, contentDesc):
        """
        通过元素的content-desc定位多个相同的元素
        """
        return self.__elements("content-desc", contentDesc)

    def get_element_bound_by_name(self, name):
        """
        通过元素名称获取单个元素的区域
        """
        return self.__bound("text", name)

    def get_element_bounds_by_name(self, name):
        """
        通过元素名称获取多个相同text元素的区域
        """
        return self.__bounds("text", name)

    def get_element_bound_by_class(self, className):
        """
        通过元素类名获取单个元素的区域
        """
        return self.__bound("class", className)

    def get_element_bounds_by_class(self, className):
        """
        通过元素类名获取多个相同class元素的区域
        """
        return self.__bounds("class", className)

    def get_element_bound_by_content_desc(self, contentDesc):
        """
        通过元素content-desc获取单个元素的区域
        """
        return self.__bound("content-desc", contentDesc)

    def get_element_bounds_by_content_desc(self, contentDesc):
        """
        通过元素content-desc获取多个相同元素的区域
        """
        return self.__bounds("content-desc", contentDesc)

    def get_element_bound_by_id(self, resource_id):
        """
        通过元素id获取单个元素的区域
        """
        return self.__bound("resource-id", resource_id)

    def get_element_bounds_by_id(self, resource_id):
        """
        通过元素id获取多个相同resource-id元素的区域
        """
        return self.__bounds("resource-id", resource_id)

    def is_elements_checked_by_name(self, name):
        """
        通过元素名称判断checked的布尔值，返回布尔值列表
        """
        return self.__checked("text", name)

    def is_elements_checked_by_id(self, resource_id):
        """
        通过元素id判断checked的布尔值，返回布尔值列表
        """
        return self.__checked("resource-id", resource_id)

    def is_elements_checked_by_class(self, className):
        """
        通过元素类名判断checked的布尔值，返回布尔值列表
        """
        return self.__checked("class", className)
