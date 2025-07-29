#!/usr/bin/env python3
"""
Test that delisted tokens are properly blocked at the scoring level
"""
import os
import asyncio
import logging
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_delisted_blocking():
    """Test that delisted tokens are blocked at the scoring level"""
    
    print("🧪 Testing Delisted Token Blocking at Scoring Level")
    print("=" * 55)
    
    try:
        async with PublicBinanceClient() as public_client:
            # Initialize market intelligence service
            intelligence = MarketIntelligenceService(public_client, redis_client=None)
            
            print("🔗 Connected to Binance public API")
            print()
            
            # Get some known delisted tokens from exchange info
            print("🔍 Finding delisted tokens...")
            exchange_info = await public_client.get_exchange_info()
            all_symbols = exchange_info.get('symbols', [])
            
            # Find USDT tokens that are not actively trading
            delisted_tokens = []
            active_tokens = []
            
            for symbol_info in all_symbols:
                symbol = symbol_info.get('symbol', '')
                status = symbol_info.get('status', '')
                
                if symbol.endswith('USDT'):
                    if status != 'TRADING':
                        delisted_tokens.append(symbol)
                    else:
                        active_tokens.append(symbol)
            
            print(f"📊 Found {len(delisted_tokens)} delisted USDT tokens")
            print(f"📊 Found {len(active_tokens)} active USDT tokens")
            print()
            
            # Test scoring of known delisted tokens
            test_delisted = delisted_tokens[:3]  # Test first 3
            test_active = active_tokens[:2]      # Test first 2 active as control
            
            print(f"🔬 Testing delisted tokens (should be blocked):")
            for symbol in test_delisted:
                try:
                    # Try to get ticker data first
                    ticker_data = await public_client.get_ticker(symbol)
                    
                    # Try to score it
                    result = await intelligence.calculate_token_score(symbol, ticker_data)
                    
                    if result.get('error'):
                        print(f"   ✅ {symbol}: BLOCKED - {result['error']}")
                    else:
                        print(f"   ❌ {symbol}: NOT BLOCKED - Score: {result.get('total_score', 0)}")
                        
                except Exception as e:
                    print(f"   ✅ {symbol}: BLOCKED at API level - {str(e)[:50]}...")
            
            print()
            print(f"🔬 Testing active tokens (should work normally):")
            for symbol in test_active:
                try:
                    ticker_data = await public_client.get_ticker(symbol)
                    result = await intelligence.calculate_token_score(symbol, ticker_data)
                    
                    if result.get('error'):
                        print(f"   ❌ {symbol}: UNEXPECTED ERROR - {result['error']}")
                    else:
                        print(f"   ✅ {symbol}: Working - Score: {result.get('total_score', 0)}")
                        
                except Exception as e:
                    print(f"   ❌ {symbol}: UNEXPECTED ERROR - {e}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_delisted_blocking())
