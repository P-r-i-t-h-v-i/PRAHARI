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
- `firmware/max30100_test/` — heart rate/SpO2 test sketch (SparkFun MAX3010x library)
- `firmware/i2c_scanner/` — I2C bus scanner, useful for diagnosing wiring/address issues
- `firmware/max30100_probe/` — raw I2C register probe that reads the sensor's PART_ID (0xFF) to identify the actual chip
- `firmware/lora_test/` — SX1278 LoRa test sketch (LoRa library by Sandeep Mistry), currently unresolved: chip not responding over SPI (see Known issues)
- `firmware/lora_probe/` — raw SPI register probe that reads the SX1278's RegVersion (0x42) directly, bypassing the LoRa library
- `firmware/heart_rate_oled/` — combined sketch: reads live heart rate and displays BPM on the SSD1306 OLED

## Known hardware note
The "MAX30100" heart-rate breakout in this build actually reports PART_ID `0x15` (MAX30102/MAX30105), not the true MAX30100 (`0x11`) — a common mislabeling on cheap breakout boards. Confirmed via `firmware/max30100_probe`. As a result, `firmware/max30100_test` uses the **SparkFun MAX3010x Pulse and Proximity Sensor Library** (MAX30105 API), not `MAX30100lib`, which fails to initialize against this chip regardless of I2C clock speed.

## Known issues
- LoRa module (SX1278/Ra-02/HW-691) not responding over SPI: `RegVersion` (0x42) reads `0x00` regardless of SPI clock speed (tried 1MHz and 100kHz), and after multiple wiring re-checks (VCC, MISO, GND, MOSI, SCK, NSS, RESET). Frequency (433MHz) and pin mapping have been verified correct in code/source. Suspect either a persistent physical connection fault or a dead module — next step is a multimeter continuity check per-wire, or swapping in a spare module if available.

## Recent changes
- **2026-08-30** — Added standalone SSD1306 OLED test sketch (`firmware/oled_test/oled_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added standalone MAX30100 heart rate/SpO2 test sketch (`firmware/max30100_test/max30100_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added `firmware/i2c_scanner` and `firmware/max30100_probe` diagnostics; discovered the heart-rate breakout is actually a MAX30102/MAX30105 (PART_ID 0x15) mislabeled as MAX30100; switched `max30100_test` to the SparkFun MAX3010x library, confirmed working (live IR readings on hardware).
- **2026-08-30** — Verified `max30100_test` end-to-end with a live finger on the sensor: IR rose from ~400 (no finger) to ~96000, avg BPM stabilized at 78.
- **2026-08-30** — Added `firmware/lora_test` and `firmware/lora_probe`; LoRa module not yet responding over SPI, diagnosis in progress (see Known issues).
- **2026-08-30** — Added `firmware/heart_rate_oled`, combining the heart-rate sensor with the SSD1306 OLED to display live BPM; flashed and both devices initialized successfully.
- **2026-08-30** — Fixed `heart_rate_oled` showing unrealistically low BPM (e.g. 8) right after placing a finger: the rolling average was dividing by the fixed window size (4) even before 4 real beats were recorded, diluting early readings with zero-initialized buffer slots. Now averages only over beats actually recorded, and resets the average when the finger is removed so a fresh placement doesn't inherit a stale reading.
- **2026-08-30** — Added serial debug logging to `heart_rate_oled` (beat delta/BPM, rejection reason, IR/finger/avg snapshot every 1s); compiled and uploaded to XIAO nRF52840 hardware via arduino-cli (installed `adafruit-nrfutil` locally to enable DFU upload over `/dev/ttyACM0`).
