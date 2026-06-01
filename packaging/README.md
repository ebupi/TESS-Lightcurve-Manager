# TESS Lightcurve Studio - Paketleme Rehberi (Packaging Guide)

Bu klasör, uygulamayı Windows için `.exe` (tek dosya taşınabilir uygulama) ve Debian/Ubuntu tabanlı Linux sistemleri için `.deb` (kurulum paketi) formatlarında derlemek ve paketlemek için gerekli tüm araçları içerir.

This folder contains all the tools needed to compile and package the application into a `.exe` for Windows and a `.deb` installer for Debian/Ubuntu-based Linux systems.

---

## 📦 1. Linux için Debian (.deb) Paketi Oluşturma

Linux üzerinde standalone (harici Python kurulumu gerektirmeyen) bir `.deb` paketi oluşturmak için projenin kök dizinindeyken terminalde aşağıdaki komutu çalıştırmanız yeterlidir:

To build a standalone `.deb` package on Linux (which doesn't require a pre-installed Python environment), simply run the packaging script:

```bash
./packaging/build_deb.sh
```

### Bu betik ne yapar? (What does this script do?)
1. Conda veya sistem ortamınızda `pyinstaller` kütüphanesini kontrol eder, yoksa kurar.
2. `TESS_Araci.py` uygulamasını tüm bağımlılıklarıyla birlikte tek bir Linux çalıştırılabilir dosyasına derler.
3. `/usr/bin/tess-lightcurve-studio` altına çalıştırılabilir dosyayı yerleştirir.
4. `/usr/share/applications` altına bir masaüstü kısayolu (`.desktop` dosyası) oluşturur.
5. `/usr/share/pixmaps` altına uygulama ikonunu kopyalar.
6. `dpkg-deb` komutunu kullanarak `tess-lightcurve-studio_2.0_amd64.deb` paketini oluşturur.

### Kurulum (Installation):
Oluşturulan `.deb` paketini kurmak için:
```bash
sudo dpkg -i packaging/tess-lightcurve-studio_2.0_amd64.deb
# Eğer eksik bağımlılık uyarısı alırsanız:
sudo apt-get install -f
```
Kurulum tamamlandıktan sonra uygulama menünüzde **TESS Lightcurve Studio** olarak görünecektir.

---

## 🪟 2. Windows için (.exe) Oluşturma

Windows (.exe) derlemesi, Windows işletim sistemi üzerinde yapılmalıdır (PyInstaller cross-compilation desteklemez).

To build the Windows executable, you must run the build command on a Windows machine:

1. Windows Command Prompt veya PowerShell açın.
2. Projenin bulunduğu dizine gidin (`cd TESS-Lightcurve-Manager`).
3. Aşağıdaki komut ile derleme betiğini çalıştırın:

```cmd
python packaging/build_exe.py
```

### Alternatif Manuel Komut (Alternative Manual Command):
Eğer betik yerine doğrudan komut satırından derlemek isterseniz, `packaging` klasörü içinde şu komutu çalıştırabilirsiniz:
```cmd
pyinstaller --clean tess_manager.spec
```

Derleme tamamlandığında tek parça çalıştırılabilir `.exe` dosyanız `packaging/dist/TESS_Lightcurve_Studio.exe` altında hazır olacaktır.

---

## 🛠️ Dosya Yapısı (File Structure)
* **[tess_manager.spec](file:///home/ebupi/TESS-Lightcurve-Manager/packaging/tess_manager.spec)**: PyInstaller için ortak yapılandırma dosyası (ikon, ek dosyalar ve kütüphaneleri tanımlar).
* **[build_deb.sh](file:///home/ebupi/TESS-Lightcurve-Manager/packaging/build_deb.sh)**: Linux paketleme otomasyon betiği.
* **[build_exe.py](file:///home/ebupi/TESS-Lightcurve-Manager/packaging/build_exe.py)**: Windows derleme otomasyon betiği.
