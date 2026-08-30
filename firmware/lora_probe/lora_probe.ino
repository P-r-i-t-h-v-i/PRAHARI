// Diagnostic: raw SPI read of the SX1278's RegVersion (0x42).
// Expected value: 0x12 for SX1276/77/78/79. Bypasses the LoRa library
// entirely to isolate whether the chip responds at the SPI transport
// level at all, independent of frequency/init logic.

#include <SPI.h>

#define LORA_NSS   3
#define LORA_RESET 2

uint8_t readRegister(uint8_t reg) {
  digitalWrite(LORA_NSS, LOW);
  SPI.transfer(reg & 0x7F); // MSB=0 for read
  uint8_t value = SPI.transfer(0x00);
  digitalWrite(LORA_NSS, HIGH);
  return value;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  delay(500);

  pinMode(LORA_NSS, OUTPUT);
  digitalWrite(LORA_NSS, HIGH);
  pinMode(LORA_RESET, OUTPUT);

  // Hardware reset pulse per SX127x datasheet
  digitalWrite(LORA_RESET, LOW);
  delay(10);
  digitalWrite(LORA_RESET, HIGH);
  delay(10);

  SPI.begin();
  SPI.beginTransaction(SPISettings(100000, MSBFIRST, SPI_MODE0));

  uint8_t version = readRegister(0x42);

  SPI.endTransaction();

  Serial.print("RegVersion (0x42): 0x");
  Serial.println(version, HEX);

  if (version == 0x12) {
    Serial.println("-> SX1276/77/78/79 detected correctly");
  } else if (version == 0x00 || version == 0xFF) {
    Serial.println("-> No response (0x00/0xFF) - check wiring/power/CS pin");
  } else {
    Serial.println("-> Unexpected value - possibly different chip or bad connection");
  }
}

void loop() {
  delay(1000);
}
