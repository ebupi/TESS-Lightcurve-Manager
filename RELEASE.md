# Release v2.0.0 - Standalone Desktop Application Support 🚀

We are excited to announce **TESS Lightcurve Studio v2.0.0**! This release introduces cross-platform standalone packaging, allowing users to run the application on Windows (`.exe`) and Linux (`.deb`) without needing to install Python or any scientific packages manually.

## What's New in v2.0.0 ✨
*   **PyQt5 GUI Interface**: Fully updated user interface for modern, responsive desktop controls.
*   **Interactive Visualizations**: Embedded Plotly web engine to visualize lightcurves, fold periods, and zoom in/out interactively.
*   **Astroquery MAST & VizieR Integration**: Fetch targets directly from NASA MAST and ephemeris (T0/Period) database servers automatically.
*   **Standalone Cross-Platform Packages**:
    *   **Windows (`.exe`)**: Run directly with a simple double-click.
    *   **Linux (`.deb`)**: Native installation with automatic desktop shortcuts and icons, requiring 0 external Python setup.

---

## 📦 How to Install and Run

### 🐧 Linux (Debian / Ubuntu / Mint)
You can install the pre-packaged standalone application using the `.deb` file:

1. Download `tess-lightcurve-studio_2.0_amd64.deb` from this Release assets.
2. Install via terminal:
   ```bash
   sudo dpkg -i tess-lightcurve-studio_2.0_amd64.deb
   # Fix any missing system dependencies if prompted:
   sudo apt-get install -f
   ```
3. Open your applications menu, search for **TESS Lightcurve Studio**, and launch it!

### 🪟 Windows (10 / 11)
1. Download `TESS_Lightcurve_Studio.exe` from this Release assets.
2. Double-click the `.exe` file to run the application directly. No installation needed.

---

## 🛠️ Developer: How to Build Your Own Packages
We have added automation scripts under the `packaging/` directory:

*   **For Linux (`.deb`)**: Run `./packaging/build_deb.sh` on your Ubuntu/Debian machine. It will automatically set up a clean, minimal virtual environment, compile the code, and package it.
*   **For Windows (`.exe`)**: Run `python packaging/build_exe.py` on your Windows machine to bundle all assets.

---

## 📄 Release Assets
*   `TESS_Lightcurve_Studio.exe` (Windows Standalone Executable)
*   `tess-lightcurve-studio_2.0_amd64.deb` (Debian/Ubuntu Standalone Installer)
*   Source Code (`.zip` / `.tar.gz`)
