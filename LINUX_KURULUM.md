# TESS İndirme Aracı - Linux Kurulum Rehberi (v2.0)

Bu uygulama, Python yüklü olan herhangi bir Linux veya macOS sisteminde sorunsuz şekilde çalışabilir. Exe dosyaları sadece Windows içindir, ancak kaynak kodu Linux'ta rahatlıkla kullanabilirsiniz.

## Gereksinimler
Linux sisteminizde Python 3.8 veya üzeri yüklü olmalıdır. Uygulama arayüzü artık **PyQt5** kullanmaktadır.

Eğer sistem genelinde (apt ile) paket kurmanız gerekirse `python3-pyqt5` paketini kurabilirsiniz, ancak `requirements.txt` ile kurmak en kolayıdır.

## Kurulum Adımları
1. Bu dizinde (TESS_Araci klasöründe) bir terminal açın.
2. Gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırın:
```bash
pip3 install -r requirements.txt
```

## Çalıştırma
Kütüphaneler yüklendikten sonra aracı başlatmak için:
```bash
python3 TESS_Araci.py
```

Işık eğrileri ve indirme seçenekleri Linux ortamında da tamamen aynı görsel ve mantıkla çalışacaktır.
