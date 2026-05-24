# TESS Işık Eğrisi İndirme Aracı (v2.0)

TESS (Transiting Exoplanet Survey Satellite) verilerini sağlanan MAST sunucularından aramanızı, grafik üzerinden incelemenizi ve toplu şekilde bilgisayarınıza indirmenizi sağlayan masaüstü bir araçtır. **Yeni sürüm ile birlikte arayüz PyQt5 kullanılarak tamamen modernize edilmiştir.**

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

## Windows İçin
Windows'da çalışan kullanıcılar doğrudan `dist` klasörü içindeki (eğer yayınlandıysa) `TESS_Araci.exe` dosyası ile uygulamayı kurulum gerekmeden çalıştırabilirler.
