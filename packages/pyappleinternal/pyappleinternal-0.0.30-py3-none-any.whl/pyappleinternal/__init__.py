import os
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
    if "arm" in arch:
        path = get_resource_path(os.path.join('lib', 'arm64', 'libusb-1.0.dylib'))
    else:
        path = get_resource_path(os.path.join('lib', 'x86_64', 'libusb-1.0.dylib'))
    return path

def get_tcprelay_path():
    return get_resource_path(os.path.join('bin', 'tcprelay'))

