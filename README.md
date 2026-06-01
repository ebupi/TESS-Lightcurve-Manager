<div align="right">
  <a href="README_TR.md"><img src="https://img.shields.io/badge/Lang-TR-red.svg" alt="TR"></a>
</div>

# TESS Lightcurve Manager (v2.0)

A desktop tool that allows you to search for TESS (Transiting Exoplanet Survey Satellite) data from MAST servers, preview them on a plot, and batch download them to your computer. **With the new release, the GUI has been completely modernized using PyQt5.**

![TESS Manager Interface Light Curve](light_curve.png)
![TESS Manager Interface Phase](phase.png)
## Features
- **Multi-Target Search**: Perform multi-target searches with a single click using comma-separated target names.
- **Combined Live Preview**: Powered by Lightkurve and Matplotlib (Qt5), you can smoothly view multiple lightcurves combined on a single anti-aliased plot.
- **Advanced Export Options**: Download data as FITS or in advanced CSV formats where you can customize the separator and decimal character. You can also select specific columns (`time`, `flux`, `flux_err`) to save.
- **Cross-Platform Smooth UI**: Crisp and professional user interface appearance on both Windows and Linux thanks to PyQt5.

## Installation (Developers & Linux/macOS)
Python is required for the project to run:
1. `pip install -r requirements.txt`
2. `python TESS_Araci.py`

*(For a faster Linux or macOS installation, please check the `LINUX_KURULUM.md` document.)*

## For Windows Users
Windows users can directly run the application using the `TESS_Araci.exe` file located in the `dist` folder (if published) without needing any installation.
