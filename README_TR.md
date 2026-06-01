<div align="right">
  <a href="README.md"><img src="https://img.shields.io/badge/Lang-EN-blue.svg" alt="EN"></a>
</div>

# TESS Işık Eğrisi İndirme Aracı (v2.0)

TESS (Transiting Exoplanet Survey Satellite) verilerini sağlanan MAST sunucularından aramanızı, grafik üzerinden incelemenizi ve toplu şekilde bilgisayarınıza indirmenizi sağlayan masaüstü bir araçtır. **Yeni sürüm ile birlikte arayüz PyQt5 kullanılarak tamamen modernize edilmiştir.**

![TESS Aracı Arayüzü Işık Eğrisi](light_curve.png)
![TESS Aracı Arayüzü Evre Grafiği](phase.png)

## Özellikler
- **Çoklu Gök Cismi Arama**: Virgül ile ayrılmış gök cismi adlarıyla tek tıklamayla çoklu arama yapılabilir.
- **Birleşik Canlı Önizleme**: Lightkurve ve Matplotlib (Qt5) altyapısı ile birden fazla ışık eğrisini tek grafik üzerinde pürüzsüz (anti-aliased) bir şekilde inceleyebilirsiniz.
- **Gelişmiş Dışa Aktarma (Export)**: Verileri FITS olarak veya ayırıcı (separator) ve ondalık (decimal) seçeneklerini kendiniz belirleyebildiğiniz gelişmiş CSV formatlarında indirebilirsiniz. İstediğiniz sütunları (`time`, `flux`, `flux_err`) seçebilirsiniz.
- **Platform Bağımsız Pürüzsüz Arayüz**: PyQt5 sayesinde hem Windows hem Linux'ta keskin ve profesyonel arayüz görünümü.

## Kurulum (Geliştiriciler & Linux/macOS)
Projenin çalışması için Python gereklidir:
1. `pip install -r requirements.txt`
2. `python TESS_Araci.py`

*(Daha hızlı bir Linux veya macOS kurulumu için `LINUX_KURULUM.md` belgesine bakabilirsiniz.)*

## 📥 Hazır Uygulama İndir (Python Gerekmez!)
Yazılımcı olmayan normal kullanıcılar, derlenmiş hazır masaüstü uygulamasını doğrudan indirebilir:
- **🪟 Windows (10/11)**: [TESS_Lightcurve_Studio.exe](https://github.com/ebupi/TESS-Lightcurve-Manager/releases/download/v2.0.0/TESS_Lightcurve_Studio.exe) dosyasını indirin (Kurulum gerekmez, çift tıklayarak çalıştırın).
- **🐧 Linux (Ubuntu/Debian)**: [tess-lightcurve-studio_2.0_amd64.deb](https://github.com/ebupi/TESS-Lightcurve-Manager/releases/download/v2.0.0/tess-lightcurve-studio_2.0_amd64.deb) paketini indirin (Terminalde `sudo dpkg -i <dosya_adi>` komutu ile kurun).
