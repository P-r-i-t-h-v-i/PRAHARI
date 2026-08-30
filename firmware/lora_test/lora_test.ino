// SX1278 / Ra-02 / HW-691 LoRa test sketch for PRAHARI - XIAO nRF52840
// SPI: MOSI=D10, MISO=D9, SCK=D8 (hardware SPI defaults, no remap needed)
// NSS(CS)=D3, RESET=D2, DIO0=D1
// Library: LoRa by Sandeep Mistry (supports SX1276/77/78/79)
//
// LoRa.begin() reads the chip's version register over SPI and only
// returns true if it matches the expected SX127x value (0x12) -- this
// confirms SPI wiring/comms are correct, independent of a second radio
// to talk to. If begin() succeeds, this sketch also transmits a test
// packet every few seconds.

#include <SPI.h>
#include <LoRa.h>

#define LORA_NSS   3
#define LORA_RESET 2
#define LORA_DIO0  1

// Ra-02/HW-691 modules are commonly 433MHz variants; change to 868E6 or
// 915E6 to match your module's silkscreen/datasheet if different.
#define LORA_FREQUENCY 433E6

uint32_t counter = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  delay(500);

  LoRa.setPins(LORA_NSS, LORA_RESET, LORA_DIO0);

  Serial.print("Initializing LoRa (SX1278)...");
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("FAILED - check wiring/frequency");
    while (1) delay(10);
  }
  Serial.println("SUCCESS");
}

void loop() {
  Serial.print("Sending packet: ");
  Serial.println(counter);

  LoRa.beginPacket();
  LoRa.print("PRAHARI LoRa test #");
  LoRa.print(counter);
  LoRa.endPacket();

  counter++;
  delay(2000);
}
