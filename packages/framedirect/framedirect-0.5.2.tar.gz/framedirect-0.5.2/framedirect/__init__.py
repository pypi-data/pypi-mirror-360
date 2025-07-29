# Made and developed by gneval9 Software
# 01-07-2025

import mmap
import os
import struct
import warnings


RED     = 0xFFFF0000
GREEN   = 0xFF00FF00
BLUE    = 0xFF0000FF
WHITE   = 0xFFFFFFFF
BLACK   = 0xFF000000
YELLOW  = 0xFFFFFF00
CYAN    = 0xFF00FFFF
MAGENTA = 0xFFFF00FF
GRAY    = 0xFF888888
ORANGE  = 0xFFFFA500


fb = None
fb_mem = None
screen_width = 0
screen_height = 0
bits_per_pixel = 32


def init():
    global fb, fb_mem, screen_width, screen_height, bits_per_pixel
    fb = os.open("/dev/fb0", os.O_RDWR)

    try:
        with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
            res = f.read().strip()
            screen_width, screen_height = map(int, res.split(","))
    except Exception as e:
        raise RuntimeError(f"No se pudo obtener la resolución del framebuffer: {e}")


    bits_per_pixel = 32

    fb_mem = mmap.mmap(fb, screen_width * screen_height * (bits_per_pixel // 8),
                       mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ, offset=0)


def draw_pixel(x, y, color):
    if fb_mem is None:
        raise RuntimeError("init() no ha sido llamada o framebuffer cerrado.")
    offset = (y * screen_width + x) * 4
    fb_mem.seek(offset)
    fb_mem.write(struct.pack('I', color))



def draw_line(x1, y1, x2, y2, color):
    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        draw_pixel(x1, y1, color)
        return

    x_inc = dx / steps
    y_inc = dy / steps

    x = x1
    y = y1

    for _ in range(steps + 1):
        draw_pixel(round(x), round(y), color)
        x += x_inc
        y += y_inc


def draw_circle(cx, cy, radius, color):
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            dist2 = (x - cx)**2 + (y - cy)**2
            if (radius - 1)**2 <= dist2 <= (radius + 1)**2:
                draw_pixel(x, y, color)



def resolution():
        print(screen_width, "x", screen_height)


def close():
    global fb, fb_mem
    if fb_mem is not None:
        fb_mem.close()
        fb_mem = None
    if fb is not None:
        os.close(fb)
        fb = None
