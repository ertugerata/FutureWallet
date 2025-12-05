import streamlit as st
import importlib
import db
import pandas as pd

def render_future_simulation_view(current_btc_price, saved_btc, saved_usdt, real_value):
    """
    Renders the unified Future Simulation and Probability Calculation view.
    """
    st.header("🔮 Gelecek Simülasyonu ve Olasılıklar")
    st.markdown("Bu alanda hem manuel fiyat senaryolarını test edebilir hem de yapay zeka destekli olasılık hesaplamaları yapabilirsiniz.")

    # --- UNIFIED INPUT SECTION ---
    st.subheader("🛠️ Fiyat ve Olasılık Analizi")
    st.info("Aşağıdaki kaydırıcıyı kullanarak belirlediğiniz hedef fiyat, hem portföy simülasyonunda hem de olasılık hesaplamasında kullanılacaktır.")

    if 'sim_price' not in st.session_state:
        st.session_state.sim_price = int(current_btc_price) if current_btc_price > 0 else 50000

    # Unified Slider and Input Synchronization
    target_price = st.slider("Bitcoin Hedef / Senaryo Fiyatı ($)",
                        min_value=int(current_btc_price * 0.1) if current_btc_price > 0 else 1000,
                        max_value=int(current_btc_price * 5) if current_btc_price > 0 else 200000,
                        value=st.session_state.sim_price, step=500, key="sim_slider")
    st.session_state.sim_price = target_price


    # Layout: Two columns, one for manual simulation, one for probability
    col_sim, col_prob = st.columns([1, 1], gap="medium")

    # --- PART 1: MANUAL SIMULATION RESULTS ---
    with col_sim:
        st.markdown("#### 📊 Portföy Simülasyonu")

        # Calculate Simulation Results using the unified target_price
        sim_total = (saved_btc * target_price) + saved_usdt
        sim_diff = sim_total - real_value

        st.metric("Tahmini Toplam Varlık", f"${sim_total:,.2f}", delta=f"{sim_diff:+,.2f} $")

        # Store for AI
        st.session_state.sim_result = {
            "sim_price": target_price,
            "sim_total": sim_total,
            "sim_diff": sim_diff
        }

    # --- PART 2: PROBABILITY CALCULATION (XGBoost) ---
    with col_prob:
        st.markdown("#### 🎲 Olasılık Analizi")
        st.caption(f"Hedef Fiyat: ${target_price:,.2f}") # Display the target price being analyzed

        days_pred = st.slider("Vade (Gün)", 1, 90, 30, key="prob_days")

        prob_result = None
        if st.button("Olasılık Hesapla 🚀"):
            try:
                # Dynamic import to avoid top-level issues and allow hot-reloading logic if needed
                future_price = importlib.import_module("future-price")
                importlib.reload(future_price)

                with st.spinner("Model geçmiş verileri analiz ediyor..."):
                    prob_result = future_price.predict_probability("BTC-USD", target_price, days_pred)

                if prob_result and prob_result["success"]:
                    st.metric("Gerçekleşme İhtimali", f"%{prob_result['probability']*100:.1f}")
                    st.success(f"Analiz Başarılı: {prob_result['message']}")

                    # Store result in session state for the combined AI analysis
                    # Ensure input parameters are included in the result for AI context
                    prob_result['target_price'] = target_price
                    prob_result['days'] = days_pred
                    st.session_state.prob_result = prob_result

                    with st.expander("Model Detayları (Feature Importance)"):
                        st.bar_chart(prob_result["feature_importances"])
                else:
                    st.error(prob_result["message"] if prob_result else "Bilinmeyen hata")

            except Exception as e:
                st.error(f"Modül hatası: {e}")

    st.divider()

    # --- PART 3: COMBINED AI INTERPRETATION ---
    st.subheader("🧠 Yapay Zeka Yorumu")
    st.markdown("Simülasyon sonuçlarını ve olasılık verilerini birleştirerek yapay zekadan yorum alın.")

    if st.button("Senaryoyu Yorumla ve Kaydet 💾", key="btn_sim_ai"):
        if 'decision_ai' in st.session_state:
            ai = st.session_state.decision_ai

            # Prepare Context
            sim_data = st.session_state.get('sim_result', {})
            prob_data = st.session_state.get('prob_result', None)

            context_str = f"""
            KULLANICI SENARYOSU:
            - Mevcut BTC Fiyatı: ${current_btc_price:,.2f}
            - Simüle Edilen BTC Fiyatı (Hedef): ${sim_data.get('sim_price', 0):,.2f}
            - Bu senaryoda Portföy Değeri: ${sim_data.get('sim_total', 0):,.2f} (Fark: ${sim_data.get('sim_diff', 0):,.2f})
            """

            if prob_data:
                # Check if the probability calculation matches the current simulation price.
                # If the user changed the slider but didn't click "Calculate Probability" again, the data might be stale.
                # We can add a note about this or just display what was calculated.
                calc_target = prob_data.get('target_price', 0)
                current_target = sim_data.get('sim_price', 0)

                context_str += f"""

                MAKİNE ÖĞRENMESİ (XGBoost) ANALİZİ:
                - Analiz Edilen Hedef Fiyat: ${calc_target:,.2f}
                - Vade: {prob_data.get('days', 0)} gün
                - Gerçekleşme Olasılığı: %{prob_data.get('probability', 0)*100:.1f}
                - Model Doğruluğu: {prob_data.get('accuracy', 0):.2f}
                """

                if calc_target != current_target:
                    context_str += f"\n(UYARI: Kullanıcı şu an simülasyonu ${current_target} için yapıyor ancak olasılık hesabı önceki ${calc_target} değeri için yapılmış.)"
            else:
                context_str += "\nNot: Kullanıcı henüz olasılık hesaplaması yapmadı."

            context = {
                'portfolio': context_str,
                'user_question': "Bu senaryoyu ve (varsa) olasılık hesaplamasını yorumla. Bu hedef mantıklı mı? Riskler neler?"
            }

            with st.spinner("AI Senaryoyu Analiz Ediyor..."):
                resp = ai.get_ai_recommendation(context)
                st.markdown(resp)

                # Save to DB
                # We use the generic 'save_analysis' function.
                # Title: "Gelecek Simülasyonu"
                # Input Summary: A brief summary of the simulation parameters
                summary = f"Sim: ${sim_data.get('sim_price', 0)} | "
                if prob_data:
                    summary += f"Prob: ${prob_data.get('target_price', 0)} (%{prob_data.get('probability', 0)*100:.0f})"

                db.save_analysis("Gelecek Simülasyonu", summary, resp)
                st.success("Analiz veritabanına kaydedildi.")
        else:
            st.warning("AI Modeli yüklü değil. Lütfen sol panelden API anahtarınızı girin.")
