class DeviceInfo:

    def __init__(self, sn: str = "", model: str = "", brand: str = "", os_type: str = "", task_type: str = "",
                 market_name: str = "", cpu_abi: str = "", os_version: str = "", sdk_version: str = "",
                 rom_version: str = "", cpu_hardware: str = "", device_hub_ip: str = "", display: str = ""):
        self.sn = sn
        self.model = model
        self.brand = brand
        self.os_type = os_type
        self.task_type = task_type
        self.market_name = market_name
        self.cpu_abi = cpu_abi
        self.os_version = os_version
        self.sdk_version = sdk_version
        self.rom_version = rom_version
        self.cpu_hardware = cpu_hardware
        self.device_hub_ip = device_hub_ip
        self.display = display
