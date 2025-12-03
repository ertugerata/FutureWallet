import streamlit as st
import ccxt
import pandas as pd
import yfinance as yf
import google.generativeai as genai
from datetime import datetime, timedelta
import db
import os
from dotenv import load_dotenv

# --- 12-FACTOR: CONFIG (Environment Variables) ---
load_dotenv()

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
def get_benchmark_data(start_date, btc_amount, usdt_amount, initial_usd):
    """Geçmiş performans grafiği verilerini hazırlar"""
    tickers = {'Bitcoin': 'BTC-USD', 'Altın (Ons)': 'GC=F', 'S&P 500': '^GSPC'}
    df_list = []
    
    # Ham verileri tutacak sözlük
    raw_data = {}

    for name, ticker in tickers.items():
        try:
            data = yf.download(ticker, start=start_date, progress=False)['Close']
            if isinstance(data, pd.DataFrame): data = data.iloc[:, 0]
            
            if not data.empty:
                raw_data[name] = data
                first_price = data.iloc[0]
                normalized = ((data / first_price) - 1) * 100
                df_temp = pd.DataFrame(normalized)
                df_temp.columns = [name]
                df_list.append(df_temp)
        except:
            pass

    # Cüzdan Hesabı (Eğer Bitcoin verisi varsa)
    if 'Bitcoin' in raw_data and initial_usd > 0:
        btc_prices = raw_data['Bitcoin']
        # Tarihsel cüzdan değeri = (O günkü BTC Fiyatı * Şimdiki BTC Adedi) + Şimdiki Nakit
        wallet_values = (btc_prices * btc_amount) + usdt_amount

        # Normalize et (Kar/Zarar %)
        wallet_normalized = ((wallet_values / initial_usd) - 1) * 100
        df_wallet = pd.DataFrame(wallet_normalized)
        df_wallet.columns = ['Cüzdanım']
        df_list.append(df_wallet)

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
        return None

# --- 2. SOL PANEL: CÜZDAN & MODEL GİRİŞİ ---
with st.sidebar:
    st.header("⚙️ Ayarlar")

    # --- FİYAT VERİSİ (MANUEL / OTOMATİK) ---
    st.subheader("💰 Fiyat Ayarları")
    use_manual_price = st.checkbox("Manuel BTC Fiyatı Kullan")

    fetched_price = get_current_btc_price()

    # Fiyat belirleme mantığı
    if use_manual_price or fetched_price is None:
        if fetched_price is None and not use_manual_price:
            st.warning("⚠️ Fiyat verisi çekilemedi (Ağ hatası). Lütfen manuel giriniz.")

        current_price = st.number_input(
            "Güncel BTC Fiyatı ($):",
            value=95000.0,
            step=100.0,
            format="%.2f"
        )
    else:
        st.success(f"Borsa Fiyatı: ${fetched_price:,.2f}")
        current_price = fetched_price

    st.divider()
    
    # --- A. API & MODEL SEÇİMİ (GÜNCELLENDİ) ---
    # 12-FACTOR: Config (Env Var support with UI override)
    env_api_key = os.getenv("GOOGLE_API_KEY")
    api_key = st.text_input(
        "Gemini API Key:",
        value=env_api_key if env_api_key else "",
        type="password",
        help="Google AI Studio'dan aldığınız anahtar. (.env dosyasında GOOGLE_API_KEY tanımlanabilir)"
    )
    
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
# current_price sidebar'da tanımlandı
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
tab_past, tab_future, tab_analysis, tab_history = st.tabs(["📊 Geçmiş Performans", "🔮 Gelecek Simülasyonu", "📈 İşlem Analizi", "📜 Kayıtlı Analizler"])

