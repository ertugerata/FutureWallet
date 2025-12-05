import streamlit as st
import pandas as pd
import db

def render_analysis_view():
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
                    # Limit sample size
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
