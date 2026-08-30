# PRAHARI

Wearable health/safety monitoring band built on Seeed XIAO nRF52840, with LoRa (SX1278/Ra-02/HW-691), MAX30100 heart rate sensor, and MLX90614/AHT20 temperature sensing.

## Hardware

### SX1278 / Ra-02 / HW-691 LoRa Module → XIAO nRF52840
- VCC: 3V3
- GND: GND
- MOSI: D10
- MISO: D9
- SCK: D8
- NSS (CS): D3
- RESET (RST): D2
- DIO0: D1

### MAX30100 Heart Rate Sensor → XIAO nRF52840
- VIN: 3V3
- GND: GND
- SCL: D5
- SDA: D4
- INT: D0 (optional)

### MLX90614 / AHT20 Temperature Sensor(s) → XIAO nRF52840
- VIN/VCC: 3V3
- GND: GND
- SCL: D5
- SDA: D4

### SSD1306 OLED Display → XIAO nRF52840
- VCC: 3V3
- GND: GND
- SDA: D4 (shared I2C bus)
- SCL: D5 (shared I2C bus)

### Shared pins
- **3V3**: shared power rail for all modules. XIAO nRF52840 is not 5V tolerant — do not use a 5V rail.
- **GND**: common star ground for all modules to reduce PPG signal noise.
- **D4 (SDA) / D5 (SCL)**: shared I2C bus. MAX30100, MLX90614, AHT20, and the OLED can all coexist here since each uses a distinct I2C address.

## Structure
- `firmware/oled_test/` — standalone SSD1306 OLED test sketch (Adafruit_GFX + Adafruit_SSD1306)

## Recent changes
- **2026-08-30** — Added standalone SSD1306 OLED test sketch (`firmware/oled_test/oled_test.ino`).
