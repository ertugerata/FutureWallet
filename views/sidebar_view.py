import streamlit as st
import os
import db
from datetime import datetime, timedelta
from services.ai_service import get_gemini_models, DecisionSupportAI

def render_sidebar():
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
            # Note: Caching is good, but calling service directly here.
            # In a real app we might want to wrap this in app.py or here with st.cache_data
            # But the service function itself is pure.
            # We can use a local wrapper for caching.
            @st.cache_data(ttl=300)
            def cached_get_models(key):
                return get_gemini_models(key)

            fetched_models = cached_get_models(api_key)
            available_models = fetched_models if fetched_models else default_models
            selected_model_name = st.selectbox("Yapay Zeka Modeli:", available_models, index=0)

            # AI Motorunu Başlat
            if 'decision_ai' not in st.session_state:
                st.session_state.decision_ai = DecisionSupportAI(api_key, selected_model_name)
            else:
                # Basic check if we need to re-init (if model changed)
                if st.session_state.decision_ai.model.model_name.split('/')[-1] != selected_model_name:
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

        # Store in session state for other views to access without re-querying DB immediately
        st.session_state.saved_btc = saved_btc
        st.session_state.saved_usdt = saved_usdt
        st.session_state.saved_initial = saved_initial
        st.session_state.start_date_obj = start_date_obj

        with st.form("portfolio_update"):
            new_btc = st.number_input("BTC Miktarı:", value=saved_btc, format="%.5f")
            new_usdt = st.number_input("Nakit ($):", value=saved_usdt)
            new_initial = st.number_input("Yatırılan Ana Para ($):", value=saved_initial)
            new_date = st.date_input("Başlangıç Tarihi:", value=start_date_obj)

            if st.form_submit_button("💾 Güncelle"):
                db.update_portfolio(new_btc, new_usdt, new_initial, str(new_date))
                st.toast("Cüzdan güncellendi!", icon="✅")
                # Update session state immediately
                st.session_state.saved_btc = new_btc
                st.session_state.saved_usdt = new_usdt
                st.session_state.saved_initial = new_initial
                st.session_state.start_date_obj = new_date
                st.rerun()

        return api_key
