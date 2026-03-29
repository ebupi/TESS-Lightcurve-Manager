# TESS Işık Eğrisi İndirme Aracı

TESS (Transiting Exoplanet Survey Satellite) verilerini sağlanan MAST sunucularından aramanızı, grafik üzerinden incelemenizi ve toplu şekilde bilgisayarınıza indirmenizi sağlayan masaüstü bir araçtır.

## Özellikler
- **Çoklu Gök Cismi Arama**: Virgül ile ayrılmış gök cismi adlarıyla (Örn: `TT And, V1298 Tau`) tek tıklamayla çoklu arama yapılabilir.
- **Canlı Önizleme**: Lightkurve ve Matplotlib altyapısı ile ışık eğrilerini indirmeden önce yüksek çözünürlüklü görebilirsiniz.
- **Çoklu Format İndirme**: Grafikleri ham FITS veya analize (Excel vb.) hazır CSV formatlarında indirebilirsiniz.

## Kurulum (Geliştiriciler & Linux/macOS)
Projenin çalışması için Python gereklidir:
1. `pip install -r requirements.txt`
2. `python TESS_Araci.py`

*(Daha hızlı bir Linux veya macOS kurulumu için `LINUX_KURULUM.md` belgesine bakabilirsiniz.)*

## Windows İçin
Windows'da çalışan kullanıcılar doğrudan `dist` klasörü içindeki (eğer yayınlandıysa) `TESS_Araci.exe` dosyası ile uygulamayı kurulum gerekmeden çalıştırabilirler.
