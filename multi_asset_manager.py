"""
Multi-Asset Portfolio Manager
Kripto + Borsa + Emtia + Forex varlıklarını yönetir
"""

import yfinance as yf
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

class AssetManager:
    """Çoklu varlık türünü tek bir arayüzden yönetir"""
    
    ASSET_TYPES = {
        'crypto': {'prefix': '', 'source': 'ccxt'},
        'stock_tr': {'prefix': '.IS', 'source': 'yfinance'},  # BIST
        'stock_us': {'prefix': '', 'source': 'yfinance'},     # NYSE/NASDAQ
        'commodity': {'prefix': '', 'source': 'yfinance'},    # Altın, Petrol
        'forex': {'prefix': '=X', 'source': 'yfinance'}       # Döviz çiftleri
    }
    
    def __init__(self):
        self.exchange = ccxt.binance()
    
    def get_price(self, symbol: str, asset_type: str) -> float:
        """
        Varlık türüne göre güncel fiyat çeker
        
        Args:
            symbol: Varlık sembolü (BTC, THYAO, GOLD vb.)
            asset_type: 'crypto', 'stock_tr', 'commodity' vb.
        
        Returns:
            Güncel fiyat (float)
        """
        try:
            config = self.ASSET_TYPES[asset_type]
            
            if config['source'] == 'ccxt':
                # Kripto için Binance
                ticker = self.exchange.fetch_ticker(f"{symbol}/USDT")
                return ticker['last']
            
            elif config['source'] == 'yfinance':
                # Borsa/Emtia/Forex için Yahoo Finance
                full_symbol = f"{symbol}{config['prefix']}"
                data = yf.download(full_symbol, period="1d", progress=False)
                
                if not data.empty:
                    return float(data['Close'].iloc[-1])
                
            return None
            
        except Exception as e:
            print(f"Fiyat çekme hatası ({symbol}): {e}")
            return None
    
    def get_historical_data(self, symbol: str, asset_type: str, 
                           days: int = 365) -> pd.DataFrame:
        """
        Geçmiş fiyat verisini çeker
        """
        try:
            config = self.ASSET_TYPES[asset_type]
            start_date = datetime.now() - timedelta(days=days)
            
            if config['source'] == 'yfinance':
                full_symbol = f"{symbol}{config['prefix']}"
                data = yf.download(full_symbol, start=start_date, progress=False)
                return data
            
            elif config['source'] == 'ccxt':
                # CCXT için OHLCV verisi
                ohlcv = self.exchange.fetch_ohlcv(
                    f"{symbol}/USDT", 
                    timeframe='1d', 
                    limit=days
                )
                df = pd.DataFrame(
                    ohlcv, 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
                
        except Exception as e:
            print(f"Veri çekme hatası: {e}")
            return pd.DataFrame()
    
    def calculate_portfolio_value(self, holdings: Dict) -> Dict:
        """
        Karışık portföy değerini hesaplar
        
        Args:
            holdings: {
                'BTC': {'type': 'crypto', 'amount': 0.5},
                'THYAO': {'type': 'stock_tr', 'amount': 100},
                'GLD': {'type': 'commodity', 'amount': 50}
            }
        
        Returns:
            Toplam değer ve detaylar
        """
        total_value = 0
        details = {}
        
        for symbol, info in holdings.items():
            price = self.get_price(symbol, info['type'])
            
            if price:
                value = price * info['amount']
                total_value += value
                
                details[symbol] = {
                    'price': price,
                    'amount': info['amount'],
                    'value': value,
                    'type': info['type']
                }
        
        return {
            'total': total_value,
            'assets': details,
            'timestamp': datetime.now()
        }
    
    def compare_performance(self, symbols: List[Dict], 
                           days: int = 365) -> pd.DataFrame:
        """
        Farklı varlık türlerinin performansını karşılaştırır
        
        Args:
            symbols: [
                {'symbol': 'BTC', 'type': 'crypto'},
                {'symbol': 'XU100', 'type': 'stock_tr'},
                {'symbol': 'GC=F', 'type': 'commodity'}
            ]
        
        Returns:
            Normalize edilmiş performans DataFrame'i
        """
        performance = pd.DataFrame()
        
        for item in symbols:
            data = self.get_historical_data(
                item['symbol'], 
                item['type'], 
                days
            )
            
            if not data.empty:
                # Kapanış fiyatlarını normalize et (%0'dan başlasın)
                close_col = 'Close' if 'Close' in data.columns else 'close'
                normalized = ((data[close_col] / data[close_col].iloc[0]) - 1) * 100
                performance[item['symbol']] = normalized
        
        return performance


# Örnek Kullanım
if __name__ == "__main__":
    manager = AssetManager()
    
    # Çoklu portföy
    my_portfolio = {
        'BTC': {'type': 'crypto', 'amount': 0.5},
        'THYAO': {'type': 'stock_tr', 'amount': 100},
        'GC=F': {'type': 'commodity', 'amount': 10},  # Altın (ons)
        'EURUSD': {'type': 'forex', 'amount': 1000}
    }
    
    result = manager.calculate_portfolio_value(my_portfolio)
    print(f"Toplam Portföy Değeri: ${result['total']:,.2f}")
    
    # Karşılaştırmalı performans
    comparison = manager.compare_performance([
        {'symbol': 'BTC', 'type': 'crypto'},
        {'symbol': 'XU100', 'type': 'stock_tr'},
        {'symbol': 'GC=F', 'type': 'commodity'}
    ], days=365)
    
    print("\nYıllık Performans:")
    print(comparison.tail())
