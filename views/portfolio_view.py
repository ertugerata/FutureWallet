import streamlit as st
import db
from services.portfolio_service import PortfolioService
from services.ai_service import DecisionSupportAI

def render_portfolio_view(api_key: str):
    st.subheader("Bütünleşik Portföy Yönetimi (BIST, Kripto, Emtia)")

    # Access session state variables
    saved_btc = st.session_state.get('saved_btc', 0.0)
    saved_usdt = st.session_state.get('saved_usdt', 0.0)

    # Initialize PortfolioService if needed (though app.py should handle high level init)
    # Ideally, we pass the service instance, but for now we can instantiate or use session state
    if 'portfolio_service' not in st.session_state:
        st.session_state.portfolio_service = PortfolioService(st.session_state.asset_manager)

    portfolio_service = st.session_state.portfolio_service

    if 'extra_assets' not in st.session_state:
        st.session_state.extra_assets = []

    # Get Snapshot
    snapshot = portfolio_service.get_portfolio_snapshot(saved_btc, saved_usdt, st.session_state.extra_assets)
    full_portfolio = snapshot['portfolio']
    total_port_val = snapshot['total_value']

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
                result = portfolio_service.validate_and_add_asset(symbol_input, asset_type, amount_input)
                if result:
                    st.session_state.extra_assets.append({
                        'symbol': result['symbol'],
                        'type': result['type'],
                        'amount': result['amount']
                    })
                    st.success(f"{result['symbol']} eklendi. Fiyat: {result['price']}")
                    st.rerun()
                else:
                    st.error(f"{symbol_input} fiyatı bulunamadı.")

        # Portföy Listesi
        st.markdown("#### Portföy Varlıkları")

        # Tablo gösterimi
        disp_data = []
        for k, v in full_portfolio.items():
            disp_data.append({
                'Varlık': k,
                'Tip': v['type'],
                'Miktar': v['amount'],
                'Değer ($)': f"${v['value']:,.2f}"
            })

        st.table(disp_data)
        st.metric("Toplam Portföy Değeri", f"${total_port_val:,.2f}")

        if st.session_state.extra_assets:
            if st.button("Listeyi Temizle"):
                st.session_state.extra_assets = []
                st.rerun()

    with col_ai_advice:
        st.markdown("#### 🧠 AI Karar Destek")

        if not api_key:
            st.warning("Analiz için API Key giriniz.")
        else:
            risk_choice = st.select_slider("Risk Profiliniz:", options=["conservative", "moderate", "aggressive"])

            if st.button("Portföyümü Analiz Et 🚀"):
                if 'decision_ai' in st.session_state:
                    ai = st.session_state.decision_ai

                    context = {
                        'portfolio': full_portfolio,
                        'market_condition': 'Belirsiz (Veri akışı bekleniyor)',
                        'user_question': f"Risk profilim {risk_choice}. Bu portföy uygun mu? Ne yapmalıyım?"
                    }

                    with st.spinner("AI Portföy Yöneticisi Düşünüyor..."):
                        rec = ai.get_ai_recommendation(context)
                        st.markdown(rec)
                        db.save_analysis("Portföy Analizi", str(full_portfolio), rec)
