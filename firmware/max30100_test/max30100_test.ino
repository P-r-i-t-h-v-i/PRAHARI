// Heart rate / SpO2 test sketch for PRAHARI - XIAO nRF52840
// I2C bus shared with MLX90614 / AHT20 / OLED (SDA=D4, SCL=D5)
//
// NOTE: the breakout board wired here reports PART_ID 0x15 (confirmed via a
// raw register probe), which is the MAX30102/MAX30105 chip ID, not the true
// MAX30100 (0x11). This is a common mislabeling on cheap "MAX30100" modules.
// Using the SparkFun MAX3010x library (MAX30105 API, also drives MAX30102).
//
// Library: SparkFun MAX3010x Pulse and Proximity Sensor Library

#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  delay(500);
  Serial.print("Initializing sensor...");

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("FAILED");
    while (1) delay(10);
  }
  Serial.println("SUCCESS");

  particleSensor.setup();                    // default config: IR + Red LEDs
  particleSensor.setPulseAmplitudeRed(0x0A);  // low red LED for basic heartbeat
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;

      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print("IR: ");
  Serial.print(irValue);
  Serial.print(" BPM: ");
  Serial.print(beatsPerMinute);
  Serial.print(" Avg BPM: ");
  Serial.print(beatAvg);

  if (irValue < 50000) Serial.print(" No finger?");

  Serial.println();
}
