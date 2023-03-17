# main.py -- put your code here!# boot.py -- run on boot-up
import config
import plasma
from plasma import plasma_stick
import time
import network
from umqtt.simple import MQTTClient
import json
from random import random, uniform
import math


def strip_rgb(r,g,b):
    for i in range(NUM_LEDS):
        led_strip.set_rgb(i,r,g,b)

def strip_hsv(h,s,v):
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i,h,s,v)

def init_wifi():
    print("Connecting to WiFi")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.wifi_ssid, config.wifi_password)
    strip_rgb(125,0,0)
    time.sleep(3)
    if not wlan.isconnected():
        print("Couldn't connect to WiFi, restarting...")
        for i in range(10):
            strip_rgb(125*(i%2),0,0)
            time.sleep(0.5)
        strip_rgb(0,0,0)
        machine.reset()
    else:
        return

def mqtt_connect():
    print("Connecting to MQTT")
    strip_rgb(0,0,125)
    client = MQTTClient(config.mqtt_client_id,
                        config.mqtt_server,
                        config.mqtt_port,
                        config.mqtt_user,
                        config.mqtt_password,
                        keepalive = 3600)
    client.connect()
    client.set_callback(command_cb)
    client.subscribe(config.mqtt_command_topic)
    strip_rgb(0,0,0)
    return client

def reconnect():
    print("Couldn't connect to MQTT, restarting...")
    for i in range(10):
        strip_rgb(0,0,125*(i%2))
        time.sleep(0.5)
    strip_rgb(0,0,0)
    machine.reset()

def solid():
    h = internal_state["color"]["h"]/360
    s = internal_state["color"]["s"]
    v = 0.95
    strip_hsv(h,s,v)

def rainbow():
    global SPEED
    global rainbow_offset
    SPEED = min(255, max(1, SPEED))
    rainbow_offset += float(SPEED) / 2000.0
    for i in range(NUM_LEDS):
        hue = float(i) / NUM_LEDS
        led_strip.set_hsv(i, hue + rainbow_offset, 1.0, 1.0)
        
def fire():
    for i in range(NUM_LEDS):
        led_strip.set_hsv(i, uniform(0.0, 50 / 360), 1.0, random())
    time.sleep(0.1)

def breathing():
    global SPEED
    global breathing_angle
    SPEED = min(255, max(1, SPEED))
    breathing_angle += float(SPEED) / 800.0
    h = internal_state["color"]["h"]/360
    s = internal_state["color"]["s"]
    v = math.sin(breathing_angle)*0.3 + 0.65
    strip_hsv(h,s,v)

def pulse():
    global SPEED
    global pulse_offset
    SPEED = min(255, max(1, SPEED))
    pulse_offset += float(SPEED) / 1000.0
    for i in range(NUM_LEDS):
        h = internal_state["color"]["h"]/360
        s = internal_state["color"]["s"]
        v = (math.sin(float(i) / NUM_LEDS * 4 + pulse_offset)) * 0.35 + 0.6
        led_strip.set_hsv(i,h,s,v)

def command_cb(topic,msg):
    try:
        command = json.loads(msg)
        internal_state.update(command)
        MESSAGE_FLAG = 1
        print(internal_state)
    except ValueError:
        pass


NUM_LEDS = config.led_num

SPEED = config.led_animation_speed

UPDATES = config.led_updates

MQTT_UPDATES = config.mqtt_status_update * UPDATES * 60

MESSAGE_FLAG = 0

mqtt_update_step_counter = 0 

# WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma_stick.DAT, color_order=plasma.COLOR_ORDER_RGB)

# Start updating the LED strip
led_strip.start()

rainbow_offset = 0.0
breathing_angle = 0.0
pulse_offset = 0.0

internal_state = {"state":"OFF",
                  "color":{"h":0.0,"s":1.0},
                  "effect":"solid"
                 }

print("Initialising")

init_wifi()

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()

strip_rgb(0,0,0)
print("initialisation is finished")
#client.publish(config.mqtt_state_topic,"online")

while True:
    client.check_msg()
    
    if MESSAGE_FLAG == 1:
        client.publish(config.mqtt_state_topic,json.dumps(internal_state))
        MESSAGE_FLAG = 0

    if mqtt_update_step_counter == MQTT_UPDATES:
        client.publish(config.mqtt_state_topic,json.dumps(internal_state))
        mqtt_update_step_counter = 0
    else:
        mqtt_update_step_counter = mqtt_update_step_counter + 1

    if internal_state["state"] == "ON":
        if internal_state["effect"] == "solid":
            solid()
        elif internal_state["effect"] == "rainbow":
            rainbow()
        elif internal_state["effect"] == "fire":
            fire()
        elif internal_state["effect"] == "breathing":
            breathing()
        elif internal_state["effect"] == "pulse":
            pulse()
    elif internal_state["state"] == "OFF":
        internal_state.update({"state":"OFF"})
        strip_rgb(0,0,0)

    time.sleep(1.0 / UPDATES)