from flask import Blueprint, render_template, request
import plotly.express as px
import plotly.io as pio
from services.portfolio_service import PortfolioService
import pandas as pd

main_bp = Blueprint('main', __name__)
portfolio_service = PortfolioService()

@main_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    # Default values (simulating what was in Streamlit session state or defaults)
    initial_investment = 1000.0
    btc_amount = 0.015
    usdt_amount = 500.0

    # In a real app, these would come from a database or user session
    # For now, we'll allow basic inputs via a simple form on top or defaults

    if request.method == 'POST':
        try:
            initial_investment = float(request.form.get('initial_investment', 1000.0))
            btc_amount = float(request.form.get('btc_amount', 0.015))
            usdt_amount = float(request.form.get('usdt_amount', 500.0))
        except ValueError:
            pass # Keep defaults on error

    # Fetch Data
    # Note: Using hardcoded start date for now as per original app logic usually defaulting to 1 year
    start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y-%m-%d')

    df = portfolio_service.get_benchmark_chart_data(
        btc_amount=btc_amount,
        usdt_amount=usdt_amount,
        initial_usd=initial_investment,
        start_date_str=start_date,
        days=365
    )

    # Generate Chart
    fig = px.line(df, x=df.index, y=df.columns, title='Portföy Performansı vs Benchmarklar')
    fig.update_layout(yaxis_title='Değişim (%)', xaxis_title='Tarih', template='plotly_white')

    chart_html = pio.to_html(fig, full_html=False)

    # Get Snapshot
    snapshot = portfolio_service.get_portfolio_snapshot(btc_amount, usdt_amount, [])

    return render_template('dashboard.html',
                           chart_html=chart_html,
                           snapshot=snapshot,
                           initial_investment=initial_investment,
                           btc_amount=btc_amount,
                           usdt_amount=usdt_amount)
