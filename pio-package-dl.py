from enum import Enum
import os
import sys
import platform

from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile, ZipInfo


class ZipFileWithPermissions(ZipFile):
    # Custom ZipFile class handling file permissions
    def _extract_member(self, member, targetpath, pwd):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        targetpath = super()._extract_member(member, targetpath, pwd)

        attr = member.external_attr >> 16
        if attr != 0:
            os.chmod(targetpath, attr)
        return targetpath


class OS(Enum):
    WINDOWS = 1
    MAC_INTEL = 2
    MAC_ARM = 3
    OTHER = 4


def determine_current_os():
    if platform.system() == 'Windows':
        return OS.WINDOWS
    elif platform.system() == 'Darwin':
        if platform.processor() == 'i386':
            return OS.MAC_INTEL
        else:
            return OS.MAC_ARM
    else:
        return OS.OTHER


def confirm_prompt(question: str) -> bool:
    reply = None
    while reply not in ("y", "n"):
        reply = input(f"{question} (y/n): ").casefold()
    return (reply == "y")


def download_and_unzip(url, output_path):
    with urlopen(url) as resp:

        # Determine final file size
        file_length = resp.getheader('content-length')
        if file_length:
            file_length = int(file_length)
            blocksize = max(4096, file_length//100)
        else:
            blocksize = 1000000 # arbitrary

        # Print out final file size
        print(f'Download size: {file_length / 1000000} MB')

        # Download and load file to buffer (while printing out progress)
        buf = BytesIO()
        size = 0
        while True:
            temp_buf = resp.read(blocksize)
            if not temp_buf:
                break
            buf.write(temp_buf)
            size += len(temp_buf)
            if file_length:
                print('{:.2f}%\r'.format(size/file_length * 100), end='')
        print('\n')

        # Unzip file into target location
        print('Extracting...')
        with ZipFileWithPermissions(buf) as zfile:
            zfile.extractall(output_path)


if __name__ == '__main__':

    # Print some information
    print('*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')
    print('*=*= 6.190 PlatformIO Packages Download Script =*=*')
    print('*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*')
    print()
    
    # Determine current os
    current_os = determine_current_os()
    if current_os == OS.OTHER:
        print('Unable to determine operating system. This script only works for Windows and MACOS computers.')
        exit()

    # Construct .platformio path
    pio_path = os.path.join(os.path.expanduser('~'), '.platformio')

    # Set target download link
    if current_os == OS.WINDOWS:
        packages_url = "https://github.com/geoffreywwang/6190-pio-dl/releases/download/v1.0.0/packages-windows.zip"
    elif current_os == OS.MAC_INTEL:
        packages_url = "https://github.com/geoffreywwang/6190-pio-dl/releases/download/v1.0.0/packages-mac-intel.zip"
    elif current_os == OS.MAC_ARM:
        packages_url = "https://github.com/geoffreywwang/6190-pio-dl/releases/download/v1.0.0/packages-mac-arm.zip"
    else:
        packages_url = None

    # Prompt user to verify information
    print('Please verify the following information:')
    print(f' - OS:\n\t{current_os}')
    print(f' - .platformio path:\n\t{pio_path}')
    print()

    response = confirm_prompt("Continue with installation?")
    if not response:
        exit()
    print()

    # Download correct packages.zip and unzip in proper location
    download_and_unzip(packages_url, pio_path)

    print('Done!')