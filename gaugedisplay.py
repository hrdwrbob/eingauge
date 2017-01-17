import serial
import struct
import time
import pygame, sys
import numpy as np
from pygame.locals import *
REFRESHDELAY=100
screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
pygame.font.init()
rawdata = dict()
realdata = dict()
arduinomap = dict()
arduinomap['iat'] = [99, 125, 155, 190, 229, 272, 319, 368, 419, 470, 521, 570, 616, 660, 700, 737, 770, 800, 827, 850, 871, 889, 905, 919, 931, 942, 951, 959, 966, 972, 978 ]
arduinomap['temp'] = [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
arduinomap['tempsensor'] = [0, 20, 40, 80, 120, 160, 203, 239, 279, 321, 361, 409, 458, 500, 530, 558, 601, 631, 666, 701, 736, 771, 806, 841, 876, 911, 946, 981, 1016, 1051, 1086]
ser = serial.Serial('/dev/ttyACM0')
ser.write(b'1')
time.sleep(1) # Settle the serial.
def get_data():
  ser.write(b'1')
  x = ser.read(3)
  rawdata['enginemap'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['oilpressure'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['fuelpressure'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['coolanttemp'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['iatpreic'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['iatpostic'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['atmomap'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['oiltemp'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['afr'] =  struct.unpack('>HB',x)[0]
  x = ser.read(3)
  rawdata['voltage'] =  struct.unpack('>HB',x)[0]
  realdata['oilpressure'] = {}
  realdata['oilpressure']['value'] = ((rawdata['oilpressure']-102)*200)/612
  realdata['oilpressure']['units'] = "PSI"
  realdata['oilpressure']['name'] = "Oil Pressure"
  realdata['fuelpressure'] = {}
  realdata['fuelpressure']['value'] = ((rawdata['fuelpressure']-102)*200)/612
  realdata['fuelpressure']['units'] = "PSI"
  realdata['fuelpressure']['name'] = "Fuel Pressure"
  realdata['enginemap'] = {}
  realdata['enginemap']['value'] = round((rawdata['enginemap']*.04362)-13.6,2)
  #realdata['enginemap']['value'] = round((rawdata['enginemap']*.04362)-14.53,2)
  realdata['enginemap']['units'] = "PSI"
  realdata['enginemap']['name'] = "Boost"
  realdata['afr'] = {}
  realdata['afr']['value'] = round((rawdata['afr']*.04362)/2+4,2)
  realdata['afr']['units'] = "AFR"
  realdata['afr']['name'] = "AFR"
  realdata['coolanttemp'] = {}
  realdata['coolanttemp']['value'] = round(np.interp(rawdata['coolanttemp'],arduinomap['tempsensor'],arduinomap['temp']),2)
  realdata['coolanttemp']['units'] = "Deg C"
  realdata['coolanttemp']['name'] = "Water Temp"
  realdata['oiltemp'] = {}
  realdata['oiltemp']['value'] = round(np.interp(rawdata['oiltemp'],arduinomap['tempsensor'],arduinomap['temp']),2)
  realdata['oiltemp']['units'] = "Deg C"
  realdata['oiltemp']['name'] = "Oil Temp"
  realdata['iatpreic'] = {}
  realdata['iatpreic']['value'] = round(np.interp(rawdata['iatpreic'],arduinomap['iat'],arduinomap['temp']),2)
  realdata['iatpreic']['units'] = "Deg C"
  realdata['iatpreic']['name'] = "IAT Cold side"
  realdata['iatpostic'] = {}
  realdata['iatpostic']['value'] = round(np.interp(rawdata['iatpostic'],arduinomap['iat'],arduinomap['temp']),2)
  realdata['iatpostic']['units'] = "Deg C"
  realdata['iatpostic']['name'] = "IAT Hot side"
  #print rawdata

def texts(data, offset):
   myfont  = pygame.font.Font("gaugefont.ttf",40)
   text=myfont.render(data['name'],1,(0,0,0))
   value=myfont.render( str(data['value']), 1,(0,0,0))
   units=myfont.render(data['units'], 1,(0,0,0))
   screen.blit(text, (0, offset))
   screen.blit(value, (400, offset))
   screen.blit(units, (550, offset))

def display_data():
  offset=0
  screen.fill((255,255,255))
  for key in realdata:
    texts(realdata[key],offset)
    offset += 50
    pygame.display.update()

# Init.
screen.fill((255,255,255))
pygame.display.update()
pygame.init()
refreshtime= pygame.time.get_ticks()
pygame.time.set_timer ( pygame.POLL_GAUGES , REFRESHDELAY )
while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    if event.type == POLL_GAUGES:
      get_data()
      display_data()
