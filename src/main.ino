#include <SimpleTimer.h>
#include "ds18b20obj.cpp"


#define TEMP1_PIN       D5
#define TEMP2_PIN       D6
#define TEMP3_PIN       D7
#define TEMP4_PIN       D3


DS18B20 temp1;
DS18B20 temp2;
DS18B20 temp3;
DS18B20 temp4;


int temp_read_delay = 900;
uint8_t temp_resolution = 12;


void print_temp(uint8_t sens_id, float temp_c){
  uint16_t itemp = (temp_c * 100);
  uint8_t temp[2] = { itemp & 0xff, itemp >> 8 };
  Serial.print(sens_id, DEC);
  Serial.print("=");
  Serial.println(temp_c);
}


void setup() {
  Serial.begin(115200);
  temp1.init(TEMP1_PIN, temp_resolution);
  temp2.init(TEMP2_PIN, temp_resolution);
  temp3.init(TEMP3_PIN, temp_resolution);
  temp4.init(TEMP4_PIN, temp_resolution);

  temp1.on_temp([](float t_new){
    temp1.read();
    print_temp(1, t_new);
  });

  temp2.on_temp([](float t_new){
    temp2.read();
    print_temp(2, t_new);
  });

  temp3.on_temp([](float t_new){
    temp3.read();
    print_temp(3, t_new);
  });

  temp4.on_temp([](float t_new){
    temp4.read();
    print_temp(4, t_new);
  });

  temp1.read();
  temp2.read();
  temp3.read();
  temp4.read();
}



void loop() {
  temp1.run();
  temp2.run();
  temp3.run();
  temp4.run();
}
