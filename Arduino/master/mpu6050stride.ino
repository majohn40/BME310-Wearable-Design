
#include "Wire.h"
const int MPU_ADDR = 0x68; 
char tmp_str[7]; 
int16_t accelerometer_x, accelerometer_y, accelerometer_z; // variables for accelerometer raw data
int16_t gyro_x, gyro_y, gyro_z; // variables for gyro raw data
int16_t temperature;


void MPU6050setup() {
  Serial.begin(115200);
	Wire.begin();
	Wire.beginTransmission(MPU_ADDR);
	Wire.write(0x6B);
	Wire.write(0);
	Wire.endTransmission(true);
}

char* convert_int16_to_str(int16_t i) {
  sprintf(tmp_str, "%6d", i);
  return tmp_str;
}


int getStepCount(int* paceflag, int* stepcount){
  if (*paceflag == 0){
    if (gyro_y > 2000){
      stepcount = stepcount +1;
      *paceflag = 1;
    }
  }
  else if (*paceflag == 1){  
    if (gyro_y < 0){
      *paceflag = 0;
    }
  }
  return *stepcount;
}

int16_t MPU6050getData(){
  //------Setup transmission--------//
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H) [MPU-6000 and MPU-6050 Register Map and Descriptions Revision 4.2, p.40]
  Wire.endTransmission(false); // the parameter indicates that the Arduino will send a restart. As a result, the connection is kept active.
  Wire.requestFrom(MPU_ADDR, 7*2, true); // request a total of 7*2=14 registers

  //------Setup Variables----------//
  int16_t accelerometer_x, accelerometer_y, accelerometer_z; 
  int16_t gyro_x, gyro_y, gyro_z; 
  int16_t temperature;

  //------Read Sensor Data--------//
  accelerometer_x = Wire.read()<<8 | Wire.read(); // reading registers: 0x3B (ACCEL_XOUT_H) and 0x3C (ACCEL_XOUT_L)
  accelerometer_y = Wire.read()<<8 | Wire.read(); // reading registers: 0x3D (ACCEL_YOUT_H) and 0x3E (ACCEL_YOUT_L)
  accelerometer_z = Wire.read()<<8 | Wire.read(); // reading registers: 0x3F (ACCEL_ZOUT_H) and 0x40 (ACCEL_ZOUT_L)
  temperature = Wire.read()<<8 | Wire.read(); // reading registers: 0x41 (TEMP_OUT_H) and 0x42 (TEMP_OUT_L)
  gyro_x = Wire.read()<<8 | Wire.read(); // reading registers: 0x43 (GYRO_XOUT_H) and 0x44 (GYRO_XOUT_L)
  gyro_y = Wire.read()<<8 | Wire.read(); // reading registers: 0x45 (GYRO_YOUT_H) and 0x46 (GYRO_YOUT_L)
  gyro_z = Wire.read()<<8 | Wire.read(); // reading registers: 0x47 (GYRO_ZOUT_H) and 0x48 (GYRO_ZOUT_L)
  return gyro_y;
}
