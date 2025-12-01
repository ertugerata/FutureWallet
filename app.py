import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json
import google.generativeai as genai

# Sayfa Ayarları (from app_new.py)
st.set_page_config(page_title="FutureWallet AI", page_icon="🤖")

# Başlık (from app_new.py)
st.title("🤖 FutureWallet: AI Finansal Asistan")
st.markdown("Verilerini simüle et, yapay zeka risklerini analiz etsin.")

# --- 1. VERİ ÇEKME (CoinGecko API from app.py) ---
# app_new.py was using Binance (ccxt), but we need CoinGecko due to regional restrictions.
@st.cache_data(ttl=30)
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data['bitcoin']['usd']
    except Exception as e:
        return None

current_price = get_btc_price()

if current_price is None or current_price == 0:
    st.warning("⚠️ Fiyat alınamadı. Varsayılan fiyat kullanılıyor.")
    current_price = 100000.0

# --- 2. SIDEBAR / AYARLAR (Combined) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    # API Key from app_new.py
    api_key = st.text_input("Google Gemini API Key:", type="password")

    st.divider()

    st.header("💰 Varlıklarım")
    # Values from app_new.py / app.py (they matched)
    btc_amount = st.number_input("Elimdeki BTC:", value=0.01415, step=0.0001, format="%.5f")
    usdt_cash = st.number_input("Elimdeki Nakit ($):", value=789.58, step=10.0)

# --- 3. SİMÜLASYON VE HESAPLAMALAR (Combined) ---
st.subheader("🔮 Senaryo Analizi")

# Logic from app.py was slightly more robust with min/max calc,
# but app_new.py was cleaner. Let's adapt app_new.py's slider structure
# but ensure ranges make sense like in app.py if needed.

# Slider logic from app_new.py:
simulated_price = st.slider(
    "Bitcoin Fiyatı ($) ne olursa?",
    min_value=int(current_price * 0.5),
    max_value=int(current_price * 2.0),
    value=int(current_price),
    step=500
)

# Hesaplamalar
real_total = (btc_amount * current_price) + usdt_cash
sim_total = (btc_amount * simulated_price) + usdt_cash
kar_zarar = sim_total - real_total
degisim_yuzdesi = (kar_zarar / real_total) * 100 if real_total > 0 else 0

# --- 4. GÖRSELLEŞTİRME (Combined) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Güncel BTC Fiyatı", value=f"${current_price:,.2f}")

with col2:
    st.metric(label="Mevcut Toplam Varlık", value=f"${real_total:,.2f}")

with col3:
    st.metric(
        label="Senaryo Sonucu", 
        value=f"${sim_total:,.2f}",
        delta=f"{kar_zarar:+,.2f} $"
    )

# Grafik (From app.py - preserved as it adds value)
st.divider()
st.caption("Fiyat Değişimine Göre Varlık Eğrisi")

min_val = int(current_price * 0.5)
max_val = int(current_price * 2.0)

if min_val > 0 and max_val > min_val:
    price_range = list(range(min_val, max_val + 1, max(1, (max_val - min_val) // 50)))
    asset_values = [(p * btc_amount) + usdt_cash for p in price_range]
    chart_df = pd.DataFrame({
        'BTC Fiyatı ($)': price_range,
        'Toplam Varlık ($)': asset_values
    })
    st.line_chart(chart_df, x='BTC Fiyatı ($)', y='Toplam Varlık ($)')

# --- 5. YAPAY ZEKA ENTEGRASYONU (From app_new.py) ---
st.divider()
st.subheader("🧠 Yapay Zeka Görüşü")

if st.button("Bu Senaryoyu Yorumla 🚀"):
    if not api_key:
        st.warning("Lütfen sol menüden Gemini API Key giriniz.")
    else:
        try:
            # 1. Modeli Yapılandır
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')

            # 2. Bağlamı (Context) Hazırla
            context_text = f"""
            Kullanıcı Profili: Bireysel Yatırımcı
            Mevcut Durum:
            - Nakit: {usdt_cash} $
            - BTC Miktarı: {btc_amount} BTC
            - Şu anki BTC Fiyatı: {current_price} $

            Simüle Edilen Senaryo:
            - Kullanıcı BTC fiyatının {simulated_price} $ olmasını bekliyor.
            - Bu durumda portföyü {real_total:.2f} $'dan {sim_total:.2f} $'a çıkacak.
            - Değişim: %{degisim_yuzdesi:.2f}

            GÖREVİN:
            Sen tecrübeli, gerçekçi ve biraz da esprili bir finansal danışmansın.
            Bu senaryonun gerçekleşme ihtimali ve riskleri hakkında kısa, 3 maddelik bir yorum yap.
            Yatırım tavsiyesi vermeden, risk yönetimi (kâr al veya stop-loss) üzerine odaklan.
            """

            # 3. AI'dan Cevap İste
            with st.spinner('Piyasalar analiz ediliyor...'):
                response = model.generate_content(context_text)
                st.success("Analiz Tamamlandı!")
                st.write(response.text)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
