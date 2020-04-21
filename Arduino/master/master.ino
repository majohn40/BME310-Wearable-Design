// Megan Johnson
// Date: 4/10/2020
// Code for Master ESP8266 to be integrated into wearable for BME 310 Final Project

//--------------------------Include Statements---------------------------/

#include <Wire.h>
//#include "MAX30105.h"
#include <ESP8266WiFi.h>
extern "C" {
    #include <espnow.h>
}

//--------------------------Wireless Communication Setup---------------------------//
// this is the MAC Address of the slave which receives the data
uint8_t remoteMac[] = {0x36, 0x33, 0x33, 0x33, 0x33, 0x34};

#define WIFI_CHANNEL 4


//--------------------------Packet Definition--------------------------------------//
// must match the slave struct
struct __attribute__((packed)) DataStruct {
    //long pulse;
    int16_t gyro_y;
};

DataStruct myData;


//--------------------------Variable Initilaization---------------------------------//
//General Variables
unsigned long lastSentMillis;
unsigned long sendIntervalMillis = 100;
unsigned long sentMicros;
unsigned long ackMicros;
 
unsigned long lastBlinkMillis;
unsigned long fastBlinkMillis = 200;
unsigned long slowBlinkMillis = 700;
unsigned long blinkIntervalMillis = slowBlinkMillis;

//MAX 30105 (PulseOx)
//MAX30105 particleSensor; 
byte ledPin = 14;

//MPU 6050 (Accelerometer)

//==============

void setup() {

//-----------------------Wireless Initiliazation--------------------------------------//
    Serial.begin(115200); Serial.println();
    Serial.println("Starting EspnowController.ino");

    WiFi.mode(WIFI_STA); // Station mode for esp-now controller
    WiFi.disconnect();

    if (esp_now_init() != 0) {
        Serial.println("*** ESP_Now init failed");
        while(true) {};
    }
    esp_now_set_self_role(ESP_NOW_ROLE_CONTROLLER);
    esp_now_add_peer(remoteMac, ESP_NOW_ROLE_SLAVE, WIFI_CHANNEL, NULL, 0);

    esp_now_register_send_cb(sendCallBackFunction);

//--------------------------MAX 30105 Initialization------------------------------------//
//  // Initialize MAX 30105 Sensor
//  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
//  {
//     Serial.println("MAX30105 was not found. Please check wiring/power. ");
//     while (1);
//  }
//
//  //Setup to sense a nice looking saw tooth on the plotter
//   byte ledBrightness = 0xF0; //Options: 0=Off to 255=50mA
//   byte sampleAverage = 8; //Options: 1, 2, 4, 8, 16, 32
//   byte ledMode = 2; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
//   int sampleRate = 1000; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
//   int pulseWidth = 411; //Options: 69, 118, 215, 411
//   int adcRange = 16384; //Options: 2048, 4096, 8192, 16384
//
//   particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings

//-------------------------MPU 6050 Initialization--------------------------------------//
    MPU6050setup();

}


//==============

void loop() {
  sendData();
//    if (particleSensor.getIR() < 8000) {
//        //Serial.println("SLeeping");
//        ESP.deepSleep(1e6);
//
//    }
//    else{
//        //Serial.println("Waking up");
//        sendData();
//        //Serial.println(particleSensor.getIR()); //Send raw data to plotter
//    }
}

//==============

void sendData() {
    if (millis() - lastSentMillis >= sendIntervalMillis) {
        lastSentMillis += sendIntervalMillis;
        
//---------Add pulseox data to packet--------------------------//
//        long TempIr = particleSensor.getIR();
//        if ((TempIr < 1e9) && (TempIr > -1e9)){
//            myData.Pulse = TempIr;
//        } 

//---------Add accelerometer data to packet--------------------//
        myData.gyro_y = MPU6050getData();

//---------Compress Packet and Send----------------------------//
        uint8_t bs[sizeof(myData)];
        memcpy(bs, &myData, sizeof(myData));
        sentMicros = micros();
        esp_now_send(NULL, bs, sizeof(myData)); // NULL means send to all peers
        //Serial.println(myData.gyro_y);
        //Serial.println("sent data");

    }
}

//==============

void sendCallBackFunction(uint8_t* mac, uint8_t sendStatus) {
    ackMicros = micros();
    Serial.println();
    if (sendStatus == 0) {
        blinkIntervalMillis = fastBlinkMillis;
    }
    else {
        blinkIntervalMillis = slowBlinkMillis;
    }
}

//================