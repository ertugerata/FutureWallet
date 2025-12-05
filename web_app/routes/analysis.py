from flask import Blueprint, render_template, request, flash, current_app
from services.ai_service import DecisionSupportAI, get_gemini_models
import os

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis', methods=['GET', 'POST'])
def analysis():
    response_text = None
    models = []
    selected_model = 'gemini-1.5-flash'

    # Init AI Service
    api_key = current_app.config.get('GOOGLE_API_KEY')

    # Try to get models if key exists
    if api_key:
        try:
            models = get_gemini_models(api_key)
        except:
            models = ['gemini-pro', 'gemini-1.5-flash'] # Fallback

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        selected_model = request.form.get('model')

        if not api_key:
            response_text = "Hata: Google API Key tanımlanmamış. Lütfen çevre değişkenlerini kontrol edin."
        else:
            try:
                ai = DecisionSupportAI(api_key=api_key, model_name=selected_model)
                response_text = ai.analyze_general(user_input)
            except Exception as e:
                response_text = f"Bir hata oluştu: {str(e)}"

    return render_template('analysis.html',
                           response=response_text,
                           models=models,
                           selected_model=selected_model,
                           api_key_present=bool(api_key))
