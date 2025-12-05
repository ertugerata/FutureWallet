import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime, timedelta
import db
import os
from dotenv import load_dotenv

# Yeni modüller
from multi_asset_manager import AssetManager
from decision_support_ai import DecisionSupportAI
from views.future_simulation_view import render_future_simulation_view

# --- 12-FACTOR: CONFIG (Environment Variables) ---
load_dotenv()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FutureWallet: Karar Destek", page_icon="💎", layout="wide")
db.init_db()

st.title("💎 FutureWallet: Yatırım Karar Destek Sistemi")

# --- INITIALIZATION ---
# Session State için AssetManager ve AI Engine başlat
if 'asset_manager' not in st.session_state:
    st.session_state.asset_manager = AssetManager()

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
def get_benchmark_chart_data(btc_amount, usdt_amount, initial_usd, start_date_str):
    """
    AssetManager kullanarak geçmiş performans grafiği verilerini hazırlar.
    Eski get_benchmark_data fonksiyonunun yerini alır.
    """
    manager = st.session_state.asset_manager
    
    # Karşılaştırma listesi
    comparison_assets = [
        {'symbol': 'BTC', 'type': 'crypto'},       # Bitcoin
        {'symbol': 'GC=F', 'type': 'commodity'},   # Altın
        {'symbol': '^GSPC', 'type': 'stock_us'}    # S&P 500
    ]

    # Verileri çek
    df_combined = manager.compare_performance(comparison_assets, days=365) # Varsayılan son 1 yıl

    # Kolon isimlerini düzelt (Sembol -> Okunabilir İsim)
    rename_map = {'BTC': 'Bitcoin', 'GC=F': 'Altın (Ons)', '^GSPC': 'S&P 500'}
    df_combined.rename(columns=rename_map, inplace=True)

    # Cüzdan Hesabı (Simüle)
    # Bitcoin verisi varsa cüzdanı hesapla
    if 'Bitcoin' in df_combined.columns and initial_usd > 0:
        # Tekrar veri çekmek yerine df_combined'daki normalize edilmiş veriyi tersine çevirip kullanabiliriz
        # YA DA AssetManager'dan ham fiyatı tekrar isteyebiliriz.
        # Daha sağlıklı olması için AssetManager ile BTC tarihçesini alalım.
        btc_hist = manager.get_historical_data('BTC', 'crypto', days=365)

        if not btc_hist.empty:
            # Tarihleri eşleştir
            btc_prices = btc_hist['Close']
            if isinstance(btc_prices, pd.DataFrame): btc_prices = btc_prices.iloc[:, 0]
            
            # DataFrame indexleri hizala
            common_idx = df_combined.index.intersection(btc_prices.index)
            btc_prices = btc_prices.loc[common_idx]

            wallet_values = (btc_prices * btc_amount) + usdt_amount
            wallet_normalized = ((wallet_values / initial_usd) - 1) * 100

            df_combined.loc[common_idx, 'Cüzdanım'] = wallet_normalized

    # Enflasyon Eğrisi
    days = len(df_combined)
    if days > 0:
        daily_inf = (1.035**(1/365)) - 1
        inf_series = [((1 + daily_inf)**i - 1) * 100 for i in range(days)]
        # Indexe göre ayarla
        df_combined['ABD Enflasyonu'] = pd.Series(inf_series, index=df_combined.index).ffill()

    return df_combined

# --- 2. SOL PANEL: CÜZDAN & MODEL GİRİŞİ ---
with st.sidebar:
    st.header("⚙️ Ayarlar")

    # --- API & MODEL SEÇİMİ ---
    env_api_key = os.getenv("GOOGLE_API_KEY")
    api_key = st.text_input(
        "Gemini API Key:",
        value=env_api_key if env_api_key else "",
        type="password",
        help="Google AI Studio'dan aldığınız anahtar."
    )
    
    default_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    if api_key:
        fetched_models = get_gemini_models(api_key)
        available_models = fetched_models if fetched_models else default_models
        selected_model_name = st.selectbox("Yapay Zeka Modeli:", available_models, index=0)

        # AI Motorunu Başlat
        if 'decision_ai' not in st.session_state:
            st.session_state.decision_ai = DecisionSupportAI(api_key, selected_model_name)
        else:
            # Model değiştiyse güncelle (basitçe yeni instance)
             st.session_state.decision_ai = DecisionSupportAI(api_key, selected_model_name)

        st.success(f"Model: {selected_model_name} aktif")
    else:
        st.selectbox("Yapay Zeka Modeli:", ["Önce API Key Giriniz 🔒"], disabled=True)
        selected_model_name = None

    st.divider()

    # --- CÜZDAN YÖNETİMİ ---
    st.header("Ana Kripto Cüzdanı")
    saved_btc, saved_usdt, saved_initial, saved_date_str = db.get_portfolio()
    try:
        start_date_obj = datetime.strptime(saved_date_str, "%Y-%m-%d").date()
    except:
        start_date_obj = datetime.now().date() - timedelta(days=365)

    with st.form("portfolio_update"):
        new_btc = st.number_input("BTC Miktarı:", value=saved_btc, format="%.5f")
        new_usdt = st.number_input("Nakit ($):", value=saved_usdt)
        new_initial = st.number_input("Yatırılan Ana Para ($):", value=saved_initial)
        new_date = st.date_input("Başlangıç Tarihi:", value=start_date_obj)
        
        if st.form_submit_button("💾 Güncelle"):
            db.update_portfolio(new_btc, new_usdt, new_initial, str(new_date))
            st.toast("Cüzdan güncellendi!", icon="✅")
            st.rerun()

