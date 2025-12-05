from flask import Blueprint, render_template, request
import future_price

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation', methods=['GET', 'POST'])
def simulation():
    result = None
    target_price = 0.0
    current_price = 0.0

    # We can get the current price for default
    try:
        from multi_asset_manager import AssetManager
        am = AssetManager()
        current_price = am.get_price('BTC', 'crypto') or 50000.0
    except:
        current_price = 50000.0

    if request.method == 'POST':
        target_price = float(request.form.get('target_price'))
        current_price_input = float(request.form.get('current_price'))

        # Calculate Probability
        prob = future_price.predict_probability(current_price_input, target_price)

        result = {
            'probability': prob * 100,
            'target': target_price,
            'current': current_price_input
        }
        current_price = current_price_input # Keep user input

    return render_template('simulation.html', result=result, current_price=current_price)
