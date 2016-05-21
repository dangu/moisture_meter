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

/**@brief Creating a class for the group of sensors */
class SensorGroup
{
public:
  void print_measurement();
};


SensorGroup *myGroup;

void setup() {
  int i;
  sensor_t sensor;
  Serial.begin(9600);

  // Create the list of devices
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

  // Set delay between sensor readings based on sensor details.
  dht_array[0]->humidity().getSensor(&sensor);
  delayMS = sensor.min_delay / 1000;

  // Initialize the sensor group
  myGroup = new SensorGroup;
}

void loop() {
  String str;

  if(Serial.available() > 0)
  {
    str = Serial.readStringUntil('\n');
    str.trim();

    // Get the data if the command is "read"
    if(str=="read")
    {
      myGroup->print_measurement();
    }
  }
}

/** @brief Print data from all sensors */
void SensorGroup::print_measurement()
{
  uint8_t i;
  sensors_event_t event; 
  // Read all sensors
  for(i=0;i<N_SENSORS;i++)
  {
    Serial.print(i);
    Serial.print(";");
    dht_array[i]->temperature().getEvent(&event);
    if (isnan(event.temperature)) {
      Serial.print("Error reading temperature!;");
    }
    else {
      Serial.print(event.temperature);
      Serial.print(";");
    }
    // Get humidity event and print its value.
    dht_array[i]->humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
      Serial.println("Error reading humidity!");
    }
    else {
      Serial.println(event.relative_humidity);
    }
  }
}




