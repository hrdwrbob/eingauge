#!/usr/bin/python
import struct
import time
import pygame, sys
import numpy as np
#import can
from collections import deque
from pygame.locals import *
import serial
can_interface = 'can0'
canenabled = True

REFRESHDELAY=500
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
        self.value = 0
        self.window = window

    def add(self, x):
        self.value = x
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
class Sensor():
  arduinomap['iat'] = [99, 125, 155, 190, 229, 272, 319, 368, 419, 470, 521, 570, 616, 660, 700, 737, 770, 800, 827, 850, 871, 889, 905, 919, 931, 942, 951, 959, 966, 972, 978 ]
  arduinomap['temp'] = [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
  arduinomap['tempsensor'] = [0, 20, 40, 80, 120, 160, 203, 239, 279, 321, 361, 409, 458, 500, 530, 558, 601, 631, 666, 701, 736, 771, 806, 841, 876, 911, 946, 981, 1016, 1051, 1086]

  def __init__(self,name,units,type,rounding):
    self.name = name
    self.units = units
    self.type = type
    self.rounding = rounding
    self.historylength = 20
    self.normalisation = 5
    self.values = SensorData(self.historylength,self.normalisation)
    self.location = [0,0]

  def insert_data(self,value):
      if self.type == "pressure":
        value = (value-102)/4.1   #(max(0,value-102)*200)/612 # Can't have negative pressure.
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



class Gauge():
  def __init__(self,sensor,location):
    self.location = location
    self.sensor = sensor

  def display_text(self,text,size,textlocation):
    myfont  = pygame.font.Font("gaugefont.ttf",size)
    rendervalue=myfont.render(text,1,(255,255,255))
    screen.blit(rendervalue, textlocation)
    return rendervalue.get_size()





class GaugeBox(Gauge):

  def render(self): 
    y = 0
    y += self.display_text(self.sensor.name,14,y)
    #y += display_text(self.values.get_average().tostring(),40,y)
    y += self.display_text("71",60,y)
    y += self.display_text(self.sensor.units,20,y)

  def display_text(self,text,size,y):
    myfont  = pygame.font.Font("gaugefont.ttf",size)
    rendervalue=myfont.render(text,1,(255,255,255))
    x = 64-(rendervalue.get_size()[0]/2)
    screen.blit(rendervalue, (x, y))
    return rendervalue.get_size()


class GaugeSmallLine(Gauge):
  def render(self):
    cursor = list(self.location)
    size = self.display_text(self.sensor.name+"  ",11,cursor)
    #y += display_text(self.values.get_average().tostring(),40,y)
    cursor[0] += 70
    #print str(self.sensor.values.get_average())
    if (self.sensor.rounding == 0):
      myvalue = int(self.sensor.values.value)
    else:
      myvalue = round(self.sensor.values.value,self.sensor.rounding)
    size = self.display_text(str(myvalue),13,cursor)
    cursor[0] += 36
    self.display_text(self.sensor.units,11,cursor)


# Initialise sensors
sensors = dict()
#sensors['fuelpressure'] = Sensor("Fuel Pressure","PSI","pressure","default")
sensors['fuelpressure'] = Sensor("Fuel Press","PSI","pressure",0)
sensors['oilpressure'] = Sensor("Oil Press     ","PSI","pressure",0)
sensors['oiltemp'] = Sensor("Oil Temp","C","temp",0)
sensors['watertemp'] = Sensor("Wat. Temp","C","direct",0)
sensors['speed'] = Sensor("Speed","km/h","direct",0)
sensors['boost'] = Sensor("Man Press","PSI","direct",1)

#sensors['oilpressure'] = Sensor("Oil Pressure","PSI","pressure","default")
gauges = []
gauges.append(GaugeSmallLine(sensors['fuelpressure'],[0,0]))
gauges.append(GaugeSmallLine(sensors['oilpressure'],[0,17]))
gauges.append(GaugeSmallLine(sensors['oiltemp'],[0,34]))
gauges.append(GaugeSmallLine(sensors['watertemp'],[0,51]))
gauges.append(GaugeSmallLine(sensors['boost'],[0,68]))

#sensors[enginemap] = Sensor("Boost","PSI","enginemap")
#sensors[afr] = Sensor("AFR","AFR","afr",3)
#sensors[coolanttemp] = Sensor("Water Temp","Deg C","temp",4)
#sensors[oiltemp] = Sensor("Oil Temp","Deg C","temp",5)
# TBD: voltage
# reference map.

def display_gauges():
  screen.fill((0,0,0))
  #screen.blit(stiImage,(0,0))
  for gauge in gauges:
    gauge.render()
  pygame.display.update()

def can_message(message):
  if (message.arbitration_id == 0x512) :
    unpack = struct.unpack('xh',m2.data)
    speed = unpack[0] * 0.05625
    sensors['speed'].insert_data(500)
  if (message.arbitration_id == 0x600) :
    unpack = struct.unpack('xxxb',m2.data)
    temperature = unpack[0] +40
    sensors['watertemp'].insert_data(temperature)
  if (message.arbitration_id == 0x420) :
    unpack = struct.unpack('hhhh',m2.data)
    sensors['fuelpressure'].insert_data(unpack[0])
    sensors['boost'].insert_data(float(unpack[1])/10.0)
    sensors['oiltemp'].insert_data(unpack[2])

def get_serial_data():
  ser.write(b'1')
  #unpack = struct.unpack('hhhhhhhh',ser.read(16));
  unpack = struct.unpack('hhhhh',ser.read(10));
  sensors['fuelpressure'].insert_data(unpack[1])
  sensors['boost'].insert_data((float(unpack[4])/10.0)-14.7)
  sensors['oiltemp'].insert_data(unpack[0])
  sensors['oilpressure'].insert_data(unpack[2])
  #print "Boost" + str(float(unpack[1])/10.0)
  # AFR
  #IAT pre 
  #IAT post.
  sensors['watertemp'].insert_data(unpack[3])

# Init.
screen.fill((0,0,0))
pygame.display.update()
pygame.init()
refreshtime= pygame.time.get_ticks()
poll_gauge_timer = pygame.USEREVENT+1
pygame.time.set_timer ( poll_gauge_timer, REFRESHDELAY )
pygame.mouse.set_visible(False)
#bus = can.interface.Bus(can_interface, bustype='socketcan_ctypes')
stiImage = pygame.image.load('stismall.png')
stiImage.set_alpha(1)
ser = serial.Serial('/dev/ttyACM0',115200)
#ser = serial.Serial('/dev/tty.usbmodem1411',115200)

#ser.write(b'1')
display_gauges()
time.sleep(4)

while True:
  #message = bus.recv(0.0)  # Timeout in seconds.
  message = None
  if message != None:
    can_message(message)

  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == poll_gauge_timer:
      #get_data()
      get_serial_data()
      display_gauges()
      #time.sleep(10)


