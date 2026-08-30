// Diagnostic: read raw PART_ID register (0xFF) at I2C address 0x57.
// MAX30100 -> expects 0x11. MAX30102/MAX30105 -> expects 0x15.
// Helps confirm which chip is actually on the breakout board.

#include <Wire.h>

#define MAX3010X_ADDR 0x57
#define REG_PART_ID   0xFF
#define REG_REV_ID    0xFE

uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(MAX3010X_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(MAX3010X_ADDR, 1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0xFF;
}

void setup() {
  Wire.begin();
  Wire.setClock(100000);
  Serial.begin(115200);
  while (!Serial) delay(10);
  delay(500);

  uint8_t partId = readReg(REG_PART_ID);
  uint8_t revId = readReg(REG_REV_ID);

  Serial.print("PART_ID (0xFF): 0x");
  Serial.println(partId, HEX);
  Serial.print("REV_ID  (0xFE): 0x");
  Serial.println(revId, HEX);

  if (partId == 0x11) {
    Serial.println("-> Matches MAX30100");
  } else if (partId == 0x15) {
    Serial.println("-> Matches MAX30102 / MAX30105 (NOT MAX30100)");
  } else {
    Serial.println("-> Unrecognized part ID");
  }
}

void loop() {
  delay(1000);
}
