# 💰 FutureWallet Ultimate: AI Finansal Asistan

FutureWallet Ultimate, Bitcoin varlıklarınızın değerini gerçek zamanlı fiyatlar üzerinden takip etmenizi, geçmiş performansınızı diğer yatırım araçlarıyla (Altın, S&P 500, Enflasyon) kıyaslamanızı ve yapay zeka desteğiyle işlem stratejilerinizi analiz etmenizi sağlayan kapsamlı bir finansal simülasyon uygulamasıdır.

## 🚀 Özellikler

- **Gerçek Zamanlı ve Esnek Veri:** Binance API (`ccxt`) üzerinden anlık Bitcoin (BTC) fiyatını çeker. API erişim sorunu durumunda manuel fiyat girişi desteği sunar.
- **Detaylı Geçmiş Analizi:** Cüzdan performansınızı **S&P 500**, **Altın** ve **ABD Enflasyonu** ile grafik üzerinde karşılaştırır.
- **İşlem Geçmişi Analizi:** Borsa veya Excel'den aldığınız işlem geçmişini (CSV/Excel) yükleyerek yapay zekaya (Gemini) stratejinizi, kar/zarar durumunuzu ve risk yönetiminizi yorumlatabilirsiniz.
- **Senaryo Analizi (What-If):** "Bitcoin X dolar olursa varlığım ne olur?" sorusuna interaktif slider ve manuel giriş ile yanıt bulabilirsiniz.
- **Dinamik Yapay Zeka Desteği:** API anahtarınız ile mevcut **Google Gemini** modelleri (Flash, Pro vb.) arasından seçim yapabilir, analizlerinizi istediğiniz modelle gerçekleştirebilirsiniz.
- **Kayıtlı Analizler:** Yaptığınız tüm simülasyonları ve yapay zeka yorumlarını veritabanına (`SQLite`) kaydeder, dilediğiniz zaman geçmiş analizlerinizi inceleyebilir veya silebilirsiniz.
- **Mobil Uyumlu Arayüz:** Tüm grafikler ve tablolar mobil cihazlarda rahatça görüntülenebilecek şekilde optimize edilmiştir.

## 🛠️ Teknolojiler

Bu proje aşağıdaki teknolojiler kullanılarak geliştirilmiştir:
- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) (Arayüz ve uygulama mantığı)
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) (Veri işleme)
- [CCXT](https://github.com/ccxt/ccxt) (Binance Borsa Verisi)
- [yfinance](https://pypi.org/project/yfinance/) (S&P 500 ve Altın Verisi)
- [Google Generative AI](https://ai.google.dev/) (Gemini Modelleri)
- [SQLite](https://www.sqlite.org/index.html) (Veri Saklama)
- [OpenPyXL](https://openpyxl.readthedocs.io/) & [xlrd](https://xlrd.readthedocs.io/) (Excel Desteği)

## 📦 Kurulum & Çalıştırma

Projeyi çalıştırmak için Python ortamı veya Docker kullanabilirsiniz.

### Seçenek 1: Python ile Çalıştırma

1. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Konfigürasyon (Opsiyonel):**
   Uygulama 12-Factor App prensiplerine uygun olarak Environment Variable desteği kazanmıştır. `.env` dosyası oluşturarak API anahtarınızı tanımlayabilirsiniz:
   ```bash
   # .env dosyası
   GOOGLE_API_KEY=AIzaSy...
   ```
   *Eğer tanımlamazsanız, uygulama arayüzünden manuel girebilirsiniz.*

3. **Uygulamayı başlatın:**
   ```bash
   streamlit run app.py
   ```

### Seçenek 2: Docker ile Çalıştırma (Önerilen)

Projeyi izole bir ortamda çalıştırmak için Docker kullanabilirsiniz.

1. **İmajı oluşturun:**
   ```bash
   docker build -t futurewallet .
   ```

2. **Konteyneri çalıştırın:**
   ```bash
   docker run -p 8501:8501 --env-file .env futurewallet
   ```
   *(Eğer .env dosyanız yoksa `--env-file .env` kısmını silebilirsiniz.)*

Uygulama `http://localhost:8501` adresinde çalışacaktır.

## 📱 Mobil Uyumluluk & Yol Haritası

Uygulama arayüzü mobil cihazlara uyumlu olacak şekilde optimize edilmiştir (Responsive Charts & Layouts).

Gelecekte tam teşekküllü bir mobil uygulamaya (iOS/Android) geçiş süreci için hazırlanan planı incelemek isterseniz:
👉 [MOBILE_ROADMAP.md](MOBILE_ROADMAP.md) dosyasını okuyunuz.

## 📂 Dosya Yapısı

- `app.py`: Uygulamanın ana kaynak kodu.
- `requirements.txt`: Proje bağımlılıklarını içeren dosya.
- `db.py`: Veritabanı işlemleri (SQLite).
- `shell.nix`: Nix ortam yapılandırması.
- `check_model.py`: Model ve API kontrol betiği.
