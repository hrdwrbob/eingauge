#!/usr/bin/python
import struct
import time
import pygame, sys
import numpy as np
from collections import deque
from pygame.locals import *
import serial

def get_serial_data():
  
  indata = ser.read(2)
  #print indata;
  unpack = struct.unpack('h',indata);
  print unpack


# Init.
ser = serial.Serial('/dev/tty.usbmodem1411',115200)
#ser.write(b'1')
time.sleep(2) # Settle the serial.
#display_gauges()

while True:
      time.sleep(1)
      ser.write(b'1')
      #print "getting data"
      get_serial_data()
      #display_gauges()


