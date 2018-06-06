import struct
import time
import pygame, sys
import numpy as np
import can
from collections import deque
from pygame.locals import *
import can

can_interface = 'can0'
canenabled = True

REFRESHDELAY=1000
#screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
screen = pygame.display.set_mode((128, 96),pygame.FULLSCREEN)
pygame.font.init()
rawdata = dict()
realdata = dict()
arduinomap = dict()


class SensorData():
    "A 1D ring buffer using numpy arrays"
    def __init__(self, length,window):
        self.data = np.zeros(length, dtype='f')
        self.index = 0
        self.window = window

    def add(self, x):
        "add x to ring buffer"
        self.index = (++self.index) % (self.data.size-1)
        self.data[self.index] = x

    def get(self):
        "Returns the first-in-first-out data in the ring buffer"
        # Has to be like this incase we're at the end.
        return self.data[self.index]

    def get(self,x):
        "Returns the xth previous data in the ring buffer"
        idx = (self.index - x)
        return self.data[idx]

    def weighted_average(self,window):
        "Returns the weighted average value - newest is weighted highest."
        total = 0
        totalcount = 0
        for x in range(0, window):
            weighting = (window-x)^2;
            total = total + self.get(x)*weighting
            totalcount = totalcount + weighting
        return total/totalcount

    def get_average(self):
       return self.weighted_average(self.window)

# Sensor - data is updated in the sensor when it's read from the interface.
class Sensor:
  arduinomap['iat'] = [99, 125, 155, 190, 229, 272, 319, 368, 419, 470, 521, 570, 616, 660, 700, 737, 770, 800, 827, 850, 871, 889, 905, 919, 931, 942, 951, 959, 966, 972, 978 ]
  arduinomap['temp'] = [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
  arduinomap['tempsensor'] = [0, 20, 40, 80, 120, 160, 203, 239, 279, 321, 361, 409, 458, 500, 530, 558, 601, 631, 666, 701, 736, 771, 806, 841, 876, 911, 946, 981, 1016, 1051, 1086]

  def __init__(self,name,units,type,format):
    self.name = name
    self.units = units
    self.type = type
    self.format = format
    self.historylength = 20
    self.normalisation = 5
    self.values = SensorData(self.historylength,self.normalisation)
    self.location = [0,0]

  def insert_data(self,value):
      if self.type == "pressure":
        #value = (max(0,value-102)*200)/612 # Can't have negative pressure.
        value = value
      elif self.type == "iat":
        value = round(np.interp(value,arduinomap['iat'],arduinomap['temp']),2)
      elif self.type == "temp":
        value = round(np.interp(value,arduinomap['tempsensor'],arduinomap['temp']),2)
      elif self.type == "airpressure":
        value = round((value*.04362)-13.6,2)
          #realdata['enginemap']['value'] = round((rawdata['enginemap']*.04362)-14.53,2)
      elif self.type == 'afr':
        value = round((value*.04362)/2+4,2)
      self.values.add(value)

  def display_text(self,text,size,y):
    myfont  = pygame.font.Font("gaugefont.ttf",size)
    rendervalue=myfont.render(text,1,(255,255,255))
    x = 64-(rendervalue.get_size()[0]/2)
    screen.blit(rendervalue, (x, y))
    return rendervalue.get_size()[1]

  def update_display(self):
    y = 0
    y += self.display_text(self.name,14,y)
    #y += display_text(self.values.get_average().tostring(),40,y)
    y += self.display_text("71",60,y)
    y += self.display_text(self.units,20,y)

  def set_location(self,x,y):
    self.location = [x,y]


print "ytfytfty"
# Initialise sensors
sensors = dict()
#sensors['fuelpressure'] = Sensor("Fuel Pressure","PSI","pressure","default")
sensors['fuelpressure'] = Sensor("Fuel Pressure","LIBERTY","pressure","default")

sensors['fuelpressure'].set_location(0,0)

#sensors[enginemap] = Sensor("Boost","PSI","enginemap")
#sensors[afr] = Sensor("AFR","AFR","afr",3)
#sensors[coolanttemp] = Sensor("Water Temp","Deg C","temp",4)
#sensors[oiltemp] = Sensor("Oil Temp","Deg C","temp",5)
# TBD: voltage
# reference map.

def display_gauges():
  screen.fill((0,0,0))
  for key in sensors:
    sensors[key].update_display()
    print key
  screen.blit(stiImage,(0,0))
  pygame.display.update()

def can_message(message):
  if (message.arbitration_id == 0x512) :
    speedcount = struct.unpack('xh',m2.data)
    speed = speedcount * 0.05625
    sensors['speed'].insert_data(500)

# Init.
screen.fill((0,0,0))
pygame.display.update()
pygame.init()
refreshtime= pygame.time.get_ticks()
poll_gauge_timer = pygame.USEREVENT+1
pygame.time.set_timer ( poll_gauge_timer, REFRESHDELAY )
pygame.mouse.set_visible(False)
bus = can.interface.Bus(can_interface, bustype='socketcan_ctypes')
stiImage = pygame.image.load('stismall.png')

while True:
  message = bus.recv(0.0)  # Timeout in seconds.
  if message != None:
    can_message(message)

  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == poll_gauge_timer:
      #get_data()
      display_gauges()

