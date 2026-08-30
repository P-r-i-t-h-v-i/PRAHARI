// MAX30100 heart rate + SpO2 test sketch for PRAHARI - XIAO nRF52840
// I2C bus shared with MLX90614 / AHT20 / OLED (SDA=D4, SCL=D5)
// Library: MAX30100lib (OXullo Intersecans)

#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

#define REPORTING_PERIOD_MS 1000

PulseOximeter pox;
uint32_t tsLastReport = 0;

void onBeatDetected() {
  Serial.println("Beat!");
}

void setup() {
  Serial.begin(115200);
  Serial.print("Initializing MAX30100...");

  if (!pox.begin()) {
    Serial.println("FAILED");
    while (1) delay(10);
  } else {
    Serial.println("SUCCESS");
  }

  // Adjust LED current if readings are too weak/saturated
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
  pox.setOnBeatDetectedCallback(onBeatDetected);
}

void loop() {
  pox.update();

  if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
    Serial.print("Heart rate: ");
    Serial.print(pox.getHeartRate());
    Serial.print(" bpm / SpO2: ");
    Serial.print(pox.getSpO2());
    Serial.println(" %");
    tsLastReport = millis();
  }
}
