# 📱 FutureWallet Mobil Uygulama Yol Haritası (Roadmap)

Bu belge, **FutureWallet** projesinin mevcut Streamlit prototipinden tam teşekküllü bir mobil uygulamaya dönüşüm sürecini planlamaktadır.

## 📊 Mevcut Durum (Streamlit Prototipi)

Şu anki kod tabanı (`app.py`), aşağıdaki özelliklerle çalışan kararlı bir prototiptir ve mobil dönüşüm için gerekli iş mantığını barındırmaktadır:
*   **Mimari:** İş mantığı (`services/`) ve arayüz (`views/`) katmanlarına ayrılmış modüler yapı.
*   **Yapay Zeka:** Google Gemini 1.5 Flash/Pro entegrasyonu (Model seçimi, Chat analizi).
*   **Makine Öğrenmesi:** XGBoost ile fiyat hedefi olasılık hesaplaması (`future-price.py`).
*   **Veri Analizi:** İşlem geçmişi (CSV/Excel) yükleme ve analiz etme.
*   **Veritabanı:** `db.py` üzerinden SQLite ile yerel kayıt (Analiz geçmişi, simülasyonlar, portföy durumu).
*   **Simülasyon:** "What-If" senaryo analizleri ve kaydırıcı (slider) ile dinamik hesaplama.
*   **Responsive:** Streamlit `use_container_width` ayarları ile mobil tarayıcılarda düzgün görüntüleme.

---

## 🗺️ Faz 1: Backend API ve Mikroservis Dönüşümü (Ay 1-2)

Kod tabanı modüler hale getirilmiştir (`services/` klasörü). Bir sonraki adım, bu servisleri bir API arkasında sunmaktır.

### 1. Backend API Geliştirme (⏳ Sırada)
*   **Hedef:** `services/` altındaki Python sınıflarını FastAPI veya Flask framework'ü ile dışa açmak.
*   **Yapılacaklar:**
    *   [ ] `PortfolioService` ve `DecisionSupportAI` sınıfları için REST API endpoint'lerinin yazılması.
    *   [ ] `future-price.py` içindeki ML modelinin (`predict_probability`) bir API endpoint'i olarak sunulması.
    *   [ ] JWT (JSON Web Token) ile temel kimlik doğrulama katmanının eklenmesi.

### 2. Veritabanı Migrasyonu (⚠️ Planlanıyor)
*   **Mevcut:** Tek kullanıcılı SQLite (`futurewallet.db`).
*   **Hedef:** Çok kullanıcılı PostgreSQL veya Firebase Firestore.
*   **Yapılacaklar:**
    *   [ ] SQLite verilerinin şema yapısının analizi ve yeni veritabanına aktarımı.
    *   [ ] Kullanıcı tablosu ve oturum yönetimi eklenmesi.

## 📱 Faz 2: Mobil Uygulama Geliştirme (Ay 3-5)

API hazır olduktan sonra, mobil uygulama geliştirme süreci başlayacaktır.

### Teknoloji Seçenekleri
*   **Cross-Platform (Önerilen):** Flutter (Dart) veya React Native.
*   **Avantajı:** Tek kod tabanı, hızlı geliştirme.

### Mobil UI/UX Özellikleri
*   **Hızlı Erişim:** Biyometrik Giriş (FaceID/TouchID).
*   **AI Vision:** Kamera ile finansal belge/ekran görüntüsü tarama.
*   **Offline Mod:** Son görüntülenen verilerin önbelleğe alınması.
*   **Bildirimler:** Fiyat alarmleri ve AI günlük özetleri.

## 🚀 Faz 3: Test ve Yayınlama (Ay 6)

1.  **Testler:** Unit Testler (Backend) ve UI Testleri.
2.  **CI/CD:** GitHub Actions ile otomatik build.
3.  **Market:** App Store ve Google Play yayın süreçleri.

## ✅ Özet Kontrol Listesi

### Tamamlanan
- [x] Temel Cüzdan Takibi ve Karşılaştırmalı Grafikler (BTC, Altın, S&P 500).
- [x] Google Gemini AI Entegrasyonu (Dinamik Model Seçimi).
- [x] XGBoost ile Olasılık Hesaplayıcısı (Machine Learning).
- [x] CSV/Excel İşlem Geçmişi Analizi.
- [x] SQLite ile Veri Kalıcılığı (Analiz ve Simülasyon Geçmişi).
- [x] Environment Variable Yönetimi (`.env` ve Sidebar Fallback).
- [x] Mobil Uyumlu UI Ayarları (Streamlit `use_container_width`).
- [x] **Kod Tabanı Refactoring (Services & Views Ayrıştırması).**

### Yapılacaklar (Mobil Dönüşüm)
- [ ] Backend API projesinin oluşturulması (FastAPI).
- [ ] Veritabanının çoklu kullanıcı yapısına geçirilmesi.
- [ ] Mobil UI tasarımının (Figma) yapılması.
- [ ] MVP Mobil Uygulama kodlamasının başlaması.
