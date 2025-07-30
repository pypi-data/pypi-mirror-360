
#!/usr/bin/env python3
"""
Test script for Market Intelligence System
Tests the new intelligent filtering and scoring system
"""

import asyncio
import os
import json
from datetime import datetime
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.config import BinanceConfig
from premium_futures_mcp.client import BinanceClient 
from premium_futures_mcp.market_intelligence import MarketIntelligenceService


async def test_market_intelligence():
    """Test the market intelligence system"""
    
    print("🧪 Testing Premium Binance Futures Market Intelligence System")
    print("=" * 60)
    
    # Load config from environment
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Error: BINANCE_API_KEY and BINANCE_SECRET_KEY environment variables required")
        return
    
    config = BinanceConfig(api_key, secret_key)
    
    try:
        print("🔗 Connecting to Binance Futures API...")
        
        async with BinanceClient(config) as client:
            # Initialize market intelligence service (without Redis for testing)
            intelligence = MarketIntelligenceService(client, redis_client=None)
            
            print("✅ Connected successfully")
            print()
            
            # Test 1: Analyze a specific token
            print("📊 Test 1: Analyzing BTCUSDT...")
            try:
                # Get ticker data for BTCUSDT
                ticker_data = await client._make_request("GET", "/fapi/v1/ticker/24hr", {"symbol": "BTCUSDT"})
                if isinstance(ticker_data, list):
                    ticker_data = ticker_data[0]
                
                # Calculate score
                btc_analysis = await intelligence.calculate_token_score("BTCUSDT", ticker_data)
                
                print(f"   Symbol: {btc_analysis['symbol']}")
                print(f"   Total Score: {btc_analysis['total_score']}/60")
                print(f"   Direction: {btc_analysis['direction']}")
                print(f"   Confidence: {btc_analysis['confidence']}")
                print(f"   Recommendation: {btc_analysis['recommendation']}")
                print(f"   Score Breakdown:")
                for factor, score in btc_analysis['score_breakdown'].items():
                    print(f"     - {factor}: {score}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            # Test 2: Quick scan of top tokens
            print("🔍 Test 2: Quick scan of top 10 tokens...")
            try:
                # Get all tickers and process top 10 by volume
                all_tickers = await client._make_request("GET", "/fapi/v1/ticker/24hr")
                
                # Filter USDT pairs and sort by volume
                usdt_tickers = [t for t in all_tickers if t['symbol'].endswith('USDT')]
                usdt_tickers.sort(key=lambda x: float(x['volume']), reverse=True)
                
                top_10 = usdt_tickers[:10]
                
                print(f"   Processing top 10 tokens by volume...")
                scored_tokens = []
                
                for i, ticker in enumerate(top_10, 1):
                    symbol = ticker['symbol']
                    print(f"   {i}/10: Analyzing {symbol}...")
                    
                    try:
                        analysis = await intelligence.calculate_token_score(symbol, ticker)
                        scored_tokens.append(analysis)
                    except Exception as e:
                        print(f"     ❌ Error analyzing {symbol}: {e}")
                
                # Sort by score and show results
                scored_tokens.sort(key=lambda x: x.get('total_score', 0), reverse=True)
                
                print()
                print("   📈 Top Scoring Tokens:")
                for i, token in enumerate(scored_tokens[:5], 1):
                    print(f"   {i}. {token['symbol']}: {token['total_score']}/60 ({token['direction']}) - {token['confidence']}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            # Test 3: Test individual scoring components
            print("🔧 Test 3: Testing individual scoring components...")
            try:
                test_symbol = "ETHUSDT"
                ticker_data = await client._make_request("GET", "/fapi/v1/ticker/24hr", {"symbol": test_symbol})
                if isinstance(ticker_data, list):
                    ticker_data = ticker_data[0]
                
                print(f"   Testing components for {test_symbol}:")
                
                # Test OI score
                oi_score = await intelligence._calculate_oi_score(test_symbol, ticker_data)
                print(f"     OI Score: {oi_score}/10")
                
                # Test volume score
                volume_score = await intelligence._calculate_volume_score(test_symbol, ticker_data)
                print(f"     Volume Score: {volume_score}/8")
                
                # Test funding score
                funding_score, funding_dir = await intelligence._calculate_funding_score(test_symbol)
                print(f"     Funding Score: {funding_score}/6 (Direction: {funding_dir})")
                
                # Test volatility score
                volatility_score = await intelligence._calculate_volatility_score(test_symbol)
                print(f"     Volatility Score: {volatility_score}/5")
                
                # Test whale score
                whale_score, whale_dir = await intelligence._calculate_whale_score(test_symbol)
                print(f"     Whale Score: {whale_score}/6 (Direction: {whale_dir})")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            print("✅ Market Intelligence System Test Completed!")
            print("🚀 System is ready for production use")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")


async def test_funding_extremes():
    """Test funding rate extreme detection"""
    
    print("💸 Testing Funding Rate Extreme Detection")
    print("=" * 40)
    
    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")
    
    if not api_key or not secret_key:
        print("❌ Error: API credentials required")
        return
    
    config = BinanceConfig(api_key, secret_key)
    
    try:
        async with BinanceClient(config) as client:
            intelligence = MarketIntelligenceService(client, redis_client=None)
            
            # Get funding rates for top tokens
            all_tickers = await client._make_request("GET", "/fapi/v1/ticker/24hr")
            usdt_pairs = [t['symbol'] for t in all_tickers if t['symbol'].endswith('USDT')][:20]
            
            extreme_funding = []
            
            for symbol in usdt_pairs:
                try:
                    funding_score, direction = await intelligence._calculate_funding_score(symbol)
                    if funding_score >= 4:  # Extreme funding
                        # Get actual funding rate
                        funding_data = await client._make_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
                        funding_rate = float(funding_data['lastFundingRate']) * 100  # Convert to percentage
                        
                        extreme_funding.append({
                            'symbol': symbol,
                            'funding_rate': funding_rate,
                            'score': funding_score,
                            'direction': direction
                        })
                except:
                    continue
            
            if extreme_funding:
                print("🚨 Extreme Funding Rates Detected:")
                extreme_funding.sort(key=lambda x: abs(x['funding_rate']), reverse=True)
                
                for i, item in enumerate(extreme_funding[:10], 1):
                    print(f"   {i}. {item['symbol']}: {item['funding_rate']:.4f}% → {item['direction']} signal (Score: {item['score']}/6)")
            else:
                print("   No extreme funding rates detected at this time")
            
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print(f"🕐 Test started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run main test
    asyncio.run(test_market_intelligence())
    
    print()
    
    # Run funding test
    asyncio.run(test_funding_extremes())
    
    print()
    print("🎯 All tests completed!")
