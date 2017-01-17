import serial
import struct
import time
import numpy as np
rawdata = dict()
realdata = dict()
ser = serial.Serial('/dev/ttyACM0')
arduinomap = dict()
arduinomap['iat'] = [99, 125, 155, 190, 229, 272, 319, 368, 419, 470, 521, 570, 616, 660, 700, 737, 770, 800, 827, 850, 871, 889, 905, 919, 931, 942, 951, 959, 966, 972, 978 ]
arduinomap['temp'] = [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
arduinomap['tempsensor'] = [0, 20, 40, 80, 120, 160, 203, 239, 279, 321, 361, 409, 458, 500, 530, 558, 601, 631, 666, 701, 736, 771, 806, 841, 876, 911, 946, 981, 1016, 1051, 1086]
ser.write(b'1')
time.sleep(1)
while 1:
  ser.write(b'1')
  time.sleep(1)
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
  realdata['enginemap']['value'] = (rawdata['enginemap']*.04362)-14.53
  realdata['enginemap']['units'] = "PSI"
  realdata['enginemap']['name'] = "Boost"
  realdata['afr'] = {}
  realdata['afr']['value'] = (rawdata['afr']*.04362)/2+9
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
  realdata['iatpreic']['value'] = rawdata['iatpreic']
  realdata['iatpreic']['units'] = "Deg C"
  realdata['iatpreic']['name'] = "IAT Hot side"
  realdata['iatpostic'] = {}
  realdata['iatpostic']['value'] = round(np.interp(rawdata['iatpostic'],arduinomap['iat'],arduinomap['temp']),2)
  realdata['iatpostic']['units'] = "Deg C"
  realdata['iatpostic']['name'] = "IAT Cold side"
  #print rawdata
  for key in realdata:
    print realdata[key]['name'] + ":" +  str(realdata[key]['value']) + " " + realdata[key]['units'],
  print
  
