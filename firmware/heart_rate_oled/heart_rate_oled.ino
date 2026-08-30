// Heart rate sensor -> SSD1306 OLED display, for PRAHARI - XIAO nRF52840
// Both devices share the same I2C bus (SDA=D4, SCL=D5) on distinct addresses:
//   Heart rate sensor (MAX30102/MAX30105, confirmed via PART_ID probe): 0x57
//   OLED (SSD1306 128x64): 0x3C
//
// Libraries: SparkFun MAX3010x Pulse and Proximity Sensor Library,
//            Adafruit GFX + Adafruit SSD1306

#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
byte beatsRecorded = 0;
long lastBeat = 0;
float beatsPerMinute;
int beatAvg = 0;

uint32_t lastDisplayUpdate = 0;
const uint32_t DISPLAY_PERIOD_MS = 500;

void setup() {
  Serial.begin(115200);

  Wire.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    while (1) delay(10);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("PRAHARI");
  display.println("Init heart sensor...");
  display.display();

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("Sensor NOT found");
    display.display();
    Serial.println("MAX3010x not found");
    while (1) delay(10);
  }

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  long irValue = particleSensor.getIR();
  bool fingerDetected = irValue >= 50000;

  if (!fingerDetected) {
    // Reset averaging so a fresh finger placement doesn't start from a
    // stale reading left over from the previous placement.
    rateSpot = 0;
    beatsRecorded = 0;
    beatAvg = 0;
  }

  if (checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;
      if (beatsRecorded < RATE_SIZE) beatsRecorded++;

      beatAvg = 0;
      for (byte x = 0; x < beatsRecorded; x++) beatAvg += rates[x];
      beatAvg /= beatsRecorded;
    }
  }

  if (millis() - lastDisplayUpdate > DISPLAY_PERIOD_MS) {
    lastDisplayUpdate = millis();

    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("PRAHARI - Heart Rate");
    display.drawLine(0, 10, SCREEN_WIDTH, 10, SSD1306_WHITE);

    if (!fingerDetected) {
      display.setCursor(0, 25);
      display.setTextSize(1);
      display.println("Place finger on");
      display.println("sensor...");
    } else {
      display.setCursor(0, 20);
      display.setTextSize(1);
      display.println("BPM:");
      display.setCursor(0, 32);
      display.setTextSize(3);
      display.print(beatAvg);
    }

    display.setTextSize(1);
    display.setCursor(0, 56);
    display.print("IR:");
    display.print(irValue);

    display.display();
  }
}
