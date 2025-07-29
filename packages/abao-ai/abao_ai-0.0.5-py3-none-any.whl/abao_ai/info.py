import psutil
from pprint import pprint
import shutil
import yaml
from cuda.bindings.runtime import cudaGetDeviceCount, cudaGetDeviceProperties
import argparse
import os


class DeviceInfo:
    def __init__(self, index: int, name: str, vram: str, capability: str) -> None:
        self.index = index
        self.name = name
        self.vram = vram
        self.capability = capability


def get_devices() -> list[dict[str, str]]:
    devices = []
    _, count = cudaGetDeviceCount()
    for i in range(count):
        _, props = cudaGetDeviceProperties(i)
        name = props.name.decode("utf-8")
        name = name.replace(" ", "_")
        vram = f"{props.totalGlobalMem / (1024**3):.2f} GB"
        capability = f"{props.major}.{props.minor}"
        device_info = {
            "index": str(i),
            "name": name,
            "vram": vram,
            "capability": capability,
        }
        devices.append(device_info)

    return devices


def get_ram() -> dict[str, str]:
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total
    available_memory = memory_info.available
    used_memory = memory_info.used
    free_memory = memory_info.free
    memory_percentage = memory_info.percent

    info = {
        "Total Memory": f"{total_memory / (1024**3):.2f} GB",
        "Available Memory": f"{available_memory / (1024**3):.2f} GB",
        "Used Memory": f"{used_memory / (1024**3):.2f} GB",
        "Free Memory": f"{free_memory / (1024**3):.2f} GB",
        "Memory Usage Percentage": f"{memory_percentage}%",
    }
    return info


def get_disk() -> dict[str, str]:
    path = "/"

    try:
        total, used, free = shutil.disk_usage(path)
        total_gib = total / (1024**3)
        used_gib = used / (1024**3)
        free_gib = free / (1024**3)

        info = {
            f"Total Disk": f"{total_gib:.2f} GiB",
            f"Used Disk": f"{used_gib:.2f} GiB",
            f"Free Disk": f"{free_gib:.2f} GiB",
            f"Disk Usage Percentage": f"{used_gib/total_gib *100:.2f}%",
        }
        return info
    except Exception as e:
        return {}


def print_info():
    devices = get_devices()
    ram = get_ram()
    disk = get_disk()
    info = {
        "devices": devices,
        "ram": ram,
        "disk": disk,
    }
    print(yaml.safe_dump(info))
