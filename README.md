# 💰 FutureWallet: AI Finansal Asistan

FutureWallet, Bitcoin varlıklarınızın değerini gerçek zamanlı fiyatlar üzerinden takip etmenizi, farklı fiyat senaryolarında ("What-If") toplam varlık değerinizin nasıl değişeceğini simüle etmenizi ve yapay zeka desteğiyle bu senaryoları analiz etmenizi sağlayan bir MVP (Minimum Viable Product) uygulamasıdır.

## 🚀 Özellikler

- **Gerçek Zamanlı Veri:** CoinGecko API kullanarak anlık Bitcoin (BTC) fiyatını çeker.
- **Varlık Yönetimi:** Elinizdeki BTC miktarını ve nakit (USDT) tutarını girebilirsiniz.
- **Senaryo Analizi:** Bitcoin fiyatı değiştiğinde toplam varlığınızın ne olacağını interaktif bir slider ile simüle edebilirsiniz.
- **Yapay Zeka Görüşü:** Oluşturduğunuz senaryoyu Google Gemini 1.5 Pro modeli ile analiz ettirip, risk ve strateji önerileri alabilirsiniz.
- **Kar/Zarar Hesaplama:** Mevcut durum ile simülasyon arasındaki farkı anlık olarak hesaplar ve gösterir.
- **Görselleştirme:** Fiyat değişimine bağlı varlık eğrisini grafik üzerinde gösterir.

## 🛠️ Teknolojiler

Bu proje aşağıdaki teknolojiler kullanılarak geliştirilmiştir:
- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) (Arayüz ve uygulama mantığı)
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) (Veri işleme)
- [CoinGecko API](https://www.coingecko.com/en/api) (Fiyat verisi)
- [Google Generative AI (Gemini 1.5 Pro)](https://ai.google.dev/) (Yapay zeka analizi)

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
- `shell.nix`: Nix ortam yapılandırması.
