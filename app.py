import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json

# Sayfa Ayarları
st.set_page_config(page_title="FutureWallet MVP", page_icon="💰")

# Başlık
st.title("💰 FutureWallet: BTC Simülatörü")
st.markdown("Gerçek verilerle 'What-If' senaryolarını test et.")

# --- 1. VERİ ÇEKME (CoinGecko API) ---
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

# --- 2. KULLANICI GİRİŞLERİ (Sol Panel) ---
with st.sidebar:
    st.header("Varlıklarım")
    # Varsayılan olarak sizin belirttiğiniz 0.01415 BTC'yi koydum
    btc_amount = st.number_input(
        "Elimdeki BTC Miktarı:", 
        value=0.01415, 
        step=0.0001, 
        format="%.5f"
    )

    usdt_cash = st.number_input(
        "Elimdeki Nakit (USDT):",
        value=789.58,
        step=10.0
    )

# --- 3. SİMÜLASYON ALANI ---
st.subheader("🔮 Gelecek Senaryosu")

# Slider ayarları: Şu anki fiyatın yarısı ile 2.5 katı arasında
step_size = 1000
min_val = int(current_price * 0.5)
min_val = (min_val // step_size) * step_size  # Step'e yuvarla
max_val = int(current_price * 2.5)
max_val = ((max_val // step_size) + 1) * step_size  # Step'e yuvarla
default_val = (int(current_price) // step_size) * step_size  # Step'e yuvarla

# Slider'ı oluştur
simulated_price = st.slider(
    "Bitcoin Fiyatı ($) ne olursa?",
    min_value=min_val,
    max_value=max_val,
    value=default_val,
    step=step_size
)

# --- 4. HESAPLAMALAR ---
# Şu anki gerçek durum
real_value = (btc_amount * current_price) + usdt_cash

# Simülasyon durumu (Nakit sabit kalır, BTC değeri değişir)
simulated_value = (btc_amount * simulated_price) + usdt_cash

# Fark (Kar/Zarar)
diff = simulated_value - real_value

# --- 5. GÖRSELLEŞTİRME ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Güncel BTC Fiyatı", value=f"${current_price:,.2f}")

with col2:
    st.metric(label="Mevcut Toplam Varlık", value=f"${real_value:,.2f}")

with col3:
    st.metric(
        label="Senaryo Sonucu", 
        value=f"${simulated_value:,.2f}", 
        delta=f"{diff:+,.2f} $" # Renkli değişim göstergesi
    )

# Ekstra: Grafiksel Gösterim
st.divider()
st.caption("Fiyat Değişimine Göre Varlık Eğrisi")

# Grafik için veri seti oluşturma
if min_val > 0 and max_val > min_val:
    price_range = list(range(min_val, max_val + 1, max(1, (max_val - min_val) // 50)))
    asset_values = [(p * btc_amount) + usdt_cash for p in price_range]
    chart_df = pd.DataFrame({
        'BTC Fiyatı ($)': price_range,
        'Toplam Varlık ($)': asset_values
    })
    st.line_chart(chart_df, x='BTC Fiyatı ($)', y='Toplam Varlık ($)')
else:
    st.info("Grafik için fiyat verisi bekleniyor...")