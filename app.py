import streamlit as st
import ccxt
import pandas as pd
import yfinance as yf
import google.generativeai as genai
from datetime import datetime, timedelta
import db

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FutureWallet Pro", page_icon="📈", layout="wide")
db.init_db()

st.title("📈 FutureWallet: Karşılaştırmalı Analiz")

# --- 1. VERİ MOTORU (YENİ) ---
@st.cache_data(ttl=3600) # 1 saat cache'le
def get_benchmark_data(start_date, btc_amount, initial_usd):
    """
    Başlangıç tarihinden bugüne kadar:
    1. Bitcoin
    2. Altın (GC=F)
    3. S&P 500 (^GSPC)
    verilerini çeker ve kümülatif getiriye çevirir.
    """
    # Yahoo Finance Sembolleri
    tickers = {
        'Bitcoin': 'BTC-USD',
        'Altın (Ons)': 'GC=F',
        'S&P 500': '^GSPC'
    }
    
    # Verileri toplu çek
    df_list = []
    for name, ticker in tickers.items():
        try:
            # Veriyi indir
            data = yf.download(ticker, start=start_date, progress=False)['Close']
            
            # Eğer veri MultiIndex dönerse (yeni yfinance sürümlerinde) düzelt
            if isinstance(data, pd.DataFrame):
                data = data.iloc[:, 0]
                
            # Normalizasyon: Başlangıç gününü 0 kabul et, yüzdelik değişimi bul
            # Formül: ((Fiyat / Başlangıç_Fiyatı) - 1) * 100
            first_price = data.iloc[0]
            normalized = ((data / first_price) - 1) * 100
            
            # Seriyi DataFrame'e çevir
            df_temp = pd.DataFrame(normalized)
            df_temp.columns = [name]
            df_list.append(df_temp)
            
        except Exception as e:
            st.error(f"{name} verisi çekilemedi: {e}")

    # Tüm verileri tarih bazında birleştir
    if df_list:
        df_combined = pd.concat(df_list, axis=1)
        
        # Eksik verileri doldur (Hafta sonu borsa kapalıdır ama Kripto açıktır)
        df_combined = df_combined.ffill() 
        
        # Enflasyon Çizgisi (Simülasyon: Yıllık %3.5 Dolar Enflasyonu)
        # Günlük enflasyon etkisi: (1.035)^(1/365)
        days = len(df_combined)
        daily_inflation = (1.035**(1/365)) - 1
        inflation_series = [( (1 + daily_inflation)**i - 1 ) * 100 for i in range(days)]
        
        # Tarih indeksine göre eşleşmesi için seriyi kes veya uydur
        if len(inflation_series) > len(df_combined):
            inflation_series = inflation_series[:len(df_combined)]
            
        df_combined['ABD Enflasyonu'] = inflation_series
        
        return df_combined
    return pd.DataFrame()

@st.cache_data(ttl=10)
def get_current_btc_price():
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        return ticker['last']
    except:
        return 95000

# --- 2. SIDEBAR & DB ---
with st.sidebar:
    st.header("⚙️ Portföy")
    saved_btc, saved_usdt, saved_initial, saved_date_str = db.get_portfolio()
    
    # Tarih formatını güvenli hale getir
    try:
        start_date_obj = datetime.strptime(saved_date_str, "%Y-%m-%d").date()
    except:
        start_date_obj = datetime.now().date() - timedelta(days=365) # Varsayılan 1 yıl önce

    with st.form("settings"):
        api_key = st.text_input("Gemini API Key:", type="password")
        st.info(f"Başlangıç: {saved_date_str}")
        
        new_btc = st.number_input("BTC Miktarı:", value=saved_btc, format="%.5f")
        new_usdt = st.number_input("Nakit ($):", value=saved_usdt)
        new_initial = st.number_input("Ana Para ($):", value=saved_initial)
        new_date = st.date_input("Başlangıç Tarihi:", value=start_date_obj)
        
        if st.form_submit_button("Güncelle ve Hesapla"):
            db.update_portfolio(new_btc, new_usdt, new_initial, str(new_date))
            st.rerun()

# --- 3. ANA EKRAN METRİKLERİ ---
current_price = get_current_btc_price()
real_value = (saved_btc * current_price) + saved_usdt
profit = real_value - saved_initial
roi = (profit / saved_initial) * 100 if saved_initial > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Toplam Varlık", f"${real_value:,.0f}")
col2.metric("Net Kar/Zarar", f"${profit:,.0f}", delta=f"%{roi:.1f}")
col3.metric("BTC Fiyatı", f"${current_price:,.0f}")

st.divider()

# --- 4. GRAFİK VE ANALİZ (YENİ BÖLÜM) ---
st.subheader(f"📊 Performans Karşılaştırması ({saved_date_str}'den beri)")

# Grafik Verilerini Getir
if saved_initial > 0:
    with st.spinner("Piyasa verileri indiriliyor (Altın, S&P 500)..."):
        chart_data = get_benchmark_data(str(start_date_obj), saved_btc, saved_initial)
    
    if not chart_data.empty:
        # 1. Grafik Gösterimi
        st.line_chart(chart_data, height=400)
        
        # 2. Sonuç Özeti
        last_values = chart_data.iloc[-1]
        
        # En iyi ve en kötü performansı bul
        best_asset = last_values.idxmax()
        best_return = last_values.max()
        
        st.markdown(f"""
        > 🏆 **Dönemin Kazananı:** **{best_asset}** (%{best_return:.1f} getiri ile).
        > Sizin Bitcoin stratejinizin getirisi: **%{last_values['Bitcoin']:.1f}**.
        """)
        
        # --- 5. AI YORUMU ---
        if st.button("Bu Tabloyu Yorumla 🧠"):
            if not api_key:
                st.error("API Key gerekli.")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                context = f"""
                Sen bir portföy analistisin.
                
                Kullanıcı {saved_date_str} tarihinden beri yatırım yapıyor.
                
                PERFORMANS KARŞILAŞTIRMASI (Yüzdesel Getiriler):
                - Bitcoin (Kullanıcı): %{last_values.get('Bitcoin', 0):.2f}
                - Altın: %{last_values.get('Altın (Ons)', 0):.2f}
                - S&P 500: %{last_values.get('S&P 500', 0):.2f}
                - ABD Enflasyonu: %{last_values.get('ABD Enflasyonu', 0):.2f}
                
                GÖREV:
                Kullanıcının performansını diğer araçlarla kıyasla. Enflasyona karşı durumunu söyle.
                Eğer Altın veya Borsa daha çok kazandırdıysa, "Çeşitlendirme yapabilirdin" gibi yapıcı bir eleştiri getir.
                """
                
                with st.spinner("Yapay zeka grafiği okuyor..."):
                    resp = model.generate_content(context)
                    st.info(resp.text)
                    
                    # Sonucu DB'ye kaydet
                    db.save_simulation(current_price, 0, real_value, resp.text)
    else:
        st.warning("Grafik verisi oluşturulamadı. Tarih çok yeni veya piyasa verisi çekilemedi.")
