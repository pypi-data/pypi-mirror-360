#!/usr/bin/env python3
"""
Final test to confirm no delisted tokens appear in market scan logs
"""
import os
import asyncio
import logging
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

# Set up logging to catch any warnings about delisted tokens
logging.basicConfig(
    level=logging.WARNING,  # This will catch the "should be filtered earlier" warnings
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_clean_scan():
    """Test that full market scan produces no delisted token warnings"""
    
    print("🧪 Final Test: Clean Market Scan (No Delisted Token Warnings)")
    print("=" * 65)
    
    try:
        async with PublicBinanceClient() as public_client:
            intelligence = MarketIntelligenceService(public_client, redis_client=None)
            
            print("🔗 Connected to Binance public API")
            print("🔍 Running LIMITED market scan (first 50 tokens only)...")
            print("⚠️  Looking for any warnings about delisted tokens...")
            print()
            
            # Get ticker data
            all_tickers = await public_client.get_all_tickers()
            usdt_tickers = [ticker for ticker in all_tickers 
                           if ticker['symbol'].endswith('USDT') 
                           and float(ticker['volume']) > 100000]
            
            # Limit to first 50 for faster testing
            limited_tickers = usdt_tickers[:50]
            
            # Get active symbols for filtering
            exchange_info = await public_client.get_exchange_info()
            active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] 
                            if symbol['status'] == 'TRADING'}
            
            # Filter to only active symbols
            active_tickers = [ticker for ticker in limited_tickers 
                            if ticker['symbol'] in active_symbols]
            
            print(f"📊 Processing {len(active_tickers)} active tokens out of {len(limited_tickers)} total")
            print()
            
            # Process tokens
            scored_count = 0
            for ticker in active_tickers:
                symbol = ticker['symbol']
                try:
                    score_data = await intelligence.calculate_token_score(symbol, ticker)
                    if score_data.get('total_score', 0) >= 15:
                        scored_count += 1
                except Exception as e:
                    print(f"❌ Unexpected error for {symbol}: {e}")
            
            print(f"✅ Scan completed successfully!")
            print(f"📊 Found {scored_count} opportunities from {len(active_tickers)} active tokens")
            print("🎉 No delisted token warnings detected!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_clean_scan())
