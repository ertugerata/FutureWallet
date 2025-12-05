from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv
import os
import importlib
import sys

# Add the parent directory to sys.path to allow imports from services and root
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Imports from your services
from services.portfolio_service import PortfolioService
from services.ai_service import DecisionSupportAI

# Need to make sure the root directory is in python path to import future_price
# which is in the root directory
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Explicitly append /app to ensure absolute path import works in this environment
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

try:
    import future_price as fp
except ImportError as e:
    print(f"Error importing future_price: {e}")
    fp = None

# Pass verbose=True or stream to avoid assertion error in some envs
try:
    load_dotenv(verbose=True)
except AssertionError:
    # Fallback for environments where find_dotenv fails
    pass

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# In a real production app, use a secure secret key and store it in env vars
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

jwt = JWTManager(app)

# Initialize Services
# Note: Services might need instantiation per request or globally depending on statefulness.
# PortfolioService and DecisionSupportAI seem stateless or depend on args, so global is fine for now.
# However, DecisionSupportAI needs an API key.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ai_service = None
if GOOGLE_API_KEY:
    ai_service = DecisionSupportAI(api_key=GOOGLE_API_KEY)

portfolio_service = PortfolioService()


# --- AUTHENTICATION ENDPOINTS ---

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Simple mock login to get a JWT.
    In production, verify username/password against DB.
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Mock User Check
    if username != 'admin' or password != 'password':
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# --- PORTFOLIO ENDPOINTS ---

@app.route('/api/portfolio/calculate', methods=['POST'])
@jwt_required()
def calculate_portfolio():
    """
    Calculates portfolio value based on provided holdings.
    """
    data = request.json
    holdings = data.get('holdings') # Expected dict structure

    if not holdings:
         return jsonify({"msg": "Missing holdings data"}), 400

    # The service expects a specific format.
    # Let's assume the client sends what AssetManager.calculate_portfolio_value expects.
    # holdings: {'BTC': {'type': 'crypto', 'amount': 0.5}, ...}

    try:
        result = portfolio_service.manager.calculate_portfolio_value(holdings)
        return jsonify(result)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/api/portfolio/benchmark', methods=['POST'])
@jwt_required()
def benchmark_portfolio():
    """
    Returns benchmark chart data.
    """
    data = request.json
    btc_amount = data.get('btc_amount', 0)
    usdt_amount = data.get('usdt_amount', 0)
    initial_usd = data.get('initial_usd', 0)
    days = data.get('days', 365)
    start_date_str = data.get('start_date', '') # Not used in service currently but in signature

    try:
        df = portfolio_service.get_benchmark_chart_data(
            btc_amount=btc_amount,
            usdt_amount=usdt_amount,
            initial_usd=initial_usd,
            start_date_str=start_date_str,
            days=days
        )
        # Convert DataFrame to JSON friendly format (records)
        return jsonify(df.reset_index().to_dict(orient='records'))
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# --- ML ENDPOINT ---

@app.route('/api/ml/predict', methods=['POST'])
@jwt_required()
def predict_probability():
    """
    Exposes the XGBoost prediction model.
    """
    data = request.json
    symbol = data.get('symbol', 'BTC-USD')
    target_price = data.get('target_price', 100000)
    days = data.get('days', 10)

    try:
        result = fp.predict_probability(symbol, target_price, days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

# --- AI ENDPOINTS ---

@app.route('/api/ai/analyze', methods=['POST'])
@jwt_required()
def analyze_portfolio():
    """
    Analyze portfolio risk using DecisionSupportAI.
    """
    if not ai_service:
        return jsonify({"msg": "AI Service not initialized (Missing API Key)"}), 503

    data = request.json
    portfolio = data.get('portfolio')

    if not portfolio:
         return jsonify({"msg": "Missing portfolio data"}), 400

    try:
        result = ai_service.analyze_portfolio_risk(portfolio)
        return jsonify(result)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

@app.route('/api/ai/recommendation', methods=['POST'])
@jwt_required()
def get_recommendation():
    """
    Get generic AI recommendation.
    """
    if not ai_service:
        return jsonify({"msg": "AI Service not initialized (Missing API Key)"}), 503

    data = request.json
    context = data.get('context') # Expected dict

    if not context:
        return jsonify({"msg": "Missing context"}), 400

    try:
        recommendation = ai_service.get_ai_recommendation(context)
        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
