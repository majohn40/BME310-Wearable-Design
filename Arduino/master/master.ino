// Megan Johnson
// Date: 4/10/2020
// Code for Master ESP8266 to be integrated into wearable for BME 310 Final Project

//--------------------------Include Statements---------------------------/

#include <SPI.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartrate.h"
#include <ESP8266WiFi.h>
#include <SparkFunHTU21D.h>
#include "Adafruit_TCS34725.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>


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
    long Pulse;
    float temp_ambient;
    float humidity;
    float red, green, blue;
    int stepcount;
    int bodytemp_ADC;
    float heartrate;
    int uv_ADC;
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

//-----------------MAX 30105 (PulseOx)---------------------------------------------//
MAX30105 particleSensor; 
byte ledPin = 14;
long lastBeat = 0;
float beatsPerMinute;

//-----------------HTU21D Temp and Humidity Sensor---------------------------------//
HTU21D humiditySensor;

//-----------------TCS34725 Color Sensor-------------------------------------------//
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

//-----------------OLED Display----------------------------------------------------//
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//----------------Accelerometer----------------------------------------------------//
int paceflag = 0;
int stepcount = 0;

//==============

void setup() {
     
    Serial.begin(115200);

//-----------------------Wireless Initiliazation--------------------------------------//
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
  // Initialize MAX 30105 Sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
     Serial.println("MAX30105 was not found. Please check wiring/power. ");
     while (1);
  }

  //Setup to sense a nice looking saw tooth on the plotter
   byte ledBrightness = 0xF0; //Options: 0=Off to 255=50mA
   byte sampleAverage = 8; //Options: 1, 2, 4, 8, 16, 32
   byte ledMode = 2; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
   int sampleRate = 1000; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
   int pulseWidth = 411; //Options: 69, 118, 215, 411
   int adcRange = 16384; //Options: 2048, 4096, 8192, 16384

   particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings

//-------------------------MPU 6050 Initialization--------------------------------------//
    MPU6050setup();

//-------------------------HTU21D Initiallization---------------------------------------//
    humiditySensor.begin();

//-------------------------TCS34725 Initialization (Color Sensor)-----------------------//
    tcs.begin();

//-------------------------OLED Initialization------------------------------------------//
    display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    welcomescroll();
  
}


//==============

void loop() {
  sendData();
//     if (particleSensor.getIR() < 8000) {
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
    long irValue = particleSensor.getIR();
    Serial.println(irValue);
    
    if (checkForBeat(irValue) == true)
    {
      //We sensed a beat!
      long delta = millis() - lastBeat;
      lastBeat = millis();
  
      beatsPerMinute = 60 / (delta / 1000.0);
    }

    if (millis() - lastSentMillis >= sendIntervalMillis) {
        lastSentMillis += sendIntervalMillis;
        
//---------Add pulseox data to packet--------------------------//
        long TempIr = irValue;
        if ((TempIr < 1e9) && (TempIr > -1e9)){
            myData.Pulse = TempIr;
        }
        myData.heartrate = beatsPerMinute;

//---------Add accelerometer data to packet--------------------//
        myData.gyro_y = MPU6050getData();
        stepcount = int(getStepCount(&paceflag, stepcount));
        myData.stepcount = stepcount;


//---------Add temp and humidity data to packet ---------------// 
        myData.temp_ambient = humiditySensor.readTemperature();
        myData.humidity = humiditySensor.readHumidity();

//---------Add color data to packet----------------------------//
        float red, green, blue;
        tcs.getRGB(&red, &green, &blue);
        myData.red = red;
        myData.green = green;
        myData.blue = blue;

//--------Add Body Temp Data to Packet-------------------------//
        digitalWrite(9, HIGH);
        myData.bodytemp_ADC = analogRead(A0);
        digitalWrite(9, LOW);

//--------Add UV Data to packet--------------------------------//
        digitalWrite(10, HIGH);
        myData.uv_ADC = analogRead(A0);
        digitalWrite(10, LOW);

//---------Compress Packet and Send----------------------------//
        uint8_t bs[sizeof(myData)];
        memcpy(bs, &myData, sizeof(myData));
        sentMicros = micros();
        esp_now_send(NULL, bs, sizeof(myData)); // NULL means send to all peers

//---------Update Screen---------------------------------------//
        float temp_farenheit =  (1.8*myData.temp_ambient) + 32;
        float heat_index = calculate_heat_index(myData.humidity, temp_farenheit);
        update_screen(myData.stepcount, temp_farenheit, heat_index, myData.bodytemp_ADC);

//--------Debugging Statements--------------------------------//
        Serial.print(myData.gyro_y);Serial.print("\t");
        Serial.print(myData.Pulse);Serial.print("\t");
        Serial.print(myData.temp_ambient);Serial.print("\t");
        Serial.print(myData.humidity); Serial.print("\t"); 
        Serial.print(int(myData.red)); Serial.print("\t"); 
        Serial.print(int(myData.green)); Serial.print("\t"); 
        Serial.print(int(myData.blue));Serial.print("\t");
        Serial.print(myData.stepcount);Serial.print("\t");
        Serial.print(myData.bodytemp_ADC);Serial.print("\t");
        Serial.print(myData.heartrate);Serial.print("\t");
        Serial.print(myData.uv_ADC);Serial.print("\n");

        //Serial.println("sent data");
    }
}

//==============

void sendCallBackFunction(uint8_t* mac, uint8_t sendStatus) {
    ackMicros = micros();
    if (sendStatus == 0) {
        blinkIntervalMillis = fastBlinkMillis;
    }
    else {
        blinkIntervalMillis = slowBlinkMillis;
    }
}

//================

//---------------------OLED Control Functions--------------------------------------//
void welcomescroll(void) {
  display.clearDisplay();

  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 0);
  display.println("Welcome");
  display.display();      // Show initial text
  delay(1000);

}
void update_screen(int stepcount, float temperature, float heat_index, int bodytemp_ADC){
  display.clearDisplay();
  display.setTextSize(1); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10,0);
  display.print("Step Count: "+String(stepcount));
  display.setCursor(10,8);
  display.print("Temperature: " + String(temperature));
  display.setCursor(10,16);
  display.print("Heat Index: " + String(heat_index));
  String warning = report_risk(heat_index, bodytemp_ADC);
  display.setCursor(10,24);
  display.print(warning);
  display.display();      // Show initial text
}

float calculate_heat_index(float RH, float T){
  float heat_index = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH;
  return heat_index;
}
String report_risk(float heat_index, int bodytemp_ADC){
  String warning_message;
  float body_temp = 15*bodytemp_ADC/1023 + 92.048;
  if (heat_index > 130){
    warning_message = "HS very likely!";
  } else if (heat_index > 105){
    warning_message = "HE, HS risk";
  } else if (heat_index > 90){
    warning_message = "Low Risk HE";
  }else if (body_temp >104) {
    warning_message = "STOP! Overheating!";
  }else{
    warning_message = "Safe to Exercise";
  }
  return warning_message;
}



  
