// I2C bus scanner for PRAHARI - XIAO nRF52840
// Scans the shared I2C bus (SDA=D4, SCL=D5) and reports any responding addresses.
// MAX30100 -> 0x57, MLX90614 -> 0x5A, AHT20 -> 0x38, SSD1306 -> 0x3C/0x3D

#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) delay(10);
  delay(1000);
  Serial.println("I2C Scanner starting...");
}

void loop() {
  byte error, address;
  int nDevices = 0;

  Serial.println("Scanning...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Device found at 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      nDevices++;
    } else if (error == 4) {
      Serial.print("Unknown error at 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }

  if (nDevices == 0) {
    Serial.println("No I2C devices found");
  } else {
    Serial.print(nDevices);
    Serial.println(" device(s) found");
  }

  delay(3000);
}
