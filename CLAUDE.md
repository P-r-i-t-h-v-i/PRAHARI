# PRAHARI

Wearable health/safety monitoring band: XIAO nRF52840 + SX1278 LoRa + MAX30100 + MLX90614/AHT20 + SSD1306 OLED.

See README.md for full wiring reference and structure.

## Repo & sync policy
- GitHub remote: `https://github.com/P-r-i-t-h-v-i/PRAHARI` (private), local branch `main` tracks `master`. This is the folder's only repo — don't ask which repo to push to, just use it (per the global git auto-push policy in `~/.claude/CLAUDE.md`).
- Obsidian project note: `Projects/PRAHARI.md` in the vault at `~/Documents/Obsidian` (reached via the `obsidian` MCP server), with topic notes under `Topics/` (e.g. `Topics/KiCad.md`) linked from it.
- On every code change in this folder: commit + push to GitHub, AND append a dated one-line "Recent changes"/changelog entry to all three of README.md, this file's Changelog, and the Obsidian project note — keep them word-for-word in sync (per the global Obsidian + git policies in `~/.claude/CLAUDE.md`). Do this automatically, without being asked each time.

## Changelog
- **2026-08-30** — Added standalone SSD1306 OLED test sketch (`firmware/oled_test/oled_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added standalone MAX30100 heart rate/SpO2 test sketch (`firmware/max30100_test/max30100_test.ino`); flashed and verified on XIAO nRF52840 hardware.
- **2026-08-30** — Added `firmware/i2c_scanner` and `firmware/max30100_probe` diagnostics; discovered the heart-rate breakout is actually a MAX30102/MAX30105 (PART_ID 0x15) mislabeled as MAX30100; switched `max30100_test` to the SparkFun MAX3010x library, confirmed working (live IR readings on hardware).
- **2026-08-30** — Verified `max30100_test` end-to-end with a live finger on the sensor: IR rose from ~400 (no finger) to ~96000, avg BPM stabilized at 78.
- **2026-08-30** — Added `firmware/lora_test` and `firmware/lora_probe`; LoRa module not yet responding over SPI (RegVersion reads 0x00), diagnosis in progress.
- **2026-08-30** — Added `firmware/heart_rate_oled`, combining the heart-rate sensor with the SSD1306 OLED to display live BPM; flashed and both devices initialized successfully.
- **2026-08-30** — Fixed `heart_rate_oled` showing unrealistically low BPM (e.g. 8) right after placing a finger: rolling average was dividing by fixed window size before it filled with real beats. Now averages only over beats actually recorded, and resets on finger removal.
- **2026-08-30** — Added serial debug logging to `heart_rate_oled` (beat delta/BPM, rejection reason, IR/finger/avg snapshot every 1s); compiled and uploaded to XIAO nRF52840 hardware via arduino-cli (installed `adafruit-nrfutil` locally to enable DFU upload over `/dev/ttyACM0`).
- **2026-09-01** — Added `pcb/` — KiCad PCB project for the PRAHARI board (schematic, layout, footprints, gerbers, BOM).
- **2026-09-01** — Documented repo/Obsidian sync policy in CLAUDE.md: this folder always pushes to `P-r-i-t-h-v-i/PRAHARI` and syncs `Projects/PRAHARI.md` in Obsidian automatically on every change, no confirmation needed.
- **2026-09-02** — Imported rev B PCB from `PRAHARI-PCB.zip` into `pcb/` (replacing rev A files; leftover rev A gerbers/drills in `pcb/out/` root are untracked and pending removal); verified all 38 footprints match schematic, netlist and KiCad 10 libraries pad-for-pad; ran ERC/DRC with kicad-cli 10.0.6 (flatpak): ERC clean (202 known cosmetic warnings), DRC fails the project bar — 3 errors (J6/U2 courtyard collision, RF clearance) + 4 unconnected (LORA_DIO1, DW_VDD ×2, F/B GND pour tie) vs expected 0/0/8; last DRC-clean board is the nested `PRAHARI-revB-verified-20260902-1120.zip`; added `.gitignore` for nested zips, backups and lock files.
- **2026-09-25** — Added `pcb/scripts/build_report_pdf.py` PDF report generator (title/idea, how-it-works, PCB renders, schematic, BOM, build status); iteratively cleaned it to remove PS number/category, the duplicate bottom-PCB image, all "SIH 2026" references (page header and schematic company field), the "open issues" section, and the "things to reconcile" section; added a final "From Prototype to Integrated Board" section answering the prototype-evolution, improvement, and testing-insight/next-steps questions in full prose.
- **2026-09-25** — Removed "rev B hardware" from the PDF report's page footer (was repeated on every page).
