import streamlit as st
import db
from services.portfolio_service import PortfolioService

def render_performance_view():
    st.subheader("Yatırımınız vs Piyasa")

    saved_initial = st.session_state.get('saved_initial', 0.0)
    saved_btc = st.session_state.get('saved_btc', 0.0)
    saved_usdt = st.session_state.get('saved_usdt', 0.0)
    start_date_obj = st.session_state.get('start_date_obj')

    if saved_initial > 0:
        if 'portfolio_service' not in st.session_state:
            st.session_state.portfolio_service = PortfolioService(st.session_state.asset_manager)

        portfolio_service = st.session_state.portfolio_service

        with st.spinner("Veriler güncelleniyor..."):
            chart_data = portfolio_service.get_benchmark_chart_data(
                saved_btc, saved_usdt, saved_initial, str(start_date_obj)
            )

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
