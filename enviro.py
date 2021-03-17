# -*- coding: utf-8 -*-
 
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from math import *


import busio
import adafruit_scd30

import paho.mqtt.publish as publish
from influxdb import InfluxDBClient

def TempToRgb(Temperature):
    Angle = Temperature*5
    AngleRad = radians(Angle)

    R = int(-cos(AngleRad)*255)
    G = int(sin(AngleRad)*255)
    B = int(cos(AngleRad)*255)

    if R < 0 : R = 0
    if G < 0 : G = 0
    if B < 0 : B = 0

    couleur_texte =  (R,G,B)
    return R,G,B


i2c = busio.I2C(board.SCL, board.SDA)
scd = adafruit_scd30.SCD30(i2c)
# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
 
# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000
 
# Setup SPI bus using hardware SPI:
spi = board.SPI()
 
# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)
 
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 0
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
 
 
# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
fontTemp = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 70)
fontTime = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
    if scd.data_available:
        CO2 = "CO2 : " + str(round(scd.CO2,0)) + " PPM"
        temperature = round((scd.temperature-2.4),1)
        Temperature = str(temperature) + "°c"
        Humidity = "Humidité : " + str(round(scd.relative_humidity,1)) + "%"
        Heure = time.strftime("%H:%M", time.localtime())
        # Write four lines of text.
        y = top
        draw.text((x, y), Heure, font=fontTime, fill=(255, 255, 255))
        y += fontTime.getsize(Heure)[1]+10
        R,G,B = TempToRgb(temperature)
        draw.text((x, y), Temperature, font=fontTemp, fill=(R,G,B))
        y += fontTemp.getsize(Temperature)[1]+20
        draw.text((x, y), CO2, font=font, fill="#FFFFFF")

        try:
            publish.single("chambre/temperature", temperature, hostname="xxx.xxx.xxx.xxx")
            publish.single("chambre/humidity", round(scd.relative_humidity,1), hostname="xxx.xxx.xxx.xxx")
            publish.single("chambre/co2", round(scd.CO2,0), hostname="xxx.xxx.xxx.xxx")
        except:
            pass

 
    # Display image.
    disp.image(image, rotation)

    time.sleep(60)

