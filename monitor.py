#!/usr/bin/env python3
"""
monitor.py - Linux Server Health Monitor
Author: Eng. Ammar Allham
"""

import os
import socket
import getpass


def get_hostname():
    return socket.gethostname()


def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        return getpass.getuser()


def main():
    hostname = get_hostname()
    current_user = get_current_user()

    print(f"Hostname     : {hostname}")
    print(f"Current User : {current_user}")


if __name__ == "__main__":
    main()
