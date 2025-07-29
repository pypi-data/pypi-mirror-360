#!/usr/bin/env python3
"""
Test full market scan to check for delisted tokens in logs
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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_full_market_scan():
    """Test the full market scan to see if delisted tokens appear"""
    
    print("🧪 Testing Full Market Scan for Delisted Token Detection")
    print("=" * 60)
    
    try:
        async with PublicBinanceClient() as public_client:
            # Initialize market intelligence service (without Redis for testing)
            intelligence = MarketIntelligenceService(public_client, redis_client=None)
            
            print("🔗 Connected to Binance public API")
            print("🔍 Starting full market scan...")
            print("   (This will process ALL active USDT tokens - may take a few minutes)")
            print()
            
            # Run the full scan_all_tokens() method
            opportunities = await intelligence.scan_all_tokens()
            
            print(f"✅ Scan completed!")
            print(f"📊 Results: {len(opportunities)} opportunities found")
            
            if opportunities:
                print(f"🏆 Top 10 opportunities:")
                for i, opp in enumerate(opportunities[:10], 1):
                    print(f"   {i}. {opp['symbol']}: {opp['total_score']}/60 ({opp['direction']})")
            else:
                print("⚠️  No opportunities found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_market_scan())
