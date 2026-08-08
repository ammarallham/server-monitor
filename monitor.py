#!/usr/bin/env python3
"""
monitor.py - Linux Server Health Monitor
Author: Eng. Ammar Allham
"""

import os
import socket
import platform
import getpass
import datetime

try:
    import psutil
except ImportError:
    print("[ERROR] The 'psutil' package is required. Install it with:")
    print("        pip install psutil")
    raise SystemExit(1)


def get_hostname():
    return socket.gethostname()


def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


def get_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def get_os_info():
    try:
        info = platform.freedesktop_os_release()
        return info.get("PRETTY_NAME", platform.platform())
    except Exception:
        return f"{platform.system()} {platform.release()}"


def get_kernel_version():
    return platform.release()


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "free_gb": round(mem.available / (1024 ** 3), 2),
        "percent": mem.percent,
    }


def get_disk_usage(path="/"):
    disk = psutil.disk_usage(path)
    return {
        "filesystem": path,
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
    }


def main():
    mem = get_memory_usage()
    disk = get_disk_usage()

    print(f"Hostname      : {get_hostname()}")
    print(f"Current User  : {get_current_user()}")
    print(f"Date          : {get_datetime()}")
    print(f"Operating Sys : {get_os_info()}")
    print(f"Kernel        : {get_kernel_version()}")
    print(f"CPU Usage     : {get_cpu_usage()}%")

    print("\nMemory Usage")
    print(f"  Total : {mem['total_gb']} GB")
    print(f"  Used  : {mem['used_gb']} GB")
    print(f"  Free  : {mem['free_gb']} GB")
    print(f"  Usage : {mem['percent']}%")

    print("\nDisk Usage")
    print(f"  Filesystem : {disk['filesystem']}")
    print(f"  Used       : {disk['used_gb']} GB")
    print(f"  Available  : {disk['free_gb']} GB")
    print(f"  Usage      : {disk['percent']}%")


if __name__ == "__main__":
    main()
