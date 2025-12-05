import streamlit as st
import db

def render_history_view():
    st.subheader("Geçmiş Analizler")
    df_analyses = db.get_analyses()
    if not df_analyses.empty:
        for i, row in df_analyses.iterrows():
            with st.expander(f"{row['created_at']} - {row['analysis_type']}"):
                st.write(row['ai_response'])
                if st.button("Sil", key=f"del_{row['id']}"):
                    db.delete_analysis(row['id'])
                    st.rerun()
