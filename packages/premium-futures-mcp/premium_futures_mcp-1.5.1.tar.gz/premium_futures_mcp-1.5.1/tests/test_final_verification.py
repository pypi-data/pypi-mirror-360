#!/usr/bin/env python3
"""
Test script to simulate MCP tool execution for get_market_opportunities
"""

import asyncio
import json

async def test_get_market_opportunities_tool():
    """Test get_market_opportunities tool like MCP would call it"""
    try:
        print("Testing get_market_opportunities tool execution...")
        
        # Import required modules
        from premium_futures_mcp.handlers import ToolHandler
        from premium_futures_mcp.config import BinanceConfig
        from premium_futures_mcp.cache import TickerCache
        from premium_futures_mcp.client import BinanceClient
        
        # Initialize handler
        config = BinanceConfig("", "")  # No API keys needed for intelligent tools
        cache = TickerCache()
        handler = ToolHandler(config, cache)
        
        # Simulate tool call
        arguments = {
            "limit": 5,
            "min_score": 25,
            "direction": "ALL",
            "confidence": "ALL",
            "risk_level": "ALL"
        }
        
        print("Executing get_market_opportunities tool...")
        
        # This simulates how the server would call the tool
        async with BinanceClient(config) as client:
            result = await handler.handle_tool_call("get_market_opportunities", arguments)
        
        print("✅ Tool execution successful!")
        print(f"✅ Found {result.get('total_found', 0)} opportunities")
        
        # Show first opportunity
        opportunities = result.get('opportunities', [])
        if opportunities:
            first = opportunities[0]
            print(f"✅ Top opportunity: {first['symbol']} - {first['total_score']}/{first['max_score']} ({first['confidence']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error executing tool: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing MCP Tool Execution ===")
    result = asyncio.run(test_get_market_opportunities_tool())
    
    if result:
        print("\n🎉 SUCCESS: get_market_opportunities tool works without TimeoutError!")
        print("Your intelligent tools are now ready for use.")
    else:
        print("\n❌ FAILED: Tool execution still has issues.")
    
    exit(0 if result else 1)
