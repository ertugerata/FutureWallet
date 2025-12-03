# 📱 FutureWallet Mobil Uygulama Yol Haritası (Roadmap)

Bu belge, FutureWallet projesinin mevcut Streamlit prototipinden tam teşekküllü bir mobil uygulamaya dönüşüm sürecini planlamaktadır.

## 🗺️ Faz 1: Hazırlık ve Backend Ayrıştırması (Ay 1-2)

Mevcut Streamlit uygulaması "monolitik" bir yapıdadır (Frontend ve Backend iç içe). Mobil uygulama için Backend servisinin ayrılması gerekmektedir.

1.  **Backend API Geliştirme:**
    *   Python (FastAPI veya Flask) kullanarak RESTful API oluşturulması.
    *   Şu anki `app.py` içindeki fonksiyonların (`get_benchmark_data`, `get_current_btc_price` vb.) API endpointlerine dönüştürülmesi.
    *   *Örnek Endpointler:*
        *   `GET /api/market/btc-price`
        *   `POST /api/portfolio/update`
        *   `POST /api/ai/analyze` (Gemini entegrasyonu burada olacak)

2.  **Veritabanı Migrasyonu:**
    *   Mevcut SQLite (`db.py`) yapısının, çoklu kullanıcı desteği için PostgreSQL veya Firebase Firestore gibi bir yapıya taşınması.
    *   Kullanıcı kimlik doğrulama (Authentication) altyapısının kurulması (OAuth2, JWT).

## 📱 Faz 2: Mobil Uygulama Geliştirme (Ay 3-5)

Kullanıcı kitlesine ve bütçeye göre teknoloji seçimi yapılacaktır.

### Seçenek A: Cross-Platform (Önerilen)
*   **Teknoloji:** Flutter (Dart) veya React Native (JS/TS).
*   **Avantajı:** Tek kod tabanı ile hem iOS hem Android çıktısı.
*   **UI Framework:** Material Design (Flutter) veya NativeBase (React Native).

### Seçenek B: Native
*   **Teknoloji:** Swift (iOS) ve Kotlin (Android).
*   **Avantajı:** En yüksek performans.
*   **Dezavantajı:** İki ayrı kod tabanı, yüksek maliyet.

**Mobil UI/UX Özellikleri:**
*   Hızlı açılış ve Biyometrik Giriş (FaceID/TouchID).
*   Push Bildirimleri (Fiyat alarmları için).
*   Offline Mod (Son görüntülenen verilerin önbelleğe alınması).
*   Responsive Grafikler (Mobile-first kütüphaneler kullanımı).

## 🚀 Faz 3: Test ve Yayınlama (Ay 6)

1.  **Testler:**
    *   Unit Testler (Backend).
    *   UI Testleri (Mobil Simülatörler).
    *   Beta Testi (TestFlight & Google Play Console).
2.  **CI/CD Pipeline:**
    *   GitHub Actions ile otomatik build ve test süreçleri.
    *   Docker ile backend deploy süreçleri.
3.  **Market Yayını:**
    *   App Store ve Play Store onay süreçleri.

## ✅ Özet Kontrol Listesi

- [ ] Backend API projesinin oluşturulması (FastAPI).
- [ ] Veritabanı şemasının tasarlanması.
- [ ] Mobil UI tasarımının (Figma/Adobe XD) yapılması.
- [ ] MVP Mobil Uygulama kodlamasının başlaması.
- [ ] Gemini AI entegrasyonunun API üzerinden sunulması.
