#!/usr/bin/env python3
"""
Test script to verify intelligent tools integration with market monitor
"""

import asyncio
import json
from premium_futures_mcp.auth import validate_member_key
from premium_futures_mcp.handlers import ToolHandler
from premium_futures_mcp.config import BinanceConfig
from premium_futures_mcp.cache import TickerCache

async def test_intelligent_tools():
    """Test intelligent tools integration"""
    
    # Create config and handler
    config = BinanceConfig()
    ticker_cache = TickerCache()
    handler = ToolHandler(config, ticker_cache)
    
    # Test get_market_opportunities
    try:
        print("🔍 Testing get_market_opportunities...")
        result = await handler.handle_tool_call("get_market_opportunities", {
            "limit": 5,
            "min_score": 20
        })
        
        print(f"✅ Success! Found {len(result.get('opportunities', []))} opportunities")
        
        if result.get('opportunities'):
            print("\n📊 Top Opportunities:")
            for i, opp in enumerate(result['opportunities'][:3], 1):
                print(f"  {i}. {opp['symbol']}: {opp['total_score']}/60 - {opp['direction']} ({opp['confidence']})")
        
        print(f"\n📈 Cache Status: {result.get('cache_status', 'unknown')}")
        print(f"🕒 Analysis Time: {result.get('analysis_timestamp', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Test get_token_analysis
    try:
        print("\n🔍 Testing get_token_analysis for BTCUSDT...")
        result = await handler.handle_tool_call("get_token_analysis", {
            "symbol": "BTCUSDT"
        })
        
        if 'error' not in result:
            print(f"✅ Success! BTC Score: {result.get('total_score', 0)}/60")
            print(f"📈 Direction: {result.get('direction', 'unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 'unknown')}")
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_intelligent_tools())
