import asyncio
import os
from pathlib import Path
import re
import subprocess
from typing import cast
import reactivex as rx
from nicegui import app, ui,background_tasks
from async_adbc import ADBClient, Status
from importlib import resources

class _AndroidProfilerService:
    on_devices_changed: rx.Subject[set[str]] = rx.Subject()
    on_device_connected: rx.Subject[str] = rx.Subject()
    on_device_disconnected: rx.Subject[str] = rx.Subject()

    def __init__(self) -> None:
        self.adbc = ADBClient()
        self._timer_scan_device = None
        self._devices: set[str] = set()

    @property
    def devices(self):
        return self._devices

    async def get_device(self, serialno: str):
        dev = await self.adbc.device(serialno)
        return dev

    async def get_device_apps(self, serialno: str):
        dev = await self.get_device(serialno)
        return await dev.pm.list_packages()

    async def get_device_processes(self, serialno: str, app_name: str):
        dev = await self.get_device(serialno)
        res = await dev.shell(f"ps -A|grep {app_name}|grep -v grep|awk '{{print $9}}'")
        return res.strip().splitlines()

    async def get_app_info(self, serialno: str, app_name: str):
        dev = await self.get_device(serialno)
        res = await dev.shell(f"dumpsys package {app_name}")
        # 获取app版本号
        version_match = re.search(r"versionName=(\S+)", res)
        # 获取app最后一次更新时间
        install_time_match = re.search(r"lastUpdateTime=(\S+)", res)

        version = version_match.group(1) if version_match else "Unknown"
        install_time = install_time_match.group(1) if install_time_match else "Unknown"

        return {"version": version, "install_time": install_time}
    
    async def start_adb_server(self):
        ret = await self._run_adb_cmd("start-server")
        self.start_scan_devices()
        return ret

    async def stop_adb_server(self):
        self.stop_scan_devices()
        return await self._run_adb_cmd("kill-server")
    
    async def _run_adb_cmd(self,cmd:str):
        files = cast(Path,resources.files("perfcat.adb"))
        adb_path = files.joinpath("adb.exe").as_posix() # noqa
        _run_cmd = asyncio.create_subprocess_exec(
            adb_path, cmd,
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
            )
        ret = await _run_cmd
        stdout,stderr = await ret.communicate()
        print(stdout.decode(),stderr.decode(),ret.returncode)
        return ret.returncode


    async def get_device_info(self, serialno: str):
        dev = await self.get_device(serialno)
        prop = await dev.properties
        info = {}
        info["品牌"] = prop.get("ro.product.brand", "Unknow")  # 品牌
        info["制造商"] = prop.get("ro.product.manufacturer", "Unknow")  # 制造商
        info["型号"] = prop.get("ro.product.model", "Unknow")  # 型号
        info["名称"] = prop.get("ro.product.name", "Unknow")  # 名称
        info["系统版本"] = prop.get("ro.build.version.release", "Unknow")  # 系统版本
        info["SDK版本"] = prop.get("ro.build.version.sdk", "Unknow")  # SDK版本
        info["首选SDK版本"] = prop.get(
            "ro.product.first_api_level", "Unknow"
        )  # 首选SDK版本

        info["CPU平台"] = prop.get("ro.board.platform", "Unknow")

        info["CPU名称"] = await dev.cpu.cpu_name
        info["CPU架构"] = prop.get("ro.product.cpu.abi", "Unknow")  # CPU架构
        info["CPU核心"] = await dev.cpu.count
        freqs = await dev.cpu.freqs
        info["CPU频率"] = f"{freqs[0].min / 1000}MHZ - {freqs[0].max / 1000}MHZ"

        gpu_info = await dev.gpu.info
        info["GPU型号"] = f"{gpu_info.manufactor} {gpu_info.name}"
        info["OpenGL"] = gpu_info.opengl

        ram_info = await dev.mem.info
        info["RAM"] = f"{ram_info.mem_total / 1024 / 1024:.2f}GB"
        info["SWAP"] = f"{ram_info.swap_total / 1024 / 1024:.2f}GB"

        info["ROOT"] = str(not await dev.shell("su"))

        info["Serial"] = f"{dev.serialno}"
        return info

    async def remote_connect(self, ip: str, port: int):
        res = await self.adbc.remote_connect(ip, port)
        if res:
            serialno = ":".join([ip, str(port)])
            self.devices.add(serialno)
            self.on_devices_changed.on_next(self.devices)
            self.on_device_connected.on_next(serialno)
        return res

    async def adb_tcpip_enable(self, serialno: str):
        dev = await self.get_device(serialno)
        res = await dev.adbd_tcpip(5555)
        return res

    def start_scan_devices(self):
        if self._timer_scan_device:
            self._timer_scan_device.cancel()

        self._timer_scan_device = ui.timer(1, self._scan_devices, once=True)

    def stop_scan_devices(self):
        if self._timer_scan_device:
            self._timer_scan_device.cancel()

    async def _scan_devices(self):
        async for dev in self.adbc.devices_track():
            if dev.status == Status.DEVICE:
                if dev.serialno not in self._devices:
                    print(f"Device {dev.serialno} connected")
                    self._devices.add(dev.serialno)
                    self.on_devices_changed.on_next(self.devices)
                    self.on_device_connected.on_next(dev.serialno)
            elif dev.status == Status.OFFLINE:
                if dev.serialno in self._devices:
                    self._devices.remove(dev.serialno)
                    print(f"Device {dev.serialno} {dev.status} disconnected")
                    self.on_devices_changed.on_next(self.devices)
                    self.on_device_disconnected.on_next(dev.serialno)


AndroidProfielerService = _AndroidProfilerService()
