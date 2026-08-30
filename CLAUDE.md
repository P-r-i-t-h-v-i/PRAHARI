# PRAHARI

Wearable health/safety monitoring band: XIAO nRF52840 + SX1278 LoRa + MAX30100 + MLX90614/AHT20 + SSD1306 OLED.

See README.md for full wiring reference and structure.

## Changelog
- **2026-08-30** — Added standalone SSD1306 OLED test sketch (`firmware/oled_test/oled_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added standalone MAX30100 heart rate/SpO2 test sketch (`firmware/max30100_test/max30100_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added `firmware/i2c_scanner` and `firmware/max30100_probe` diagnostics; discovered the heart-rate breakout is actually a MAX30102/MAX30105 (PART_ID 0x15) mislabeled as MAX30100; switched `max30100_test` to the SparkFun MAX3010x library, confirmed working (live IR readings on hardware).
