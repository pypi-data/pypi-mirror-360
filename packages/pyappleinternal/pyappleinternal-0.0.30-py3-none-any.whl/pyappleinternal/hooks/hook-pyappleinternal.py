import os
import pyappleinternal
pkg_dir = os.path.dirname(pyappleinternal.__file__)

arches = ['x86_64', 'arm64']
datas = []

for arch in arches:
    libusb_path = os.path.join(pkg_dir, 'lib', arch, 'libusb-1.0.dylib')
    datas.append((libusb_path, f'pyappleinternal/lib/{arch}'))

tcprelay_path = os.path.join(pkg_dir, 'bin', 'tcprelay')
datas.append((tcprelay_path, 'pyappleinternal/bin'))