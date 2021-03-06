import struct
import time
import pygame, sys
import numpy as np
from collections import deque
from pygame.locals import *
REFRESHDELAY=1000
#screen = pygame.display.set_mode((800, 480),pygame.FULLSCREEN)
screen = pygame.display.set_mode((800, 480))
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
  format = {
    'text': self.display_text,
  }
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

  def display_text(self):
   myfont  = pygame.font.Font("gaugefont.ttf",40)
   rendername=myfont.render(self.name,1,(0,0,0))
   print('%.2f' % self.values.get_average())
   rendervalue=myfont.render(self.values.get_average().tostring(),1,(0,0,0))
   #rendervalue=myfont.render("71",1,(0,0,0))
   renderunits=myfont.render(self.units, 1,(0,0,0))
   x = self.location[0]
   y = self.location[1]
   screen.blit(rendername, (x, y))
   x += (rendername.get_size()[0] +5)
   screen.blit(rendervalue, (x, y))
   x += (rendervalue.get_size()[0] +5)
   screen.blit(renderunits, (x, y))

  def update_display(self):
    format[self.format]()

  def set_location(self,x,y):
    self.location = [x,y]


print "ytfytfty"
# Initialise sensors
sensors = dict()
sensors['oilpressure'] = Sensor("Oil Pressure","PSI","pressure")
sensors['oilpressure'].set_location(50,50)

sensors['fuelpressure'] = Sensor("Fuel Pressure","PSI","pressure")
sensors['oilpressure'].set_location(0,50)

#sensors[enginemap] = Sensor("Boost","PSI","enginemap")
#sensors[afr] = Sensor("AFR","AFR","afr",3)
#sensors[coolanttemp] = Sensor("Water Temp","Deg C","temp",4)
#sensors[oiltemp] = Sensor("Oil Temp","Deg C","temp",5)
# TBD: voltage
# reference map.

def display_gauges():
  screen.fill((255,255,255))
  for key in sensors:
    sensors[key].insert_data(500)
    sensors[key].update_display()
    print key
  pygame.display.update()

# Init.
screen.fill((255,255,255))
pygame.display.update()
pygame.init()
refreshtime= pygame.time.get_ticks()
poll_gauge_timer = pygame.USEREVENT+1
pygame.time.set_timer ( poll_gauge_timer, REFRESHDELAY )
while True:
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == poll_gauge_timer:
      #get_data()
      display_gauges()
