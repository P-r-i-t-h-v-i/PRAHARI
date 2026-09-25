# PRAHARI — SIH 2026

The editable PowerPoint and matching PDF contain six slides, using the supplied SIH template as the base. The template's required sections, aspect ratio and branding are retained; content layouts, fonts and colors are restyled. The instruction slide is removed. Presenter notes include explanation and evidence.

**Before submission:** enter the registered Team ID on slide 1 and export the PDF again. The source presentation names the team **Point Break** and problem statement **26181**, but leaves Team ID blank.

## Sources and image credits

- Local references: `~/Downloads/PRAHARI_SIH2026_Idea_3.pdf`, `~/Downloads/PRAHARI_Project_Report.pdf`, `~/Documents/Obsidian/Projects/PRAHARI.md` and linked hardware notes, project README and PCB documentation.
- [CEEW heat-risk study, 2025](https://www.ceew.in/publications/mapping-climate-risks-and-impacts-of-extreme-heatwave-disaster-in-indian-districts): the 57% district statistic.
- [NDMA SACHET](https://sachet.ndma.gov.in/): official CAP / RSS alert source.
- [Buller et al.](https://ojs.aaai.org/index.php/AAAI/article/view/18809): physiological estimation research; not validation of this device.
- [Seeed Studio documentation](https://wiki.seeedstudio.com/XIAO_BLE/): MCU platform and actual component image on slide 3.
- Slides 1 and 5: **yajna S R**, [construction workers in Mumbai, Pexels](https://www.pexels.com/photo/construction-workers-working-on-top-of-a-building-20591230/), under the [Pexels License](https://www.pexels.com/license/). Contextual photography; these people are not claimed to be the team or trial participants.
- SIH 2026 logo: extracted from the supplied template.

No AI image generation was used. The board image is a manufacturer component image, not a finished Prahari prototype photograph. Diagrams are editable PowerPoint shapes and text.

## Evidence and validation

The deck distinguishes demonstrated heart-rate/OLED work from planned forecasting, app, relay and security integration. The rev B architecture uses MAX30102, MAX30208 and SX1262. The alert path includes a LoRa gateway band after the connected phone. New official alerts require a connected entry point.

The old ₹3,468 figure covers selected rev A modules, not a complete rev B band, so it is not quoted as a finished device price. Unverified range, accuracy, clinical outcome, competitor and regulatory claims are omitted. Air temperature and humidity are not called full measured WBGT.

Generated with python-pptx and exported with LibreOffice. PowerPoint geometry and PDF text boundaries were checked; all six slides were visually reviewed. `build_deck.py` rebuilds the deck; `review_deck.py` renders previews and checks the PDF. Fonts: Lato. Palette: navy, warm ivory, teal, amber.
