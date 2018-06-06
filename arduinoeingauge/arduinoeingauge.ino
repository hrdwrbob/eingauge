#include "SwitecX25.h"

#include <mcp_can.h>
#include <SPI.h>
#include <Adafruit_MAX31855.h>

// Vars for the steppers
static unsigned short myAccelTable[][2] = {
  {   20, 4500},
  {   50, 2000},
  {  100, 1400},
  {  150, 1200},
  {  300, 800}
};

// Values 
int enginemap = 0;    // first analog sensor
int atmmap = 0;   // second analog sensor
int inByte;
double speed = 0;
uint16_t rpm;
double psi;
unsigned long GaugePreviousMillis = 0;
unsigned long dataPreviousMillis = 0;
unsigned long statusPreviousMillis = 0;
int ign = 0;
int lights = 0;
int gaugesweep = 1;

// Settings
const int GaugeUpdateInterval = 100;  // 100 milliseconds speedo update rate
const int PiTimeout = 300; // seconds
const int dataUpdateInterval = 100;
const int statusUpdateInterval = 500;


// board pins.
// #define CAN_INT // Not Used.
#define CAN_CS 26
#define THERMOCOUPLE_CS 22
// pins.
const int relayPower = 31;
const int relayScreen = 35;
const int relayPi = 33;


const int lightPin = 51;
const int ignPin = 53;


//  interrupt pins Mega, Mega2560, MegaADK  2, 3, 18, 19, 20, 21

SwitecX25 motor1(230 * 3, 2, 3, 4, 5); // Boost gauge.
SwitecX25 motor2(220 * 3, 6, 7, 8, 9); // Tacho.
SwitecX25 motor3(270 * 3, 10, 11, 12, 13); // Speedo.

Adafruit_MAX31855 thermocouple(THERMOCOUPLE_CS);
MCP_CAN CAN0(CAN_CS);   

void setup() {
  // start serial port
  //Serial.begin(115200);
  //while (!Serial) {
  //  ; // wait for serial port to connect. Needed for native USB port only
  //}
  //set pinmodes
  pinMode(lightPin, INPUT);
  pinMode(ignPin, INPUT);

  pinMode(relayPower, OUTPUT);
  pinMode(relayScreen, OUTPUT);
  pinMode(relayPi, OUTPUT);
  // "turn" ourself on
  digitalWrite(relayPower, HIGH);
  // Se
  CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ);
  CAN0.setMode(MCP_NORMAL);
  CAN0.init_Mask(0,0,0x05120000);
  CAN0.init_Filt(0,0,0x05120000);
  
  motor1.accelTable = myAccelTable;
  motor2.accelTable = myAccelTable;
  motor3.accelTable = myAccelTable;
  motor1.zero(); // Zero the boost gauge.
  motor2.zero();
  motor3.zero();
  //startGaugeSweep();
     Serial.print("Internal Temp = ");
   Serial.println(thermocouple.readInternal());

}

