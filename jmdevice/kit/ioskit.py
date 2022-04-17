import json
import logging
import os
import platform
from queue import Queue

from jmdevice.kit import DeviceInfo
from jmdevice.tools.cmdkit import CmdKit

logger = logging


class IDBKit(object):
    _ports = Queue(100)

    def __init__(self, sn=None):
        if platform.system() != 'Darwin':
            return
        self._sn = sn
        if self._sn is None:
            devices = self.list_device()
            if len(devices) > 0:
                self._sn = devices[0]

    def _log(self, info):
        logger.info("%s: %s" % (self._sn, info))

    @property
    def sn(self):
        return self._sn

    @property
    def info(self):
        try:
            product_type = CmdKit.run_sysCmd(
                "tidevice --udid %s info | grep ProductType | awk -F: '{print $2}'" % self._sn).strip()
            os_version = CmdKit.run_sysCmd(
                "tidevice --udid %s info | grep ProductVersion | awk -F: '{print $2}'" % self._sn).strip()
            cpu_abi = CmdKit.run_sysCmd(
                "tidevice --udid %s info | grep CPUArchitecture | awk -F: '{print $2}'" % self._sn).strip()

            if product_type.find("iPhone") != -1:
                brand = 'iPhone'
            elif product_type.find("iPad") != -1:
                brand = 'iPad'
            elif product_type.find("iPod") != -1:
                brand = 'iPod'
            else:
                brand = ''

            config_file = os.path.join(os.path.dirname(__file__), 'ios_mapping.json')
            with open(config_file, 'r') as f:
                config = json.loads(f.read())

            market_name = config[product_type]

        except Exception as e:
            self._log(e)
            return None

        device_info = DeviceInfo(sn=self._sn, os_type="iOS", os_version=os_version,
                                 sdk_version=os_version,
                                 brand=brand, model=market_name, market_name=market_name,
                                 rom_version=os_version, cpu_abi=cpu_abi)
        return device_info

    @staticmethod
    def list_device():
        if platform.system() != 'Darwin':
            return []
        _output = CmdKit.run_sysCmd('idevice_id -l')
        if "not found" not in _output:
            return [serial for serial in _output.split('\n') if serial]
        else:
            return []
