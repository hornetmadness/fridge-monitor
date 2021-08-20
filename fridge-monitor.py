#!/usr/bin/env python3
#Created by Erik Mathis 08/2021
#hornetmadness@gmail.com

#This script polls the DS18B20 Temperature Sensor and creates an
#average over a period of time. Each poll result are written to a
#file in json format for another script to read and deside if the
#temp is correct. It also displays the current info on a OLED display
#   https://www.amazon.com/gp/product/B08RJ59BDJ
#   http://www.diymalls.com/DIYmall-PiOLED-0.91inch-OLED-for-Raspberry-Pi

import os
import sys
import time
from w1thermsensor import W1ThermSensor, Unit
import json
from datetime import datetime
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import busio
import logging
import logging.handlers
from statistics import stdev
import atexit

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
logger.addHandler(handler)

max_age=int(os.getenv('MAX_AGE', 300))
results_file=os.getenv('RESULTS_FILE', "/run/user/1000/temp_results")
enable_syslog=os.getenv('ENABLE_SYSLOG', 0)
pid_file=os.getenv('PID_FILE', "/run/fridge-monitor.pid")
cache=dict()
latest=int()
max_temp=float()
min_temp=float(10000000)
last_temp=float()

def log_error(line):
    if enable_syslog == 1:
        logger.error(line)
def log_warn(line):
    if enable_syslog == 1:
        logger.warn(line)
def log_info(line):
    if enable_syslog == 1:
        logger.info(line)

def Average(lst):
    if not lst:
        return -1
    return float(f"{sum(lst) / len(lst):.1f}")

def Standard_Deviation(lst):
   return float(f"{stdev(lst):.1f}")

def get_temp(sensor):
    return float(f"{sensor.get_temperature(Unit.DEGREES_F):.1f}")

def calculate_temp(current):
    global cache, min_temp, max_temp, latest, last_temp
    now=int(datetime.now().strftime("%s"))
    latest=now

    if not cache:
        new={
            "max": current,
            "min": current,
            "avg": current,
            "temp": current,
            "time": now,
            "last": current,
            "stdev": 0,
        }
        cache[now]=new
        return

    delete=list()
    keep=list()
    past_temp=list()

    for a in cache:
        if now - a <= max_age:
            keep.append(a)
        else:
            delete.append(a)

    for entry in keep:
        ref=cache[entry]
        if current < min_temp:
            min_temp=current
        if current > max_temp:
            max_temp=current
        past_temp.append(ref['temp'])

    past_temp.append(current)

    new={
        "avg": Average(past_temp),
        "min": min_temp,
        "max": max_temp,
        "temp": current,
        "time": now,
        "last": last_temp,
        "stdev": Standard_Deviation(past_temp),
    }
    cache[now]=new
    last_temp=current
    keep.append(now)

    for d in delete:
        #We reset these because we dont care about
        #min/max that is out side of our window
        if cache[d]['max'] == max_temp:
            max_temp=current
        if cache[d]['min'] == min_temp:
            min_temp=current
        del cache[d]

def write_results():
    file=open(results_file, 'w')
    file.writelines(json.dumps(cache[latest]))
    file.close()

def draw_display(draw, disp, width, height, top, x, image, font, err=None):
    if err:
       draw.rectangle((0, 0, width, height), outline=0, fill=0)
       draw.text((x, top+16), err, font=font, fill=255)
       disp.image(image)
       disp.show()
       log_error(err)
       sys.exit(1)

    ref=cache[latest]
    direction="="
    if ref['last'] > ref['temp']: 
        direction="-"
    if ref['last'] < ref['temp']:
        direction="+"

    line1=f"MIN: {ref['min']} MAX: {ref['max']}"
    line2=f"AVG:{ref['avg']} TEMP:{ref['temp']}{direction}"
    line3=f"{datetime.now().strftime('%A %h %m')}"
    line4=f"{datetime.now().strftime('%I:%M:%S %p')}"

    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x, top+8), line1, font=font, fill=255)
    draw.text((x, top+16), line2, font=font, fill=255)
    draw.text((x, top+24), line3, font=font, fill=255)
    draw.text((x, top+32), line4, font=font, fill=255)
    disp.image(image)
    disp.show()

def all_done():
    os.remove(pid_file)

def write_pid_file():
    pid = str(os.getpid())
    f = open(pid_file, 'w')
    f.write(pid)
    f.close()

def init():
    if os.path.exists(pid_file):
       log_error(f"The pid fle {pid_file} already exists")
       sys.exit(1)

    if os.path.exists(results_file):
        os.remove(results_file)

    atexit.register(all_done)
    write_pid_file()

    log_info(f"Results File: {results_file}, Max Age: {max_age}, Pid File {pid_file}, enable_syslog: {enable_syslog}")

if __name__ == '__main__':
    init()

    # Create the I2C interface.
    i2c = busio.I2C(SCL, SDA)
    # Create the SSD1306 OLED class.
    # The first two parameters are the pixel width and pixel height.  Change these
    # to the right size for your display!
    disp = adafruit_ssd1306.SSD1306_I2C(128, 40, i2c)
    # Clear display.
    disp.fill(0)
    disp.show()
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0
    # Load default font.
    font = ImageFont.load_default()

    try:
        temp_sensor = W1ThermSensor()
    except:
        error="TermSensor not found"
        draw_display(draw, disp, width, height, top, x, image, font, error)

    while True:
        # print(f"Size: {sys.getsizeof(cache)}")
        current=get_temp(temp_sensor)
        calculate_temp(current)
        write_results()
        draw_display(draw, disp, width, height, top, x, image, font)
        log_info(f"- {cache[latest]}")
        time.sleep(2)
