#!/usr/bin/env python3
"""
Test to specifically detect if delisted tokens are being processed
"""
import os
import asyncio
import logging
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

# Set up more verbose logging to catch delisted token handling
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_delisted_detection():
    """Test to see if delisted tokens are being processed"""
    
    print("🧪 Testing Delisted Token Detection with Verbose Logging")
    print("=" * 60)
    
    try:
        async with PublicBinanceClient() as public_client:
            # Initialize market intelligence service
            intelligence = MarketIntelligenceService(public_client, redis_client=None)
            
            print("🔗 Connected to Binance public API")
            print("🔍 Getting all ticker data first...")
            
            # Get all tickers (before filtering)
            all_tickers = await public_client.get_all_tickers()
            usdt_tickers = [ticker for ticker in all_tickers 
                           if ticker['symbol'].endswith('USDT') 
                           and float(ticker['volume']) > 100000]
            
            print(f"📊 Found {len(usdt_tickers)} USDT tokens with volume > 100k")
            
            # Get exchange info for filtering
            print("🔍 Getting exchange info for active symbol filtering...")
            exchange_info = await public_client.get_exchange_info()
            active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] 
                            if symbol['status'] == 'TRADING'}
            
            print(f"📊 Found {len(active_symbols)} active trading symbols total")
            
            # Check which symbols would be filtered out
            filtered_out = [ticker for ticker in usdt_tickers 
                          if ticker['symbol'] not in active_symbols]
            
            if filtered_out:
                print(f"⚠️  {len(filtered_out)} USDT tokens would be filtered out as non-trading:")
                for ticker in filtered_out[:10]:  # Show first 10
                    print(f"     - {ticker['symbol']}")
                if len(filtered_out) > 10:
                    print(f"     ... and {len(filtered_out) - 10} more")
            else:
                print("✅ All USDT tokens with volume > 100k are active trading symbols")
            
            # Now test a few specific tokens that might be delisted
            print("\n🔍 Testing specific token scoring (including potential delisted ones)...")
            
            test_symbols = []
            # Add some filtered out symbols if they exist
            if filtered_out:
                test_symbols.extend([t['symbol'] for t in filtered_out[:3]])
            
            # Add some known active symbols
            active_usdt = [ticker for ticker in usdt_tickers 
                          if ticker['symbol'] in active_symbols]
            if active_usdt:
                test_symbols.extend([t['symbol'] for t in active_usdt[:3]])
            
            for symbol in test_symbols:
                print(f"\n🔬 Testing {symbol}...")
                try:
                    # Find the ticker data
                    ticker_data = next((t for t in usdt_tickers if t['symbol'] == symbol), None)
                    if ticker_data:
                        score_data = await intelligence.calculate_token_score(symbol, ticker_data)
                        print(f"   ✅ {symbol}: Score = {score_data.get('total_score', 0)}")
                    else:
                        print(f"   ⚠️  No ticker data for {symbol}")
                except Exception as e:
                    error_msg = str(e)
                    if "4108" in error_msg or "delivering or delivered or settling or closed" in error_msg:
                        print(f"   🚫 {symbol}: Delisted/suspended (error 4108) - correctly handled")
                    else:
                        print(f"   ❌ {symbol}: Unexpected error - {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_delisted_detection())
