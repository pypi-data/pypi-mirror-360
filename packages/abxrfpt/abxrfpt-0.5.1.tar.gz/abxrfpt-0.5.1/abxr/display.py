#
# Copyright (c) 2024-2025 ABXR Labs, Inc.
# Released under the MIT License. See LICENSE file for details.
#

import io
import time
from abxr.version import version

i2c = None
disp = None

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception:
        pass
    
    return False


if is_raspberrypi():
    from board import SCL, SDA
    import busio
    import adafruit_ssd1306

    i2c = busio.I2C(SCL, SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)


class Display:
    LINE_HEIGHT = 8
    MAX_CHARACTERS_PER_LINE = 21

    LINE_POSITIONS = [
        LINE_HEIGHT * 0,
        LINE_HEIGHT * 1,
        LINE_HEIGHT * 2,
        LINE_HEIGHT * 3
    ]

    def __init__(self):
        self.disp = disp
        self.font_file = "abxr/font5x8.bin"
        self.line_height = 8

    def show(self):
        if self.disp:
            self.disp.show()

    def clear(self):
        if self.disp:
            self.fill(0)
            self.show()

    def text(self, text, x, y, color):
        if self.disp:
            self.disp.text(text, x, y, color, font_name=self.font_file)

    def fill(self, color):
        if self.disp:
            self.disp.fill(color)

    def show(self):
        if self.disp:
            self.disp.show()

    def write(self, text, wait=0):
        if self.disp is None:
            return

        self.clear()

        if type(text) is str:
            text = [ text ]

        wrapped_text = []
        for line in text:
            if len(line) > self.MAX_CHARACTERS_PER_LINE:
                for i in range(0, len(line), self.MAX_CHARACTERS_PER_LINE):
                    wrapped_text.append(line[i:i + self.MAX_CHARACTERS_PER_LINE].strip())
            else:
                wrapped_text.append(line)

        current_line = 0
        for line in wrapped_text:
            if current_line >= len(self.LINE_POSITIONS):
                break
            self.text(line, 0, self.LINE_POSITIONS[current_line], 255)
            current_line += 1
            
        self.show()

        if wait:
            time.sleep(wait)

   


display = Display()

