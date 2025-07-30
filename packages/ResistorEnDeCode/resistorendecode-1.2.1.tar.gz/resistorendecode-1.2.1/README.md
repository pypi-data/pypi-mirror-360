<img align="right" src=icons/resistor_decoder.png width=120px>

# ResistorEn​Decode

This is a code copy (not a fork) from https://github.com/VoxelCubes/ResistorDecoder.  
Its a copy because, there are some infrastructure changes made which may not be very compatible with the original code base.

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This is a standalone Qt GUI tool for color bands on through-hole resistors and number codes on SMD parts.
It supports 3, 4, 5, and 6 band resistors, as well as standard SMD codes, including the EIA-96 standard.

| 3 or 4 Bands | 5 Bands |
|:------------:|:-------:|
|![4band](example_screenshots/4band.png)|![5band](example_screenshots/5band.png)|
| 6 Bands | SMD |
|![6band](example_screenshots/6band.png)|![smd](example_screenshots/smd.png)|

With this version you can also encode resistance values.

## Features
- Encode resistance values
- Decode the resistance and tolerance, as well as the Temperature Coefficient of Resistance (for 6 band resistors).
- Can parse SMD codes¹, including the EIA-96 standard.
- Respects your system's Qt theming.

## Dependencies
PySide6

```
pip install PySide6
```

## Installation


```
git clone https://github.com/AlfredoCubitos/ResistorEnDeCode
cd ResistorEnDecode
python src/main.py
```

## Notes
1. Tolerance values are only standardized for EIA-96 codes and codes with short underlines. Check the manufacturer's datasheet if the tolerance is critical for your application.
