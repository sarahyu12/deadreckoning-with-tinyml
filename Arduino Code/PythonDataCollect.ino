// Reads data from an accelerometer and GPS  
// ©2023 The Johns Hopkins University Applied Physics Laboratory LLC

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "SD.h"
#include "SPI.h"
#include "FS.h"
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_LIS3DH.h>
#include <Adafruit_Sensor.h>
#include <TinyGPSPlus.h>
#include <HardwareSerial.h>


#define RXD 34
#define TXD -1
Adafruit_MPU6050 mpu;
TinyGPSPlus gps;
HardwareSerial SerialGPS(1);

void setup(void) {
  Serial.begin(115200);
	SerialGPS.begin(9600, SERIAL_8N1, RXD, TXD);
  while (!Serial && !SerialGPS)
    delay(10);  // will pause Zero, Leonardo, etc until serial console opens
  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  bool establishedConnection = false;
  int c = 0;
      // while(!establishedConnection){
      //   if(SerialGPS.available() > 0){
      //     if(gps.encode(SerialGPS.read())){
      //       if(gps.location.lat() != 0){
      //         establishedConnection = true;
      //       }
      //     }
      //   }
      //   Serial.println(c);
      //   c++;
      // }
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void loop() {

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Print out the values */
  Serial.print(a.acceleration.x);
  Serial.print(",");
  Serial.print(a.acceleration.y);
  Serial.print(",");
  Serial.print(a.acceleration.z);
  Serial.print(",");
  Serial.print(g.gyro.x);
  Serial.print(",");
  Serial.print(g.gyro.y);
  Serial.print(",");
  Serial.print(g.gyro.z);

  if(SerialGPS.available() > 0){
    if(gps.encode(SerialGPS.read())){
    Serial.print(",");
    Serial.print(gps.location.lat(), 6);
    Serial.print(",");
    Serial.print(gps.location.lng(), 6);
    } else {
    Serial.print(",,");
    }
  }

  Serial.println();
  Serial.flush();
  delay(50);
}