# --- TAB 1: GEÇMİŞ GRAFİĞİ ---
with tab_past:
    st.subheader("Yatırımınız vs Piyasa")
    if saved_initial > 0:
        with st.spinner("Piyasa verileri getiriliyor..."):
            chart_data = get_benchmark_data(str(start_date_obj), saved_btc, saved_usdt, saved_initial)
        if not chart_data.empty:
            # Kullanıcı Seçimi
            all_options = ['Cüzdanım', 'Bitcoin', 'Altın (Ons)', 'S&P 500', 'ABD Enflasyonu']
            selected_options = st.multiselect(
                "Grafikte Gösterilecek Veriler:",
                options=all_options,
                default=all_options
            )

            valid_selections = [col for col in selected_options if col in chart_data.columns]

            if valid_selections:
                st.line_chart(chart_data[valid_selections], height=400, use_container_width=True)
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
                        Seçilen yapay zeka modeli ({selected_model_name}) olarak, "Cüzdanım" performansını;
                        Enflasyon, S&P 500 ve Altın ile karşılaştırarak değerlendir.
                        Cüzdanın durumunu diğer yatırım araçlarına göre analiz et.
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

        # Session state başlatma ve güncelleme kontrolü
        if 'sim_price' not in st.session_state:
            st.session_state.sim_price = int(current_price)
            st.session_state.last_base_price = current_price

        # Eğer güncel fiyat değiştiyse (örneğin manuel giriş ile), simülasyonu da resetle
        if 'last_base_price' in st.session_state and st.session_state.last_base_price != current_price:
             st.session_state.sim_price = int(current_price)
             st.session_state.last_base_price = current_price

        def update_slider():
            st.session_state.sim_price = st.session_state.slider_key

        def update_input():
            st.session_state.sim_price = int(st.session_state.input_key)

        min_p = int(current_price * 0.1) # Geniş aralık
        max_p = int(current_price * 5.0)

        # Değerin sınırlar içinde kaldığından emin ol
        if st.session_state.sim_price < min_p: st.session_state.sim_price = min_p
        if st.session_state.sim_price > max_p: st.session_state.sim_price = max_p

        # Slider
        st.slider(
            "Bitcoin ($) kaç olursa? (Slider)",
            min_value=min_p,
            max_value=max_p,
            value=st.session_state.sim_price,
            step=500,
            key='slider_key',
            on_change=update_slider
        )

        # Number Input
        st.number_input(
            "Bitcoin ($) kaç olursa? (Manuel)",
            min_value=min_p,
            max_value=max_p,
            value=st.session_state.sim_price,
            step=500,
            key='input_key',
            on_change=update_input
        )

        simulated_price = st.session_state.sim_price
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

# --- TAB 3: İŞLEM ANALİZİ (YENİ) ---
with tab_analysis:
    st.subheader("📁 İşlem Geçmişi Analizi")
    st.info("Borsa veya Excel'den aldığınız işlem geçmişini (CSV/Excel) yükleyin, yapay zeka stratejinizi değerlendirsin.")

    uploaded_file = st.file_uploader("Dosya Yükle (CSV veya Excel)", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            # Dosya uzantısına göre okuma
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_tx = pd.read_csv(uploaded_file)
                    # Tek kolon geldiyse muhtemelen noktalı virgül (Excel CSV) dir
                    if len(df_tx.columns) == 1:
                        uploaded_file.seek(0)
                        df_tx = pd.read_csv(uploaded_file, sep=';')
                except:
                    uploaded_file.seek(0)
                    df_tx = pd.read_csv(uploaded_file, sep=';')
            else:
                # .xls için xlrd, .xlsx için openpyxl otomatik seçilir
                df_tx = pd.read_excel(uploaded_file)

            st.success(f"✅ {len(df_tx)} adet işlem yüklendi.")
            st.dataframe(df_tx.head(10), use_container_width=True) # İlk 10 satırı göster

            st.divider()

            if st.button("Stratejimi Değerlendir 🧠", key="btn_tx_ai"):
                if not api_key or not selected_model_name:
                    st.error("Lütfen sol menüden API Key giriniz.")
                else:
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel(selected_model_name)

                        # Veriyi string'e çevir (Token limitine dikkat etmek gerekebilir, şimdilik basit tutuyoruz)
                        # İlk 50-100 satırı veya özetini göndermek daha güvenli olabilir ama
                        # kullanıcı "belirli bir periyot" dediği için tümünü string olarak deniyoruz.
                        csv_data = df_tx.to_csv(index=False)

                        context = f"""
                        GÖREV:
                        Aşağıdaki işlem geçmişi verisini analiz et ve bu yatırımcının stratejisini değerlendir.

                        ANALİZ EDİLECEK NOKTALAR:
                        1. Kar/Zarar durumu ve kazanma oranı (Win Rate).
                        2. Risk yönetimi (Stop loss kullanılmış mı, giriş çıkışlar mantıklı mı?).
                        3. Varsa sık yapılan hatalar (FOMO, panik satış vb. veriden çıkarılabiliyorsa).
                        4. Genel strateji tavsiyesi ve puanlama (10 üzerinden).

                        VERİ SETİ:
                        {csv_data}

                        NOT: Cevabı Türkçe, profesyonel ama anlaşılır bir dille ver.
                        """

                        with st.spinner(f'{selected_model_name} işlemlerini inceliyor...'):
                            response = model.generate_content(context).text
                            st.markdown("### 🤖 Yapay Zeka Değerlendirmesi")
                            st.write(response)

                    except Exception as e:
                        st.error(f"Hata oluştu: {e}")

        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")


# --- TAB 4: GEÇMİŞ TABLOSU ---
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
