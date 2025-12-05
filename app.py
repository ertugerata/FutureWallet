import streamlit as st
from dotenv import load_dotenv
import db

# Services
from multi_asset_manager import AssetManager

# Views
from views.sidebar_view import render_sidebar
from views.portfolio_view import render_portfolio_view
from views.performance_view import render_performance_view
from views.future_simulation_view import render_future_simulation_view
from views.analysis_view import render_analysis_view
from views.history_view import render_history_view

# --- 12-FACTOR: CONFIG (Environment Variables) ---
load_dotenv()

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="FutureWallet: Karar Destek", page_icon="💎", layout="wide")
db.init_db()

st.title("💎 FutureWallet: Yatırım Karar Destek Sistemi")

# --- INITIALIZATION ---
if 'asset_manager' not in st.session_state:
    st.session_state.asset_manager = AssetManager()

# --- RENDER SIDEBAR ---
api_key = render_sidebar()

# --- ÜST BİLGİ PANELİ (Header Stats) ---
# Retrieve values from session state (set by sidebar)
saved_btc = st.session_state.get('saved_btc', 0.0)
saved_usdt = st.session_state.get('saved_usdt', 0.0)
saved_initial = st.session_state.get('saved_initial', 0.0)

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

# --- SEKMELİ YAPI ---
tab_portfolio, tab_past, tab_future_sim, tab_analysis, tab_history = st.tabs([
    "💼 Portföy & Karar Destek",
    "📊 Geçmiş Performans",
    "🔮 Gelecek Simülasyonu",
    "📈 İşlem Analizi",
    "📜 Kayıtlar"
])

# --- RENDER TABS ---
with tab_portfolio:
    render_portfolio_view(api_key)

with tab_past:
    render_performance_view()

with tab_future_sim:
    render_future_simulation_view(current_btc_price, saved_btc, saved_usdt, real_value)

with tab_analysis:
    render_analysis_view()

with tab_history:
    render_history_view()
