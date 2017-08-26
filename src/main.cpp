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
uint8_t current_temp[4][2];
uint8_t serial_curr_pos = 0;
uint8_t serial_msg[4];


void store_temp(uint8_t sens_id, float temp_c){
  uint16_t itemp = (temp_c * 100);
  uint8_t temp[2] = { itemp & 0xff, itemp >> 8 };
  current_temp[sens_id][0] = temp[0];
  current_temp[sens_id][1] = temp[1];
  Serial.write((int)sens_id);
  Serial.write(temp, 2);
}


void setup() {
  Serial.begin(115200);
  temp1.init(TEMP1_PIN, temp_resolution);
  temp2.init(TEMP2_PIN, temp_resolution);
  temp3.init(TEMP3_PIN, temp_resolution);
  temp4.init(TEMP4_PIN, temp_resolution);

  temp1.on_temp([](float t_new){
    temp1.read();
    store_temp(1, t_new);
  });

  temp2.on_temp([](float t_new){
    temp2.read();
    store_temp(2, t_new);
  });

  temp3.on_temp([](float t_new){
    temp3.read();
    store_temp(3, t_new);
  });

  temp4.on_temp([](float t_new){
    temp4.read();
    store_temp(4, t_new);
  });

  temp1.read();
  temp2.read();
  temp3.read();
  temp4.read();
}


void parse_serial(){
  uint8_t cmd = serial_msg[0];
  uint8_t sensor = serial_msg[1];
  uint8_t data = serial_msg[2];

  // change resolution
  if ( cmd == 1 ){

    if (data>12){
      data = 12;
    }
    if (data<9){
      data = 9;
    }

    if (sensor == 1){
      temp1.set_resolution(data);
    }
    if (sensor == 2){
      temp2.set_resolution(data);
    }
    if (sensor == 3){
      temp3.set_resolution(data);
    }
    if (sensor == 4){
      temp4.set_resolution(data);
    }
    
    return;
  }

}



void read_serial(){
  serial_msg[serial_curr_pos] = Serial.read();
  serial_curr_pos++;
  if (serial_curr_pos>2){
    serial_curr_pos = 0;
    parse_serial();
  }
}


void loop() {
  if (Serial.available() > 0) {
    read_serial();
  }
  temp1.run();
  temp2.run();
  temp3.run();
  temp4.run();
}
