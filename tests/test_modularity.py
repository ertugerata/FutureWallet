
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Add root directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.portfolio_service import PortfolioService
from services.ai_service import DecisionSupportAI, get_gemini_models

class TestModularity(unittest.TestCase):
    def setUp(self):
        # Mock AssetManager to avoid external API calls
        self.mock_asset_manager = MagicMock()
        self.portfolio_service = PortfolioService(asset_manager=self.mock_asset_manager)

    def test_portfolio_service_snapshot(self):
        """Test that get_portfolio_snapshot returns correct structure without UI dependency."""
        self.mock_asset_manager.get_price.return_value = 50000.0

        snapshot = self.portfolio_service.get_portfolio_snapshot(
            saved_btc=1.0,
            saved_usdt=1000.0,
            extra_assets=[{'symbol': 'ETH', 'type': 'crypto', 'amount': 10}]
        )

        self.assertIn('portfolio', snapshot)
        self.assertIn('total_value', snapshot)
        self.assertEqual(snapshot['btc_price'], 50000.0)
        # 1 BTC * 50k + 1000 USDT + 10 ETH * 50k (mock price) = 51000 + 500000 = 551000
        self.assertEqual(snapshot['total_value'], 551000.0)

    def test_ai_service_structure(self):
        """Test AI service methods exist and return expected types."""
        ai = DecisionSupportAI(api_key="test_key")
        # Mock the generator
        ai.model.generate_content = MagicMock(return_value=MagicMock(text="AI Response"))

        response = ai.get_ai_recommendation({})
        self.assertEqual(response, "AI Response")

        # Test risk analysis (pure logic)
        portfolio = {
            'BTC': {'type': 'crypto', 'value': 100, 'returns': [0.1, -0.1]},
            'GOLD': {'type': 'commodity', 'value': 100, 'returns': [0.01, 0.02]}
        }
        risk = ai.analyze_portfolio_risk(portfolio)
        self.assertIn('detected_profile', risk)

    @patch('google.generativeai.list_models')
    def test_get_gemini_models(self, mock_list_models):
        """Test model listing service."""
        mock_model = MagicMock()
        mock_model.name = 'models/gemini-pro'
        mock_model.supported_generation_methods = ['generateContent']
        mock_list_models.return_value = [mock_model]

        models = get_gemini_models("test_key")
        self.assertIn('models/gemini-pro', models)

if __name__ == '__main__':
    unittest.main()
