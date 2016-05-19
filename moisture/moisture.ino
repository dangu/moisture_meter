// Depends on the following Arduino libraries:
// - Adafruit Unified Sensor Library: https://github.com/adafruit/Adafruit_Sensor
// - DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN1            2         // Pin which is connected to the DHT sensor.
#define DHTPIN2            3
#define DHTPIN3            4
#define DHTPIN4            5
#define DHTPIN5            6
#define DHTPIN6            7

#define N_SENSORS   6   //!< The number of sensors used
// Uncomment the type of sensor in use:
//#define DHTTYPE           DHT11     // DHT 11 
#define DHTTYPE           DHT22     // DHT 22 (AM2302)
//#define DHTTYPE           DHT21     // DHT 21 (AM2301)


// See guide for details on sensor wiring and usage:
//   https://learn.adafruit.com/dht/overview

DHT_Unified *dht_array[N_SENSORS];

uint32_t delayMS;

void setup() {
  int i;
  Serial.begin(9600); 
  // Initialize device.
  Serial.println("DHTxx Unified Sensor Example");

  dht_array[0] = new DHT_Unified(DHTPIN1,DHTTYPE);
  dht_array[1] = new DHT_Unified(DHTPIN2,DHTTYPE);
  dht_array[2] = new DHT_Unified(DHTPIN3,DHTTYPE);
  dht_array[3] = new DHT_Unified(DHTPIN4,DHTTYPE);
  dht_array[4] = new DHT_Unified(DHTPIN5,DHTTYPE);
  dht_array[5] = new DHT_Unified(DHTPIN6,DHTTYPE);
  for(i=0;i<N_SENSORS;i++)
  {
    dht_array[i]->begin();
  }
  // Print temperature sensor details.
  sensor_t sensor;
  dht_array[0]->temperature().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Temperature");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" *C");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" *C");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" *C");  
  Serial.println("------------------------------------");
  // Print humidity sensor details.
  dht_array[0]->humidity().getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.println("Humidity");
  Serial.print  ("Sensor:       "); Serial.println(sensor.name);
  Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println("%");
  Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println("%");
  Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println("%");  
  Serial.println("------------------------------------");
  // Set delay between sensor readings based on sensor details.
  delayMS = sensor.min_delay / 1000;
}

void loop() {
  uint8_t i;
  // Delay between measurements.
  // Get temperature event and print its value.
  sensors_event_t event; 
  delay(delayMS);

  // Read all sensors
  for(i=0;i<N_SENSORS;i++)
  {
    Serial.print("Sensor ");
    Serial.println(i);
    dht_array[i]->temperature().getEvent(&event);
    if (isnan(event.temperature)) {
      Serial.println("Error reading temperature!");
    }
    else {
      Serial.print("Temperature: ");
      Serial.print(event.temperature);
      Serial.println(" *C");
    }
    // Get humidity event and print its value.
    dht_array[i]->humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
      Serial.println("Error reading humidity!");
    }
    else {
      Serial.print("Humidity: ");
      Serial.print(event.relative_humidity);
      Serial.println("%");
    }
  }
}