# --- 3. ÜST BİLGİ PANELİ ---
# Canlı fiyatı AssetManager'dan al
try:
    current_btc_price = st.session_state.asset_manager.get_price('BTC', 'crypto')
    if current_btc_price is None: current_btc_price = 0.0
except:
    current_btc_price = 0.0

real_value = (saved_btc * current_btc_price) + saved_usdt
profit = real_value - saved_initial
roi = (profit / saved_initial) * 100 if saved_initial > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mevcut Toplam Varlık", f"${real_value:,.0f}")
col2.metric("Toplam Kar/Zarar", f"${profit:,.0f}", delta=f"%{roi:.1f}")
col3.metric("Ana Para", f"${saved_initial:,.0f}")
col4.metric("Canlı BTC Fiyatı", f"${current_btc_price:,.0f}")

st.divider()

# --- 4. SEKMELİ YAPI ---
tab_portfolio, tab_past, tab_future_sim, tab_analysis, tab_history = st.tabs([
    "💼 Portföy & Karar Destek",
    "📊 Geçmiş Performans",
    "🔮 Gelecek Simülasyonu",
    "📈 İşlem Analizi",
    "📜 Kayıtlar"
])

# --- TAB 1: PORTFÖY & KARAR DESTEK (YENİ - Multi Asset) ---
with tab_portfolio:
    st.subheader("Bütünleşik Portföy Yönetimi (BIST, Kripto, Emtia)")

    # Ana Cüzdanı da dict formatına çevir (Her zaman erişilebilir olması için burada tanımlıyoruz)
    full_portfolio = {
        'BTC (Cüzdan)': {'type': 'crypto', 'amount': saved_btc, 'value': saved_btc * current_btc_price},
        'Nakit (USDT)': {'type': 'cash', 'amount': saved_usdt, 'value': saved_usdt}
    }

    # Session State for extra assets
    if 'extra_assets' not in st.session_state:
        st.session_state.extra_assets = []

    # Ek varlıkları ekle
    if st.session_state.extra_assets:
        for asset in st.session_state.extra_assets:
            p = st.session_state.asset_manager.get_price(asset['symbol'], asset['type'])
            if p:
                val = p * asset['amount']
                full_portfolio[asset['symbol']] = {
                    'type': asset['type'],
                    'amount': asset['amount'],
                    'value': val
                }

    col_assets, col_ai_advice = st.columns([1, 1])

    with col_assets:
        st.markdown("#### Varlık Ekle")

        with st.form("add_asset"):
            c1, c2, c3 = st.columns(3)
            with c1:
                asset_type = st.selectbox("Tür", ["stock_tr", "stock_us", "crypto", "commodity", "forex"],
                                          format_func=lambda x: {
                                              'stock_tr': 'BIST Hisse (TR)',
                                              'stock_us': 'ABD Hisse',
                                              'crypto': 'Kripto Para',
                                              'commodity': 'Emtia (Altın vb.)',
                                              'forex': 'Döviz'
                                          }[x])
            with c2:
                symbol_input = st.text_input("Sembol (Örn: THYAO, AAPL, ETH)", value="THYAO").upper()
            with c3:
                amount_input = st.number_input("Adet/Miktar", min_value=0.0, step=1.0)

            if st.form_submit_button("Ekle"):
                # Fiyat kontrolü yap
                test_price = st.session_state.asset_manager.get_price(symbol_input, asset_type)
                if test_price:
                    st.session_state.extra_assets.append({
                        'symbol': symbol_input,
                        'type': asset_type,
                        'amount': amount_input
                    })
                    st.success(f"{symbol_input} eklendi. Fiyat: {test_price}")
                    st.rerun() # Refresh to show in table
                else:
                    st.error(f"{symbol_input} fiyatı bulunamadı.")

        # Portföy Listesi
        st.markdown("#### Portföy Varlıkları")

        # Tablo gösterimi
        disp_data = []
        total_port_val = 0
        for k, v in full_portfolio.items():
            disp_data.append({
                'Varlık': k,
                'Tip': v['type'],
                'Miktar': v['amount'],
                'Değer ($)': f"${v['value']:,.2f}"
            })
            total_port_val += v['value']

        st.table(disp_data)
        st.metric("Toplam Portföy Değeri", f"${total_port_val:,.2f}")

        if st.session_state.extra_assets:
            # Silme butonu
            if st.button("Listeyi Temizle"):
                st.session_state.extra_assets = []
                st.rerun()

    with col_ai_advice:
        st.markdown("#### 🧠 AI Karar Destek")

        if not api_key:
            st.warning("Analiz için API Key giriniz.")
        else:
            # Risk Profili Seçimi
            risk_choice = st.select_slider("Risk Profiliniz:", options=["conservative", "moderate", "aggressive"])

            if st.button("Portföyümü Analiz Et 🚀"):
                if 'decision_ai' in st.session_state:
                    ai = st.session_state.decision_ai

                    # Analiz için portföy yapısını hazırla
                    # (Yukarıdaki full_portfolio sözlüğünü kullanacağız ama 'returns' verisi olmadan basit analiz)
                    # Daha detaylı analiz için AssetManager'dan return geçmişi çekilebilir.

                    # Basit context
                    context = {
                        'portfolio': full_portfolio,
                        'market_condition': 'Belirsiz (Veri akışı bekleniyor)',
                        'user_question': f"Risk profilim {risk_choice}. Bu portföy uygun mu? Ne yapmalıyım?"
                    }

                    with st.spinner("AI Portföy Yöneticisi Düşünüyor..."):
                        rec = ai.get_ai_recommendation(context)
                        st.markdown(rec)

                        # Kaydet
                        db.save_analysis("Portföy Analizi", str(full_portfolio), rec)

