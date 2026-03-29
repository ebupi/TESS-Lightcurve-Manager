# TESS İndirme Aracı - Linux Kurulum Rehberi

Bu uygulama, Python yüklü olan herhangi bir Linux veya macOS sisteminde sorunsuz şekilde çalışabilir. Exe dosyaları sadece Windows içindir, ancak kaynak kodu Linux'ta rahatlıkla kullanabilirsiniz.

## Gereksinimler
Linux sisteminizde Python 3.8 veya üzeri ve `python3-tk` (Tkinter arayüzü için) yüklü olmalıdır.

Debian/Ubuntu tabanlı sistemlerde öncelikle Tkinter'ı yükleyin:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

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
