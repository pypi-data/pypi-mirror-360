import os
import ctypes
import sys

os.system('color')


kernel32 = ctypes.windll.kernel32
stdout_handle = kernel32.GetStdHandle(-11)

black = 0x0000
blue = 0x0001
green = 0x0002
cyan = 0x0003
red = 0x0004
magenta = 0x0005
yellow = 0x0006
grey = 0x0007
intensity = 0x0008

def set_red():
    if os.isatty(sys.stdout.fileno()):
        current_bg = _get_current_background()
        kernel32.SetConsoleTextAttribute(stdout_handle, red | current_bg)

def set_yellow():
    if os.isatty(sys.stdout.fileno()):
        current_bg = _get_current_background()
        kernel32.SetConsoleTextAttribute(stdout_handle, yellow | current_bg)

def set_green():
    if os.isatty(sys.stdout.fileno()):
        current_bg = _get_current_background()
        kernel32.SetConsoleTextAttribute(stdout_handle, green | current_bg)

def set_intensity():
    if os.isatty(sys.stdout.fileno()):
        current_bg = _get_current_background()
        kernel32.SetConsoleTextAttribute(stdout_handle, intensity | current_bg)

def _get_current_background():
    csbi = ctypes.create_string_buffer(22)
    res = kernel32.GetConsoleScreenBufferInfo(stdout_handle, csbi)
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        bg = wattr & 0x0070
        return bg
    else:
        return black
