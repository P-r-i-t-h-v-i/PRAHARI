// OLED test sketch for PRAHARI - XIAO nRF52840 + SSD1306 128x64 I2C
// I2C bus shared with MAX30100 / MLX90614 / AHT20 (SDA=D4, SCL=D5)

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1   // no dedicated reset pin
#define SCREEN_ADDRESS 0x3C // common addr; try 0x3D if this fails

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    while (1) delay(10);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("PRAHARI System");
  display.println("OLED Test OK");
  display.display();
}

void loop() {
  static uint32_t count = 0;
  display.clearDisplay();
  display.setCursor(0, 0);
  display.setTextSize(2);
  display.println("PRAHARI");
  display.setTextSize(1);
  display.print("Uptime: ");
  display.print(count++);
  display.println("s");
  display.display();
  delay(1000);
}
