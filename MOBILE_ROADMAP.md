# 📱 FutureWallet Mobil Uygulama Yol Haritası (Roadmap)

Bu belge, **FutureWallet** projesinin mevcut Streamlit prototipinden tam teşekküllü bir mobil uygulamaya dönüşüm sürecini planlamaktadır.

## 📊 Mevcut Durum (Streamlit Prototipi)

Şu anki kod tabanı (`app.py`), aşağıdaki özelliklerle çalışan kararlı bir prototiptir ve mobil dönüşüm için gerekli iş mantığını barındırmaktadır:
*   **Yapay Zeka:** Google Gemini 1.5 Flash/Pro entegrasyonu (Model seçimi, Chat analizi).
*   **Veri Analizi:** İşlem geçmişi (CSV/Excel) yükleme ve analiz etme.
*   **Veritabanı:** `db.py` üzerinden SQLite ile yerel kayıt (Analiz geçmişi, simülasyonlar, portföy durumu).
*   **Simülasyon:** "What-If" senaryo analizleri ve kaydırıcı (slider) ile dinamik hesaplama.
*   **Responsive:** Streamlit `use_container_width` ayarları ile mobil tarayıcılarda düzgün görüntüleme.

---

## 🗺️ Faz 1: Hazırlık ve Backend Ayrıştırması (Ay 1-2)

Mevcut "monolitik" yapı (Streamlit) API tabanlı bir mimariye dönüştürülecektir.

### 1. Backend API Geliştirme (⏳ Beklemede)
*   **Hedef:** `app.py` içindeki iş mantığını (Business Logic) FastAPI veya Flask servisine taşımak.
*   **Yapılacaklar:**
    *   [ ] `get_benchmark_data` (Yahoo Finance) ve `get_current_btc_price` (CCXT) fonksiyonlarının servise taşınması.
    *   [ ] Gemini AI entegrasyonunun (`get_gemini_models`, prompt yönetimi) API endpoint'ine çevrilmesi.
    *   [ ] CSV analiz mantığının (`tab_analysis`) backend servisine taşınması ve validasyon katmanı eklenmesi.

### 2. Veritabanı Migrasyonu (⚠️ Planlanıyor)
*   **Mevcut:** Tek kullanıcılı SQLite (`futurewallet.db`).
*   **Hedef:** Çok kullanıcılı PostgreSQL veya Firebase Firestore.
*   **Yapılacaklar:**
    *   [ ] SQLite verilerinin şema yapısının analizi.
    *   [ ] Kullanıcı kimlik doğrulama (Auth) tablolarının eklenmesi.
    *   [ ] API üzerinden veritabanı erişim katmanının (ORM) yazılması.

## 📱 Faz 2: Mobil Uygulama Geliştirme (Ay 3-5)

Kullanıcı kitlesine ve bütçeye göre teknoloji seçimi yapılacaktır.

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

### Tamamlanan (Prototip Aşamasında)
- [x] Temel Cüzdan Takibi ve Karşılaştırmalı Grafikler (BTC, Altın, S&P 500).
- [x] Google Gemini AI Entegrasyonu (Dinamik Model Seçimi).
- [x] CSV/Excel İşlem Geçmişi Analizi.
- [x] SQLite ile Veri Kalıcılığı (Analiz ve Simülasyon Geçmişi).
- [x] Environment Variable Yönetimi (`.env` ve Sidebar Fallback).
- [x] Mobil Uyumlu UI Ayarları (Streamlit `use_container_width`).

### Yapılacaklar (Mobil Dönüşüm)
- [ ] Backend API projesinin oluşturulması (FastAPI).
- [ ] Veritabanının çoklu kullanıcı yapısına geçirilmesi.
- [ ] Mobil UI tasarımının (Figma) yapılması.
- [ ] MVP Mobil Uygulama kodlamasının başlaması.
