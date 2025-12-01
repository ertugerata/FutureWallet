# 💰 FutureWallet: BTC Simülatörü

FutureWallet, Bitcoin varlıklarınızın değerini gerçek zamanlı fiyatlar üzerinden takip etmenizi ve farklı fiyat senaryolarında ("What-If") toplam varlık değerinizin nasıl değişeceğini simüle etmenizi sağlayan bir MVP (Minimum Viable Product) uygulamasıdır.

## 🚀 Özellikler

- **Gerçek Zamanlı Veri:** CoinGecko API kullanarak anlık Bitcoin (BTC) fiyatını çeker.
- **Varlık Yönetimi:** Elinizdeki BTC miktarını ve nakit (USDT) tutarını girebilirsiniz.
- **Senaryo Analizi:** Bitcoin fiyatı değiştiğinde toplam varlığınızın ne olacağını interaktif bir slider ile simüle edebilirsiniz.
- **Kar/Zarar Hesaplama:** Mevcut durum ile simülasyon arasındaki farkı anlık olarak hesaplar ve gösterir.
- **Görselleştirme:** Fiyat değişimine bağlı varlık eğrisini grafik üzerinde gösterir.

## 🛠️ Teknolojiler

Bu proje aşağıdaki teknolojiler kullanılarak geliştirilmiştir:
- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) (Arayüz ve uygulama mantığı)
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) (Veri işleme)
- [CoinGecko API](https://www.coingecko.com/en/api) (Fiyat verisi)

## 📦 Kurulum

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin:

1. **Dosyaları edinin:**
   Repoyu klonlayın veya dosyaları bilgisayarınıza indirin.

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Kullanım

Kurulum tamamlandıktan sonra uygulamayı başlatmak için terminalde şu komutu çalıştırın:

```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak `http://localhost:8501` adresi açılacak ve uygulamayı kullanmaya başlayabileceksiniz.

## 📂 Dosya Yapısı

- `app.py`: Uygulamanın ana kaynak kodu.
- `requirements.txt`: Proje bağımlılıklarını içeren dosya.
- `shell.nix`: Nix ortam yapılandırması.