# --- TAB 2: GEÇMİŞ GRAFİĞİ ---
with tab_past:
    st.subheader("Yatırımınız vs Piyasa")
    if saved_initial > 0:
        with st.spinner("Veriler güncelleniyor..."):
            # AssetManager entegrasyonu ile veri çekme
            chart_data = get_benchmark_chart_data(saved_btc, saved_usdt, saved_initial, str(start_date_obj))

        if not chart_data.empty:
            all_options = list(chart_data.columns)
            selected_options = st.multiselect("Grafikte Göster:", options=all_options, default=all_options)
            
            if selected_options:
                st.line_chart(chart_data[selected_options], height=400, use_container_width=True)

            # Grafik Yorumlama
            if st.button("Grafiği Yorumla 🧠", key="btn_chart_ai"):
                if 'decision_ai' in st.session_state:
                    ai = st.session_state.decision_ai
                    last_vals = chart_data.iloc[-1].to_dict()
                    context = {
                        'portfolio': f"Getiriler (%): {last_vals}",
                        'user_question': "Cüzdanım diğer varlıklara göre nasıl performans göstermiş? Enflasyonu yenebilmiş mi?"
                    }
                    with st.spinner("Analiz ediliyor..."):
                        resp = ai.get_ai_recommendation(context)
                        st.info(resp)
                        db.save_analysis("Grafik Yorumu", str(last_vals), resp)
        else:
            st.warning("Veri çekilemedi.")

# --- TAB 3: GELECEK SİMÜLASYONU (MODÜLER) ---
with tab_future_sim:
    render_future_simulation_view(current_btc_price, saved_btc, saved_usdt, real_value)

# --- TAB 4: İŞLEM ANALİZİ ---
with tab_analysis:
    st.subheader("📁 İşlem Geçmişi Analizi")
    uploaded_file = st.file_uploader("CSV/Excel Yükle", type=['csv', 'xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_tx = pd.read_csv(uploaded_file)
            else:
                df_tx = pd.read_excel(uploaded_file)

            st.dataframe(df_tx.head(), use_container_width=True)

            if st.button("İşlemleri Analiz Et 🧠"):
                 if 'decision_ai' in st.session_state:
                    ai = st.session_state.decision_ai
                    csv_sample = df_tx.to_csv(index=False)
                    context = {
                        'portfolio': f"İşlem Geçmişi Verisi (İlk 50 satır): {csv_sample[:2000]}...",
                        'user_question': "Bu yatırımcının işlem stratejisini analiz et. Hataları ve doğruları neler? Puanla."
                    }
                    with st.spinner("İşlemler inceleniyor..."):
                        resp = ai.get_ai_recommendation(context)
                        st.markdown(resp)
                        db.save_analysis("İşlem Dosyası Analizi", uploaded_file.name, resp)
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")

# --- TAB 5: KAYITLAR ---
with tab_history:
    st.subheader("Geçmiş Analizler")
    df_analyses = db.get_analyses()
    if not df_analyses.empty:
        for i, row in df_analyses.iterrows():
            with st.expander(f"{row['created_at']} - {row['analysis_type']}"):
                st.write(row['ai_response'])
                if st.button("Sil", key=f"del_{row['id']}"):
                    db.delete_analysis(row['id'])
                    st.rerun()
