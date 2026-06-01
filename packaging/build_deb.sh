#!/bin/bash
# Exit on any error
set -e

# Change directory to the script's directory
cd "$(dirname "$0")"

echo "=== TESS Lightcurve Studio (.deb) Packaging Script ==="

# 1. Create a clean, temporary Python virtual environment for minimal package size
echo "Creating isolated virtual environment for clean build..."
rm -rf .venv_build
python3 -m venv .venv_build

echo "Activating virtual environment..."
source .venv_build/bin/activate

echo "Installing minimal dependencies..."
pip install --upgrade pip
pip install -r ../requirements.txt pyinstaller

# 2. Build Linux Standalone Binary using PyInstaller
echo "Building standalone Linux binary..."
pyinstaller --clean tess_manager.spec

# 3. Verify output binary
EXE_PATH="dist/TESS_Lightcurve_Studio"
if [ ! -f "$EXE_PATH" ]; then
    echo "Error: PyInstaller failed to produce standalone binary at $EXE_PATH"
    deactivate
    rm -rf .venv_build
    exit 1
fi

echo "Standalone binary successfully created!"

# 4. Prepare Debian Package Structure
DEB_DIR="deb_build"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"

# Create Debian control file
cat <<EOF > "$DEB_DIR/DEBIAN/control"
Package: tess-lightcurve-studio
Version: 2.0
Section: science
Priority: optional
Architecture: amd64
Maintainer: Mustafa Salman <mustafasalman0502@gmail.com>
Depends: libc6
Description: TESS Lightcurve Studio
 A PyQt5 desktop application for fetching, visualizing, and analyzing lightcurves from the NASA TESS mission.
 It runs as a standalone compiled application with no external python runtime dependencies required.
EOF

# Copy the compiled binary to usr/bin
cp "$EXE_PATH" "$DEB_DIR/usr/bin/tess-lightcurve-studio"

# Copy the icon
cp ../tess_icon_v2.png "$DEB_DIR/usr/share/pixmaps/tess-lightcurve-studio.png"

# Create Desktop Shortcut
cat <<EOF > "$DEB_DIR/usr/share/applications/tess-lightcurve-studio.desktop"
[Desktop Entry]
Version=1.0
Name=TESS Lightcurve Studio
Comment=TESS Lightcurve Analysis Tool
Exec=/usr/bin/tess-lightcurve-studio
Icon=tess-lightcurve-studio
Terminal=false
Type=Application
Categories=Science;Astronomy;Education;
StartupWMClass=TESS_Lightcurve_Studio
EOF

# Set permissions
chmod 755 "$DEB_DIR/usr/bin/tess-lightcurve-studio"
chmod 644 "$DEB_DIR/usr/share/applications/tess-lightcurve-studio.desktop"
chmod 644 "$DEB_DIR/usr/share/pixmaps/tess-lightcurve-studio.png"
chmod 755 "$DEB_DIR/DEBIAN/control"

# 5. Build .deb package
echo "Building debian package using dpkg-deb..."
dpkg-deb --build "$DEB_DIR" tess-lightcurve-studio_2.0_amd64.deb

# Clean up temporary build folders and virtual environment
echo "Cleaning up build directory and temporary virtual environment..."
deactivate
rm -rf .venv_build
rm -rf "$DEB_DIR"
rm -rf build dist

echo "=============================================="
echo "🎉 Debian package successfully created:"
echo "   packaging/tess-lightcurve-studio_2.0_amd64.deb"
echo "=============================================="
