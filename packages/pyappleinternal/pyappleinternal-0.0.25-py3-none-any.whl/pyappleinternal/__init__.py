import os
import subprocess
import re
import textwrap
import sys
import platform

def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS 
        resource_path = os.path.join(base_path, 'pyappleinternal', filename)
    else:
        base_path = os.path.dirname(__file__)
        resource_path = os.path.join(base_path, filename)
    return resource_path

def get_libusb_path():
    arch = platform.machine()
    if arch == 'x86_64':
        path = get_resource_path(os.path.join('lib', 'x86_64', 'libusb-1.0.dylib'))
    elif arch == 'arm64':
        path = get_resource_path(os.path.join('lib', 'arm64', 'libusb-1.0.dylib'))
    else:
        raise RuntimeError(f'Unsupported architecture: {arch}')
    return path

def get_tcprelay_path():
    return get_resource_path(os.path.join('bin', 'tcprelay'))

