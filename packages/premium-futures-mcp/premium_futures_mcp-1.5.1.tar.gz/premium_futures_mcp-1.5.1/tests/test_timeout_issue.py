#!/usr/bin/env python3
"""
Test script to diagnose the TimeoutError issue with market intelligence
"""

import asyncio
import sys
import traceback

async def test_market_intelligence():
    """Test if market intelligence can be imported and initialized"""
    try:
        print("Testing MarketIntelligenceService import...")
        from premium_futures_mcp.market_intelligence import MarketIntelligenceService
        print("✅ Import successful")
        
        print("Testing MarketIntelligenceService initialization...")
        service = MarketIntelligenceService(None, None)
        print("✅ Initialization successful")
        
        print("Testing PublicBinanceClient import...")
        from premium_futures_mcp.public_client import PublicBinanceClient
        print("✅ PublicBinanceClient import successful")
        
        print("Testing aioredis import...")
        import aioredis
        print("✅ aioredis import successful")
        
        print("Testing aiohttp import...")
        import aiohttp
        print("✅ aiohttp import successful")
        
        print("All imports and initialization successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")
        print("❌ Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    result = asyncio.run(test_market_intelligence())
    exit(0 if result else 1)
