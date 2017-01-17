#include "SwitecX25.h"


int enginemap = 0;    // first analog sensor
int atmmap = 0;   // second analog sensor
int rpm = 0;    // digital sensor
int roadspeed = 0;         // incoming serial byte
int inByte;

SwitecX25 motor1(225*3, 5,4,3,2); // Boost gauge.
SwitecX25 motor2(225*3, 6,7,8,9); // Tacho.
SwitecX25 motor3(225*3, 10,11,12,13); // Speedo.


void setup() {
  // start serial port at 9600 bps:
  Serial.begin(9600);
 // while (!Serial) {

 //   ; // wait for serial port to connect. Needed for native USB port only
 // }

  //pinMode(2, INPUT);   // digital sensor is on digital pin 2
//  establishContact();  // send a byte to establish contact until receiver responds
   delay(1000);
   motor1.zero(); // Zero the boost gauge.
   delay(1000);
   motor1.setPosition(660);
  motor1.updateBlocking();
   motor1.setPosition(200);
  motor1.updateBlocking();
   delay(1000);
   motor1.zero(); // Zero the boost gauge.
}

void loop() {
  // Read the sensors we need for gauges.
    analogRead(0); // Switch the MUX and settle.
    enginemap = analogRead(0);  // Manifold Presssure
    // MAP sensor http://www.robietherobot.com/storm/mapsensor.htm
    // (V*8.94)-14.53 / 1024
    // (analog*.04362)-14.53 = PSI.
    // Gauge reads up to 40psi absolute pressure.
    // 675/40 = 16.875 steps per psi
    // step = ((analog*.04362)-14.53)*16.875
    // ((a*.04362)-14.53)*16.875 evaluates to 0.736088a-245.194
    motor1.setPosition((((float)enginemap*.04362)-14.53)*16.8); // Set the boost gauge.
    //motor1.setPosition(enginemap); // Set the boost gauge.
    analogRead(1); // Switch the MUX and settle.
    //atmmap = analogRead(1);  // ATmo pressure
    // correct for atmospheric pressure - tba.
   
    // Need to read digital input here for RPM and Speed.

    // Need to write gauge sweeper code and trigger on ignition voltage.    
    
    
    // Move the steppers.
    motor1.update();
    
  // if we get a valid byte, read analog ins:
  if (Serial.available() > 0) {
    // get incoming byte:
    inByte = Serial.read(); // Accept whatever, then give all the values in order.
   
    //enginemap = 300;
    SendInt(enginemap); // we already read this.
    analogRead(1); // Switch the MUX and settle.
    SendInt(analogRead(1)); // Oil pressure
    analogRead(2); // Switch the MUX and settle.
    SendInt(analogRead(2)); // Fuel pressure
    analogRead(3); // Switch the MUX and settle.
    SendInt(analogRead(3)); // Coolant Temp
    analogRead(4); // Switch the MUX and settle.
    SendInt(analogRead(4)); // IAT preIC
    analogRead(5); // Switch the MUX and settle.
    SendInt(analogRead(5)); // IAT PostIC
    analogRead(6); // Switch the MUX and settle.
    SendInt(analogRead(6)); // Atmospheric pressure
    analogRead(7); // Switch the MUX and settle.
    SendInt(analogRead(7)); // Oil Temp
    analogRead(8); // Switch the MUX and settle.
    SendInt(analogRead(8)); // AFR
    analogRead(9); // Switch the MUX and settle.
    SendInt(analogRead(9)); // Voltage
    
    //thirdSensor = map(digitalRead(2), 0, 1, 0, 255);
    
  }
}
void SendInt(int s) {
    Serial.write((byte) (s / 256));
    Serial.write((byte) s % 256);
    Serial.write((byte) 100);
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}
