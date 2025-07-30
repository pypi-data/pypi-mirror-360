from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

from PIL import Image, ImageDraw, ImageFont
import subprocess
import time

# Display Refresh Interval
LOOPTIME = 1.0

# Set up I2C and SH1106 device
serial = i2c(port=1, address=0x3C)
oled = sh1106(serial, width=128, height=64)

# Create a blank image for drawing
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Load custom font
from importlib.resources import files

font_path = files(__package__).joinpath("PixelOperator.ttf")
font = ImageFont.truetype(str(font_path), 16)


while True:
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # System stats commands
    IP = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip()
    CPU = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'", shell=True).decode().strip()
    Temp = subprocess.check_output("vcgencmd measure_temp |cut -f 2 -d '='", shell=True).decode().strip()
    MemUsage = subprocess.check_output("free -m | awk 'NR==2{printf \"%.1f %.1f %.1f\", $3/1024,$2/1024,($3/$2)*100}'", shell=True).decode().strip()
    Disk = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'", shell=True).decode().strip()

    mem_parts = MemUsage.split()
    mem_display = f"Mem: {mem_parts[0]}/{mem_parts[1]}GB {mem_parts[2]}%"

    # Draw text
    draw.text((0, 0), f"IP: {IP}", font=font, fill=255)
    draw.text((0, 16), f"{CPU} LA", font=font, fill=255)
    draw.text((80, 16), f"{Temp}", font=font, fill=255)
    draw.text((0, 32), mem_display, font=font, fill=255)
    draw.text((0, 48), f"{Disk}", font=font, fill=255)

    # Display image
    oled.display(image)

    time.sleep(LOOPTIME)
