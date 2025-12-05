"""
Portfolio Management Service
Handles portfolio calculations, data fetching, and benchmark comparisons.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from multi_asset_manager import AssetManager

class PortfolioService:
    def __init__(self, asset_manager: Optional[AssetManager] = None):
        self.manager = asset_manager if asset_manager else AssetManager()

    def get_benchmark_chart_data(self, btc_amount: float, usdt_amount: float,
                                 initial_usd: float, start_date_str: str,
                                 days: int = 365) -> pd.DataFrame:
        """
        Prepares historical performance chart data using AssetManager.
        Replaces logic previously in app.py's get_benchmark_chart_data.
        """
        # Comparison assets
        comparison_assets = [
            {'symbol': 'BTC', 'type': 'crypto'},       # Bitcoin
            {'symbol': 'GC=F', 'type': 'commodity'},   # Gold
            {'symbol': '^GSPC', 'type': 'stock_us'}    # S&P 500
        ]

        # Fetch data
        df_combined = self.manager.compare_performance(comparison_assets, days=days)

        # Rename columns (Symbol -> Readable Name)
        rename_map = {'BTC': 'Bitcoin', 'GC=F': 'Altın (Ons)', '^GSPC': 'S&P 500'}
        df_combined.rename(columns=rename_map, inplace=True)

        # Calculate Wallet Performance (Simulated)
        if 'Bitcoin' in df_combined.columns and initial_usd > 0:
            # Re-fetch BTC history to ensure alignment and accuracy
            btc_hist = self.manager.get_historical_data('BTC', 'crypto', days=days)

            if not btc_hist.empty:
                btc_prices = btc_hist['Close']
                if isinstance(btc_prices, pd.DataFrame):
                    btc_prices = btc_prices.iloc[:, 0]

                # Align indices
                common_idx = df_combined.index.intersection(btc_prices.index)
                btc_prices = btc_prices.loc[common_idx]

                wallet_values = (btc_prices * btc_amount) + usdt_amount
                wallet_normalized = ((wallet_values / initial_usd) - 1) * 100

                df_combined.loc[common_idx, 'Cüzdanım'] = wallet_normalized

        # Inflation Curve
        num_days = len(df_combined)
        if num_days > 0:
            daily_inf = (1.035**(1/365)) - 1
            inf_series = [((1 + daily_inf)**i - 1) * 100 for i in range(num_days)]
            # Align with dataframe index
            df_combined['ABD Enflasyonu'] = pd.Series(inf_series, index=df_combined.index).ffill()

        return df_combined

    def get_portfolio_snapshot(self, saved_btc: float, saved_usdt: float,
                              extra_assets: List[Dict]) -> Dict:
        """
        Returns a complete snapshot of the portfolio including current values.
        """
        # Get BTC price
        current_btc_price = self.manager.get_price('BTC', 'crypto')
        if current_btc_price is None:
            current_btc_price = 0.0

        # Base Portfolio
        full_portfolio = {
            'BTC (Cüzdan)': {'type': 'crypto', 'amount': saved_btc, 'value': saved_btc * current_btc_price},
            'Nakit (USDT)': {'type': 'cash', 'amount': saved_usdt, 'value': saved_usdt}
        }

        total_val = (saved_btc * current_btc_price) + saved_usdt

        # Extra Assets
        for asset in extra_assets:
            p = self.manager.get_price(asset['symbol'], asset['type'])
            if p:
                val = p * asset['amount']
                full_portfolio[asset['symbol']] = {
                    'type': asset['type'],
                    'amount': asset['amount'],
                    'value': val
                }
                total_val += val

        return {
            'portfolio': full_portfolio,
            'total_value': total_val,
            'btc_price': current_btc_price
        }

    def validate_and_add_asset(self, symbol: str, asset_type: str, amount: float) -> Optional[Dict]:
        """
        Validates asset existence and returns the asset object if valid.
        """
        test_price = self.manager.get_price(symbol, asset_type)
        if test_price:
            return {
                'symbol': symbol,
                'type': asset_type,
                'amount': amount,
                'price': test_price
            }
        return None
