import gc
import uos
import random
import machine
import jpegdec
import uasyncio
import sdcard
import WIFI_CONFIG
import network
from machine import Pin, PWM, Timer
from pimoroni_i2c import PimoroniI2C
import rp2
from pcf85063a import PCF85063A
import time
import inky_frame
import math
import sys

from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY  # 7.3"

import urequests
from urllib import urequest

# Device hostname on network
# If you have more than one device each needs a unique name
MYHOSTNAME = 'rp2-cal'

# Length of time between updates in Seconds.
# Frequent updates will reduce battery life!
UPDATE_INTERVAL = 60 * 1  # once 3 minutes for testing

# What to download
ENDPOINT = "http://192.168.1.172/calendar.jpg"

# And where to put it
FILENAME = "/sd/dashboard.jpg"

# WorldTime API including timezone
CURR_TIME_URL = "https://worldtimeapi.org/api/timezone/Europe/London"

"""
HA dashboard mk 1

You *must* insert an SD card into Inky Frame!
We need somewhere to save the jpg for display.
"""

# set the brightness of the network led
def network_led(brightness):
    brightness = max(0, min(100, brightness))  # clamp to range
    # gamma correct the brightness (gamma 2.8)
    value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
    network_led_pwm.duty_u16(value)

def network_led_callback(t):
    # updates the network led brightness based on a sinusoid seeded by the current time
    brightness = (math.sin(time.ticks_ms() * math.pi * 2 / (1000 / network_led_pulse_speed_hz)) * 40) + 60
    value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
    network_led_pwm.duty_u16(value)

# set the network led into pulsing mode
def pulse_network_led(speed_hz=1):
    global network_led_timer, network_led_pulse_speed_hz
    network_led_pulse_speed_hz = speed_hz
    network_led_timer.deinit()
    network_led_timer.init(period=50, mode=Timer.PERIODIC, callback=network_led_callback)

# turn off the network led and disable any pulsing animation that's running
def stop_network_led():
    global network_led_timer
    network_led_timer.deinit()
    network_led_pwm.duty_u16(0)

def network_connect(SSID, PSK):
    # Enable the Wireless
    wlan = network.WLAN(network.STA_IF)
    wlan.config(hostname=MYHOSTNAME)
    wlan.active(True)

    # Number of attempts to make before timeout
    max_wait = 180

    # Sets the Wireless LED pulsing and attempts to connect to your local network.
    pulse_network_led()
    wlan.connect(SSID, PSK)

    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    print(f'wlan.status: {wlan.status()}')
    stop_network_led()
    network_led_pwm.duty_u16(30000)

    # Handle connection error. Switches the Warn LED on.
    if wlan.status() != 3:
        stop_network_led()
        led_warn.on() 

try:
    sd_spi = machine.SPI(0, sck=machine.Pin(18, machine.Pin.OUT), mosi=machine.Pin(19, machine.Pin.OUT), miso=machine.Pin(16, machine.Pin.OUT))
    sd = sdcard.SDCard(sd_spi, machine.Pin(22))
    uos.mount(sd, "/sd")

    with open('/sd/log.txt', "at") as em:
                em.write("Startup \n")

    led_warn = Pin(6, Pin.OUT)

    # set up for the network LED
    network_led_pwm = PWM(Pin(7))
    network_led_pwm.freq(1000)
    network_led_pwm.duty_u16(0)

    network_led_timer = Timer(-1)
    network_led_pulse_speed_hz = 1
    
    wlan = network.WLAN(network.STA_IF)
    rp2.country('GB')

    time.sleep(5) # wait for things to settle

    gc.collect()  # We're really gonna need that RAM!

    graphics = PicoGraphics(DISPLAY)

    gc.collect()  # Claw back some RAM!  

    while True:
        led_warn.off()

        network_connect(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK)

        if wlan.status() != 3:
            led_warn.on()
            time.sleep(10)
            continue

        print("Connected!")

        timeJson = urequests.get(CURR_TIME_URL, timeout=60)
        currTime = timeJson.json()['datetime']
        date_time = currTime[:19] + currTime[-6:]
        
        gc.collect()

        WIDTH, HEIGHT = graphics.get_bounds()

        mysocket = myurequest.urlopen(ENDPOINT, timeout=60)

        # Stream the image data from the socket onto disk in 1024 byte chunks
        data = bytearray(1024)
        with open(FILENAME, "wb") as f:
            while True:
                if mysocket.readinto(data) == 0:
                    break
                f.write(data)
        mysocket.close()
        gc.collect()  # We really are tight on RAM!

        jpeg = jpegdec.JPEG(graphics)
        gc.collect()  # For good measure...

        graphics.set_pen(1)
        graphics.clear()

        jpeg.open_file(FILENAME)
        jpeg.decode(dither=False)
        
        # Add download time
        graphics.set_pen(0)
        graphics.set_font('bitmap6')
        graphics.text(f'Downloaded: {date_time}', 420, 465)

        graphics.update()
        
        gc.collect()  # For good measure...

        time.sleep(UPDATE_INTERVAL)
except Exception as err:
    errMsg = f"Unexpected err={err}, type(err)={type(err)}"
    timeJson = urequests.get(CURR_TIME_URL, timeout=60)
    currTime = timeJson.json()['datetime']
    date_time = currTime[:19] + currTime[-6:]
    with open('/sd/log.txt', "at") as em:
        em.write(date_time)
        em.write(errMsg + "\n")
        sys.print_exception(err, em)
    led_warn.on()
    time.sleep(30)
    with open('/sd/log.txt', "at") as em:
        em.write("reset... \n")
finally:    
    machine.reset()


