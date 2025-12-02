import streamlit as st
import ccxt
import pandas as pd
import yfinance as yf
import google.generativeai as genai
from datetime import datetime, timedelta
import db

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FutureWallet Ultimate", page_icon="💎", layout="wide")
db.init_db()

st.title("💎 FutureWallet: Geçmiş Analiz & Gelecek Simülasyonu")

# --- 1. FONKSİYONLAR ---
@st.cache_data(ttl=300)
def get_gemini_models(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return models
    except:
        return []

@st.cache_data(ttl=3600)
def get_benchmark_data(start_date, btc_amount, initial_usd):
    """Geçmiş performans grafiği verilerini hazırlar"""
    tickers = {'Bitcoin': 'BTC-USD', 'Altın (Ons)': 'GC=F', 'S&P 500': '^GSPC'}
    df_list = []
    
    for name, ticker in tickers.items():
        try:
            data = yf.download(ticker, start=start_date, progress=False)['Close']
            if isinstance(data, pd.DataFrame): data = data.iloc[:, 0]
            
            if not data.empty:
                first_price = data.iloc[0]
                normalized = ((data / first_price) - 1) * 100
                df_temp = pd.DataFrame(normalized)
                df_temp.columns = [name]
                df_list.append(df_temp)
        except:
            pass

    if df_list:
        df_combined = pd.concat(df_list, axis=1).ffill()
        days = len(df_combined)
        daily_inf = (1.035**(1/365)) - 1
        inf_series = [((1 + daily_inf)**i - 1) * 100 for i in range(days)]
        if len(inf_series) > len(df_combined): inf_series = inf_series[:len(df_combined)]
        df_combined['ABD Enflasyonu'] = inf_series
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

# --- 2. SOL PANEL: CÜZDAN & MODEL GİRİŞİ ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    # --- A. API & MODEL SEÇİMİ (GÜNCELLENDİ) ---
    api_key = st.text_input("Gemini API Key:", type="password", help="Google AI Studio'dan aldığınız anahtar.")
    
    # Model Listesi
    default_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    if api_key:
        fetched_models = get_gemini_models(api_key)
        available_models = fetched_models if fetched_models else default_models

        # Key varsa seçim kutusunu aktif et
        selected_model_name = st.selectbox("Yapay Zeka Modeli:", available_models, index=0)
        st.success(f"Model: {selected_model_name} aktif")
    else:
        # Key yoksa kutuyu pasif yap (disabled=True)
        st.selectbox("Yapay Zeka Modeli:", ["Önce API Key Giriniz 🔒"], disabled=True)
        selected_model_name = None

    st.divider()

    # --- B. CÜZDAN YÖNETİMİ ---
    st.header("Cüzdan Yönetimi")
    saved_btc, saved_usdt, saved_initial, saved_date_str = db.get_portfolio()
    try:
        start_date_obj = datetime.strptime(saved_date_str, "%Y-%m-%d").date()
    except:
        start_date_obj = datetime.now().date() - timedelta(days=365)

    with st.form("portfolio_update"):
        st.markdown("### 💰 Mevcut Varlıklar")
        new_btc = st.number_input("BTC Miktarı:", value=saved_btc, format="%.5f")
        new_usdt = st.number_input("Nakit ($):", value=saved_usdt)
        
        st.markdown("### 📅 Başlangıç Bilgileri")
        new_initial = st.number_input("Yatırılan Ana Para ($):", value=saved_initial)
        new_date = st.date_input("Başlangıç Tarihi:", value=start_date_obj)
        
        if st.form_submit_button("💾 Güncelle ve Kaydet"):
            db.update_portfolio(new_btc, new_usdt, new_initial, str(new_date))
            st.toast("Cüzdan başarıyla güncellendi!", icon="✅")
            st.rerun()

# --- 3. ÜST BİLGİ PANELİ (SCORECARD) ---
current_price = get_current_btc_price()
real_value = (saved_btc * current_price) + saved_usdt
profit = real_value - saved_initial
roi = (profit / saved_initial) * 100 if saved_initial > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mevcut Toplam Varlık", f"${real_value:,.0f}")
col2.metric("Toplam Kar/Zarar", f"${profit:,.0f}", delta=f"%{roi:.1f}")
col3.metric("Ana Para", f"${saved_initial:,.0f}")
col4.metric("Canlı BTC Fiyatı", f"${current_price:,.0f}")

st.divider()

# --- 4. SEKMELİ YAPI (Tabs) ---
tab_past, tab_future, tab_history = st.tabs(["📊 Geçmiş Performans", "🔮 Gelecek Simülasyonu", "📜 Kayıtlı Analizler"])

# --- TAB 1: GEÇMİŞ GRAFİĞİ ---
with tab_past:
    st.subheader("Yatırımınız vs Piyasa")
    if saved_initial > 0:
        with st.spinner("Piyasa verileri getiriliyor..."):
            chart_data = get_benchmark_data(str(start_date_obj), saved_btc, saved_initial)
        if not chart_data.empty:
            # Kullanıcı Seçimi
            all_options = ['Bitcoin', 'Altın (Ons)', 'S&P 500', 'ABD Enflasyonu']
            selected_options = st.multiselect(
                "Grafikte Gösterilecek Veriler:",
                options=all_options,
                default=all_options
            )

            valid_selections = [col for col in selected_options if col in chart_data.columns]

            if valid_selections:
                st.line_chart(chart_data[valid_selections], height=400)
            else:
                st.warning("Görüntülenecek veri seçilmedi.")
            
            # Grafik Yorumlatma Butonu (Tab 1 İçin)
            if st.button("Grafiği Yorumla 🧠", key="btn_chart_ai"):
                if not api_key or not selected_model_name:
                    st.error("Lütfen sol menüden API Key giriniz.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(selected_model_name) # SEÇİLEN MODEL BURADA KULLANILIYOR
                        
                        last_vals = chart_data.iloc[-1].to_dict()
                        context = f"""
                        YATIRIM PERFORMANSI RAPORU:
                        Tarih Aralığı: {saved_date_str} - Bugün
                        
                        GETİRİLER (%):
                        {last_vals}
                        
                        GÖREV:
                        Seçilen yapay zeka modeli ({selected_model_name}) olarak, kullanıcının performansını kıyasla.
                        """
                        with st.spinner(f'{selected_model_name} düşünüyor...'):
                            resp = model.generate_content(context)
                            st.info(resp.text)
                    except Exception as e:
                        st.error(f"Hata: {e}")

        else:
            st.warning("Grafik verisi yok.")
    else:
        st.info("Grafik için ana para girişi yapınız.")

# --- TAB 2: GELECEK SİMÜLASYONU (FutureWallet) ---
with tab_future:
    st.subheader("What-If: Senaryo Analizi")
    
    col_sim_input, col_sim_result = st.columns([1, 1])
    
    with col_sim_input:
        st.markdown("#### Hedef Fiyatı Belirle")
        simulated_price = st.slider(
            "Bitcoin ($) kaç olursa?",
            min_value=int(current_price * 0.5),
            max_value=int(current_price * 3.0),
            value=int(current_price),
            step=500
        )
        st.info(f"Senaryo Fiyatı: **${simulated_price:,.0f}**")

    sim_total = (saved_btc * simulated_price) + saved_usdt
    sim_diff = sim_total - real_value
    
    with col_sim_result:
        st.markdown("#### Cüzdan Tahmini")
        st.metric("Tahmini Toplam Varlık", f"${sim_total:,.2f}", delta=f"{sim_diff:+,.2f} $")
    
    st.divider()
    
    # AI Yorum ve Kaydetme
    st.markdown(f"### 🧠 AI Danışman ({selected_model_name if selected_model_name else 'Devre Dışı'})")
    
    if st.button("Senaryoyu Analiz Et ve Kaydet 📝", key="btn_sim_ai"):
        if not api_key or not selected_model_name:
            st.error("Lütfen sol menüden API Key giriniz.")
        else:
            try:
                genai.configure(api_key=api_key)
                # KULLANICININ SEÇTİĞİ MODELİ YÜKLÜYORUZ
                model = genai.GenerativeModel(selected_model_name)
                
                context = f"""
                DURUM:
                - Başlangıç: {saved_date_str}, Para: {saved_initial}$
                - Şu an: {real_value}$
                
                SENARYO:
                - Beklenti: BTC {simulated_price}$ olacak.
                - Sonuç Cüzdan: {sim_total}$ olacak.
                
                GÖREV:
                Kısa, net ve esprili bir yatırım tavsiyesi (YTD) ver.
                """
                
                with st.spinner(f'{selected_model_name} senaryoyu simüle ediyor...'):
                    response = model.generate_content(context).text
                    st.success(response)
                    db.save_simulation(current_price, simulated_price, sim_total, response)
                    st.toast("Kayıt Başarılı!", icon="💾")
                    
            except Exception as e:
                st.error(f"Hata: {e}")

# --- TAB 3: GEÇMİŞ TABLOSU ---
with tab_history:
    st.subheader("Geçmiş Analizler")
    df_history = db.get_history()
    if not df_history.empty:
        st.dataframe(
            df_history[['sim_date', 'simulated_price', 'total_value', 'ai_comment']],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Kayıt yok.")
