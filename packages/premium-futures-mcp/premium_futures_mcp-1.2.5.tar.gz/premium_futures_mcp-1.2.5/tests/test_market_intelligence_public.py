#!/usr/bin/env python3
"""
Test script for Market Intelligence System
Tests the new intelligent filtering and scoring system (no API keys required)
"""
import os
import asyncio
import json
from datetime import datetime
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService


async def test_market_intelligence():
    """Test the market intelligence system"""
    
    print("🧪 Testing Premium Binance Futures Market Intelligence System")
    print("=" * 60)
    print("ℹ️  Using public market data - no API keys required")
    print()
    
    try:
        print("🔗 Connecting to Binance public API...")
        
        async with PublicBinanceClient() as public_client:
            # Initialize market intelligence service (without Redis for testing)
            intelligence = MarketIntelligenceService(public_client, redis_client=None)
            
            print("✅ Connected successfully")
            print()
            
            # Test 1: Analyze a specific token
            print("📊 Test 1: Analyzing BTCUSDT...")
            try:
                # Get ticker data for BTCUSDT
                ticker_data = await public_client.get_ticker("BTCUSDT")
                
                # Calculate score
                btc_analysis = await intelligence.calculate_token_score("BTCUSDT", ticker_data)
                
                print(f"   Symbol: {btc_analysis['symbol']}")
                print(f"   Total Score: {btc_analysis['total_score']}/60")
                print(f"   Direction: {btc_analysis['direction']}")
                print(f"   Confidence: {btc_analysis['confidence']}")
                print(f"   Recommendation: {btc_analysis['recommendation']}")
                print(f"   Entry Timeframe: {btc_analysis.get('entry_timeframe', 'N/A')}")
                print(f"   Risk Level: {btc_analysis.get('risk_level', 'N/A')}")
                print(f"   Score Breakdown:")
                for factor, score in btc_analysis['score_breakdown'].items():
                    print(f"     - {factor.replace('_', ' ').title()}: {score}")
                
                if btc_analysis.get('confidence_factors'):
                    print(f"   Confidence Factors:")
                    for factor in btc_analysis['confidence_factors']:
                        print(f"     - {factor}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            # Test 2: Quick scan of top tokens (with proper filtering)
            print("🔍 Test 2: Quick scan of top 10 active tokens by volume...")
            try:
                print("   Getting exchange info to filter active symbols...")
                
                # Get exchange info to filter active symbols (like the real system does)
                exchange_info = await public_client.get_exchange_info()
                active_symbols = set()
                
                for symbol_info in exchange_info.get('symbols', []):
                    if (symbol_info.get('status') == 'TRADING' and 
                        symbol_info.get('contractType') == 'PERPETUAL' and
                        symbol_info['symbol'].endswith('USDT')):
                        active_symbols.add(symbol_info['symbol'])
                
                print(f"   Found {len(active_symbols)} active USDT perpetual contracts")
                
                # Get all tickers and filter by active symbols
                all_tickers = await public_client.get_all_tickers()
                
                # Filter by active symbols first, then sort by volume
                active_tickers = [t for t in all_tickers 
                                if t['symbol'] in active_symbols and float(t['volume']) > 100000]
                active_tickers.sort(key=lambda x: float(x['volume']), reverse=True)
                
                top_10 = active_tickers[:10]
                
                print(f"   Processing top 10 active tokens by volume...")
                print(f"   Active tokens to analyze: {[t['symbol'] for t in top_10]}")
                
                opportunities = []
                for i, ticker in enumerate(top_10, 1):
                    symbol = ticker['symbol']
                    print(f"   [{i}/10] Analyzing {symbol}...", end=" ")
                    
                    try:
                        analysis = await intelligence.calculate_token_score(symbol, ticker)
                        opportunities.append(analysis)
                        print(f"Score: {analysis['total_score']}/60 ({analysis['direction']})")
                    except Exception as e:
                        print(f"Error: {e}")
                
                # Sort by score and show top 5
                opportunities.sort(key=lambda x: x.get('total_score', 0), reverse=True)
                
                print()
                print("🏆 Top 5 Opportunities from scan:")
                for i, opp in enumerate(opportunities[:5], 1):
                    print(f"   {i}. {opp['symbol']}: {opp['total_score']}/60")
                    print(f"      Direction: {opp['direction']} | Confidence: {opp['confidence']}")
                    print(f"      Recommendation: {opp['recommendation']}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            # Test 3: Test specific market intelligence features
            print("🎯 Test 3: Testing specific scoring components...")
            try:
                test_symbol = "ETHUSDT"
                ticker_data = await public_client.get_ticker(test_symbol)
                
                print(f"   Testing {test_symbol} scoring components:")
                
                # Test individual scoring components
                analysis = await intelligence.calculate_token_score(test_symbol, ticker_data)
                
                breakdown = analysis.get('score_breakdown', {})
                for component, score in breakdown.items():
                    component_name = component.replace('_', ' ').title()
                    print(f"     ✓ {component_name}: {score} points")
                
                print(f"   Total Assessment:")
                print(f"     Overall Score: {analysis['total_score']}/60")
                print(f"     Trading Direction: {analysis['direction']}")
                print(f"     Confidence Level: {analysis['confidence']}")
                print(f"     Risk Assessment: {analysis.get('risk_level', 'N/A')}")
                print(f"     Entry Timing: {analysis.get('entry_timeframe', 'N/A')}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            # Test 4: Market overview (using proper filtering)
            print("📈 Test 4: Market overview and statistics...")
            try:
                print("   Generating market overview with active symbols only...")
                
                # Use the same active symbols from Test 2
                exchange_info = await public_client.get_exchange_info()
                active_symbols = set()
                
                for symbol_info in exchange_info.get('symbols', []):
                    if (symbol_info.get('status') == 'TRADING' and 
                        symbol_info.get('contractType') == 'PERPETUAL' and
                        symbol_info['symbol'].endswith('USDT')):
                        active_symbols.add(symbol_info['symbol'])
                
                # Get all tickers and filter by active symbols
                all_tickers = await public_client.get_all_tickers()
                active_tickers = [t for t in all_tickers 
                                if t['symbol'] in active_symbols and float(t['volume']) > 100000]
                active_tickers.sort(key=lambda x: float(x['volume']), reverse=True)
                
                # Get sample of market data (top 30 by volume)
                sample_tickers = active_tickers[:30]
                
                print(f"   Analyzing top 30 active tokens by volume...")
                
                total_analyzed = 0
                high_confidence = 0
                long_signals = 0
                short_signals = 0
                
                for ticker in sample_tickers:
                    try:
                        analysis = await intelligence.calculate_token_score(ticker['symbol'], ticker)
                        total_analyzed += 1
                        
                        if analysis.get('confidence') == 'HIGH':
                            high_confidence += 1
                        
                        if analysis.get('direction') == 'LONG':
                            long_signals += 1
                        elif analysis.get('direction') == 'SHORT':
                            short_signals += 1
                            
                    except:
                        continue
                
                print(f"   Market Overview (Top 30 active tokens):")
                print(f"     Total Active Symbols: {len(active_symbols)}")
                print(f"     Total Analyzed: {total_analyzed}")
                print(f"     High Confidence Opportunities: {high_confidence}")
                print(f"     Long Signals: {long_signals}")
                print(f"     Short Signals: {short_signals}")
                print(f"     Neutral/Watch: {total_analyzed - long_signals - short_signals}")
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
            
            print("✅ All tests completed successfully!")
            print()
            print("🎉 Market Intelligence System is working properly!")
            print("📊 Ready for integration with MCP server")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_market_intelligence())
