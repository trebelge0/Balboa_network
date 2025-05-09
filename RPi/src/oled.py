"""
* Master's Thesis *
Implementation of a robotic swarm platform
based on the Balboa self-balancing robot
© 2025 Romain Englebert
"""

import board
import digitalio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# To be used in a Blinka virtual environment with circuit python installed

class FILOBuffer:
    """
    Stack First in last out
    """
    def __init__(self, size=4):
        self.size = size
        self.stack = ["..."]*size

    def push(self, item):
        if len(self.stack) >= self.size:
            self.stack.pop(0)
        self.stack.append(item)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def __repr__(self):
        return f"Stack (top -> bottom): {list(reversed(self.stack))}"


# Gobal constants
WIDTH = 128
HEIGHT = 64
FONTSIZE = 50

# I²C communication
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

# Initialization
oled.fill(0)
oled.show()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

# Parameters
padding = -5
top = padding
bottom = oled.height - padding
x = 0
font = ImageFont.truetype('/home/trebelge/Documents/Balboa_Network/src/fonts/PixelOperator.ttf', FONTSIZE)

# To keep the 4 last messages
buffer = FILOBuffer(size=1)

def write(new_msg):
    """
    new_msg: string to be added to the buffer
    Show the content of the buffer
    """

    # Update buffer
    buffer.push(new_msg)

    # Write
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    for i in range(len(buffer.stack)):
        draw.text((x, top + FONTSIZE*i), buffer.stack[i], font=font, fill=255)

    # Display image
    oled.image(image)
    oled.show()
