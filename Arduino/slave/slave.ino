// EspnowSlave.ino

// a minimal program derived from
//          https://github.com/HarringayMakerSpace/ESP-Now

// This is the program that receives the data. (The Slave)

//-----------------------Include Statements------------------------//
#include <ESP8266WiFi.h>
extern "C" {
    #include <espnow.h>
     #include <user_interface.h>
}

//-----------------------Wireless Setup-----------------------------//
uint8_t mac[] = {0x36, 0x33, 0x33, 0x33, 0x33, 0x34};


void initVariant() {
  WiFi.mode(WIFI_AP);
  wifi_set_macaddr(SOFTAP_IF, &mac[0]);
}

#define WIFI_CHANNEL 4


//-----------------------Packet Setup--------------------------------//
struct __attribute__((packed)) DataStruct {
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


void setup() {
    Serial.begin(115200); Serial.println();
    Serial.println("Starting EspnowSlave.ino");

    Serial.print("This node AP mac: "); Serial.println(WiFi.softAPmacAddress());
    Serial.print("This node STA mac: "); Serial.println(WiFi.macAddress());

    if (esp_now_init()!=0) {
        Serial.println("*** ESP_Now init failed");
        while(true) {};
    }

    esp_now_set_self_role(ESP_NOW_ROLE_SLAVE);

    esp_now_register_recv_cb(receiveCallBackFunction);


    Serial.println("End of setup - waiting for messages");
}

//============

void loop() {

}

//============

void receiveCallBackFunction(uint8_t *senderMac, uint8_t *incomingData, uint8_t len) {
    memcpy(&myData, incomingData, sizeof(myData));
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

}
