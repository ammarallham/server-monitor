#!/usr/bin/env python3
"""
monitor.py - Linux Server Health Monitor
Author: Eng. Ammar Allham

Collects key health metrics from a Linux server (hostname, current user,
date/time, OS, kernel, CPU, memory, disk, IP address, uptime) and
generates a plain-text report inside reports/server_report.txt.
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


REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "server_report.txt")


def get_hostname():
    return socket.gethostname()


def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        # os.getlogin() can fail when there's no controlling terminal
        # (e.g. run via cron, SSH without a tty, or some IDEs)
        return getpass.getuser()


def get_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def get_os_info():
    try:
        # Reads /etc/os-release for a clean distro name, e.g. "Ubuntu 24.04"
        info = platform.freedesktop_os_release()
        return info.get("PRETTY_NAME", platform.platform())
    except Exception:
        return f"{platform.system()} {platform.release()}"


def get_kernel_version():
    return platform.release()


def get_cpu_usage():
    # interval=1 samples over 1 second for an accurate reading
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


def get_ip_address():
    # Trick: open a UDP "connection" to a public IP (no data is actually sent)
    # to reliably discover the primary outbound IPv4 address, avoiding the
    # common Ubuntu pitfall of gethostname() resolving to 127.0.1.1.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_uptime():
    boot_timestamp = psutil.boot_time()
    uptime_seconds = datetime.datetime.now().timestamp() - boot_timestamp
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    return f"{days} Days {hours} Hours"


def collect_report_data():
    mem = get_memory_usage()
    disk = get_disk_usage()
    return {
        "hostname": get_hostname(),
        "current_user": get_current_user(),
        "date": get_datetime(),
        "os": get_os_info(),
        "kernel": get_kernel_version(),
        "cpu_usage": f"{get_cpu_usage()}%",
        "memory": mem,
        "disk": disk,
        "ip_address": get_ip_address(),
        "uptime": get_uptime(),
    }


def format_report(data):
    lines = [
        "=" * 32,
        "SERVER HEALTH REPORT",
        "=" * 32,
        "",
        f"Hostname      : {data['hostname']}",
        f"Current User  : {data['current_user']}",
        f"Date          : {data['date']}",
        f"Operating Sys : {data['os']}",
        f"Kernel        : {data['kernel']}",
        f"CPU Usage     : {data['cpu_usage']}",
        "",
        "Memory Usage",
        f"  Total : {data['memory']['total_gb']} GB",
        f"  Used  : {data['memory']['used_gb']} GB",
        f"  Free  : {data['memory']['free_gb']} GB",
        f"  Usage : {data['memory']['percent']}%",
        "",
        "Disk Usage",
        f"  Filesystem : {data['disk']['filesystem']}",
        f"  Used       : {data['disk']['used_gb']} GB",
        f"  Available  : {data['disk']['free_gb']} GB",
        f"  Usage      : {data['disk']['percent']}%",
        "",
        f"IP Address    : {data['ip_address']}",
        f"Uptime        : {data['uptime']}",
        "=" * 32,
    ]
    return "\n".join(lines)


def write_report(report_text):
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        f.write(report_text + "\n")


def main():
    data = collect_report_data()
    report_text = format_report(data)

    # Print to console (for live viewing / screenshots)
    print(report_text)

    # Save to reports/server_report.txt
    write_report(report_text)
    print(f"\n[OK] Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
