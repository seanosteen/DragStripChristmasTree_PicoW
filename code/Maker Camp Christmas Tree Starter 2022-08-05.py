# a PICO W powered drag race "Chistmas Tree" designed to be used at Pinewood Derbies.
# Created at Maker Alliance Summer Camp, on August 4, 2022 in Elizabethtown, Kentucky.
# Software and hardware were donated to a local Cub Scout pack at the end of Camp.
# Software is provided as-is and without warranty
# Contributors:
#  Sean O'Steen - @TinkeringRocks - sean@tinkeringrocks.com
#  Halbert Walston - halbert.walston@gmail.com
#
import time, array
from machine import Pin
import rp2
import random
import socket

import network
ssid = 'StartLights'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)
# Pixel mappings for each light group in the Christmas Tree
PG_PRESTAGE = [0,1,2,3,4,5,6,7,8,9,10]
PG_STAGE = [11,12,13,14,15,16,17,18,19,20,21]
PG_YELLOW1 = [22,23,24,57,56,55]
PG_YELLOW2 = [26,27,28,53,52,51]
PG_YELLOW3 = [30,31,32,49,48,47]
PG_GREEN = [34,35,36,45,44,43]
PG_GREEN2 = [37,38,39,40,41,42]

#How fast does each light flash
BLINKSPEED_MS = 100
 
# Configure the number of WS2812 LEDs, pins and brightness.
NUM_LEDS = 58
PIN_NUM = 22
brightness = .7
 
 
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
 
 
# Create the StateMachine with the ws2812 program, outputting on Pin(16).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
 
# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
 
# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])
 
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)
 
def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]
    
def pixel_group_set(pg, color):
    for i in range(len(pg)):
        pixels_set(pg[i], color)
 
def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
 
 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE, BLACK)



def race_start():
    for i in range(random.randint(2,7)):
        pixels_fill(BLACK)
        pixels_show()
        time.sleep_ms(BLINKSPEED_MS)
        pixel_group_set(PG_PRESTAGE, PURPLE)
        pixels_show()
        time.sleep_ms(BLINKSPEED_MS)
        pixels_fill(BLACK)
    for i in range(random.randint(2,7)):
        pixels_fill(BLACK)
        pixels_show()
        time.sleep_ms(BLINKSPEED_MS)
        pixel_group_set(PG_PRESTAGE, BLUE)
        pixel_group_set(PG_STAGE, BLUE)
        pixels_show()
        time.sleep_ms(BLINKSPEED_MS)
        pixels_fill(BLACK)
    pixel_group_set(PG_PRESTAGE, RED)
    pixel_group_set(PG_STAGE, RED)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS*10)
    pixels_fill(BLACK)
    pixel_group_set(PG_YELLOW1, YELLOW)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS)
    pixels_fill(BLACK)
    pixel_group_set(PG_YELLOW2, YELLOW)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS)
    pixels_fill(BLACK)
    pixel_group_set(PG_YELLOW3, YELLOW)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS)
    pixels_fill(BLACK)
    pixel_group_set(PG_GREEN, GREEN)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS)
    pixels_fill(BLACK)
    pixel_group_set(PG_GREEN2, GREEN)
    pixels_show()
    time.sleep_ms(BLINKSPEED_MS*10)
    pixels_fill(BLACK)
    pixels_show()

############################################
    
# Roll through colors as a POST    
for color in COLORS:
    pixels_fill(color)
    pixels_show()
    time.sleep(0.5)


html = """<!DOCTYPE html>
<html>
    <head> <title>Pinewood Derby Start Lights</title> </head>
    <body> 
        <p style='font-size:100px;'><a href='/start/'>START</a></p>
    </body>
</html>


"""

max_wait = 10
while max_wait > 0:
    if ap.status() < 0 or ap.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if ap.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = ap.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        
        request = cl.recv(1024)
        request = str(request)
        start = request.find('/start/')
        if start == 6:
            race_start()
            

        response = html

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')


    


