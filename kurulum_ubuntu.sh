#!/bin/bash
# TESS Lightcurve Manager - Ubuntu Masaüstü Kısayolu Kurulumu

APP_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/tess-manager.desktop"

# phoebe conda ortamının python dizinini dinamik olarak bul
PYTHON_BIN=$(conda run -n phoebe which python 2>/dev/null)
if [ -z "$PYTHON_BIN" ]; then
    PYTHON_BIN="$HOME/anaconda3/envs/phoebe/bin/python"
fi

echo "TESS Lightcurve Manager masaüstü kısayolu oluşturuluyor..."

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Name=TESS Lightcurve Studio
Comment=TESS Işık Eğrisi Analiz Aracı
Exec=bash -c 'cd "$APP_DIR" && "$PYTHON_BIN" TESS_Araci.py'
Icon=$APP_DIR/app_icon.png
Terminal=false
Type=Application
Categories=Science;Astronomy;Education;
StartupWMClass=TESS Lightcurve Studio
EOF

chmod +x "$DESKTOP_FILE"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null

echo "✅ Kurulum tamamlandı!"
echo "Artık Ubuntu uygulama menüsünü açıp 'TESS Lightcurve Studio' yazarak doğrudan çalıştırabilirsiniz."
