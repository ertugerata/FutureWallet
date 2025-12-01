import streamlit as st
import ccxt
import pandas as pd
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="FutureWallet AI", page_icon="🤖")

st.title("🤖 FutureWallet: AI Finansal Asistan")
st.markdown("Verilerini simüle et, yapay zeka risklerini analiz etsin.")

# --- 1. AYARLAR VE API KEY (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    # Kullanıcıdan API Key alma (Güvenlik için şifreli giriş)
    api_key = st.text_input("Google Gemini API Key:", type="password")
    
    st.divider()
    
    st.header("💰 Varlıklarım")
    btc_amount = st.number_input("Elimdeki BTC:", value=0.01415, step=0.0001, format="%.5f")
    usdt_cash = st.number_input("Elimdeki Nakit ($):", value=789.58, step=10.0)

# --- 2. VERİ ÇEKME ---
@st.cache_data(ttl=10)
def get_btc_price():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return ticker['last']
    except:
        return 95000 # Hata olursa varsayılan değer

current_price = get_btc_price()

# --- 3. SİMÜLASYON ---
st.subheader("Senaryo Analizi")
col_sim, col_res = st.columns([2, 1])

with col_sim:
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

with col_res:
    st.metric("Tahmini Toplam Varlık", f"${sim_total:,.2f}", delta=f"{kar_zarar:+,.2f} $")

# --- 4. YAPAY ZEKA ENTEGRASYONU (RAG / Context Injection) ---
st.divider()
st.subheader("🧠 Yapay Zeka Görüşü")

if st.button("Bu Senaryoyu Yorumla 🚀"):
    if not api_key:
        st.warning("Lütfen sol menüden Gemini API Key giriniz.")
    else:
        try:
            # 1. Modeli Yapılandır
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            # 2. Bağlamı (Context) Hazırla
            # Burası RAG'in "Context" kısmıdır. Sayısal veriyi metne döküyoruz.
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