void loop() {
  unsigned long currentMillis = millis();

  int gaugeupdate = 0;

  if (currentMillis - GaugePreviousMillis >= GaugeUpdateInterval) {
    GaugePreviousMillis = currentMillis;
    gaugeupdate = 1;
  } 
  
  if (currentMillis - dataPreviousMillis > dataUpdateInterval)  {
    dataPreviousMillis = currentMillis;
    can_data_send();
  }

  if (currentMillis - statusPreviousMillis > statusUpdateInterval)  {
    statusPreviousMillis = currentMillis;
    can_status_send();
  }
  

  // Get CAN messages
  if (CAN0.checkReceive() == CAN_MSGAVAIL) {
    long unsigned int rxId;
    unsigned char len = 0;
    unsigned char rxBuf[8];
    CAN0.readMsgBuf(&rxId, &len, rxBuf);
    if (rxId == 0x410) {
      rpm = word(rxBuf[6],rxBuf[5]);
    }    
    if (rxId == 0x512) {
      uint16_t speedcount = word(rxBuf[3],rxBuf[2]);
      //645.2
      speed = speedcount * 0.05625; // 645.2
    }
  }
  double realspeed = speed;
 psi = get_boost();
 //  Make fuel pressure go to speedo 
 /*
  double fp = analogRead(A2);
  fp = fp - 102; // 0 psi = .5V
  speed = fp *.24; // 0.24 per psi 
  double rawfp = speed;
  */
  
  //speed = speed - (psi-14.7);
  
    // Check things that don't need to be checked every cycle
  //if (gaugeupdate) {
    //check_state();
    //    Serial.print("RPM:");
   // Serial.print(rpm);
   //  Serial.print(",");
   // Serial.print(realspeed);
   // Serial.print(",");
    //Serial.print(rawfp);
   // Serial.print(",");
  //  Serial.println(psi-14.7);
  //}

  // Set the gauge positions.
  if (finishedGaugeSweep()  && gaugeupdate)  {
    //psi = get_boost();

    // Boost Gauge - static scale (-1 to account for base needle position.)
    motor1.setPosition((psi-1.5) * 16.875 );
    //speed = 50;
    // Tacho - staggered scale.
    if (rpm < 1000) {
      motor2.setPosition(((double)rpm / 100.0) * 5.1);
    } else {
      motor2.setPosition(51 + ((double)(rpm - 1000) / 100.0 * 6.75));
    }
    
    
    // Speedo - staggered scale.
    if (speed < 20) {
      motor3.setPosition((speed / 20) * 40);
    } else {
      motor3.setPosition(40 + ((speed-20) / 10 * 27));
    }
    


  }


  // Move the steppers every cycle.
  motor1.update();
  motor2.update();
  motor3.update();

  // if we get a byte, return the relevant data.
  if (0)  { //Serial.available() > 0) {
    // get incoming byte:
    inByte = Serial.read(); 
    switch (inByte) {
      case 'c':
        analogRead(A3); // Switch the MUX and settle.
        serial_write_int(analogRead(A3)); // Coolant Temp
        break;
      case 'f':
        analogRead(A6); // Switch the MUX and settle.
        serial_write_int(analogRead(A6)); // Atmospheric pressure
        break;
      case 'i':
        analogRead(A9); // Switch the MUX and settle.
        serial_write_int(analogRead(A9)); // Voltage
        break;
      case 'l':
        serial_write_int(lights); // RPM
        break;
      case 'm':
        serial_write_int(ign); // RPM
        break;
    }
  }
}

void can_status_send() {
  int fuel_pressure = analogRead(A2);
  int intake_pressure = (int)(psi*10.0);
  int oil_temp = analogRead(A7);
  int afr = analogRead(A8);
  int iat_preic = analogRead(A4);
  int iat_postic = analogRead(A5);
  byte data[8] = {
    lowByte(fuel_pressure),
    highByte(fuel_pressure),
    lowByte(intake_pressure),
    highByte(intake_pressure),
    lowByte(oil_temp),
    highByte(oil_temp),  
    lowByte(afr),
    highByte(afr)
    };
  

  CAN0.sendMsgBuf(0x420, 0, 8, data);

  byte data2[4] = {
    lowByte(iat_preic),
    highByte(iat_preic),
    lowByte(iat_postic),
    highByte(iat_postic), 
    };
  CAN0.sendMsgBuf(0x421, 0, 4, data2);
}

void can_data_send() {
  byte data[8] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07};

  // send data:  ID = 0x100, Standard CAN Frame, Data length = 8 bytes, 'data' = array of data bytes to send
  //CAN0.sendMsgBuf(0x100, 0, 8, data);

}

void serial_write_int(uint16_t myint) {
  Serial.write(lowByte(myint));
  Serial.write(highByte(myint));
}

void check_state() {
  int oldign = ign;
  ign =  digitalRead(ignPin);
  if (oldign != ign) {
    ignChange();
  }

  int oldlights = lights;
  lights =  digitalRead(lightPin);
  if (oldlights != lights) {
    lightsChange();
  }

}
double get_boost() {
    analogRead(A0); // Switch the MUX and settle.
    enginemap = analogRead(A0);  // Manifold Presssure
    return ((double)enginemap * 0.04362) + 0.6; // Absolute PSI
}

void startGaugeSweep() {
  motor1.setPosition(2000);
  motor2.setPosition(2000);
  motor3.setPosition(2000);
  gaugesweep = 1;
}

int finishedGaugeSweep() {
  if (motor1.currentStep == motor1.targetStep &&
      motor2.currentStep == motor2.targetStep &&
      motor3.currentStep == motor3.targetStep &&
      gaugesweep == 1) {
    motor1.setPosition(0);
    motor2.setPosition(0);
    motor3.setPosition(0);
    gaugesweep = 2;
    return 0;
  } else if (motor1.currentStep == motor1.targetStep &&
             motor2.currentStep == motor2.targetStep &&
             motor3.currentStep == motor3.targetStep &&
             gaugesweep == 2) {
    gaugesweep = 0;
    return 0;
  } else if (gaugesweep == 0) {
    return 1;
  }
  return 0;
}


void ignChange () {
  if (ign) {
    startGaugeSweep();
    digitalWrite(relayScreen, HIGH);
    digitalWrite(relayPi, HIGH);
  }
}

void lightsChange () {
  if (lights) {
    ;
  }
}

