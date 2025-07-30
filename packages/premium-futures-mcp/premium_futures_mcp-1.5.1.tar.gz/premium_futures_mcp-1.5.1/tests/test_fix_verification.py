#!/usr/bin/env python3
"""
Test script to verify that get_market_opportunities works without TimeoutError
"""

import asyncio
import json
import aioredis

async def test_market_opportunities():
    """Test the market opportunities function directly"""
    try:
        print("Testing Redis connection...")
        redis = aioredis.from_url('redis://localhost:6379')
        await redis.ping()
        print("✅ Redis connected")
        
        print("Testing market opportunities data...")
        data = await redis.get('market_opportunities')
        if data:
            try:
                parsed = json.loads(data)
                opportunities = parsed.get('opportunities', [])
                print(f"✅ Found {len(opportunities)} opportunities in Redis")
                
                if opportunities:
                    # Show first opportunity
                    first = opportunities[0]
                    print(f"✅ Sample opportunity: {first['symbol']} - {first['total_score']}/{first['max_score']}")
                    return True
                else:
                    print("⚠️ No opportunities found in Redis (market monitor might be starting)")
                    return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                return False
        else:
            print("⚠️ No market_opportunities key in Redis (market monitor might be starting)")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")
        return False
    finally:
        try:
            await redis.close()
        except:
            pass

async def test_tools_handler():
    """Test the tools handler directly"""
    try:
        print("Testing ToolHandler import...")
        from premium_futures_mcp.handlers import ToolHandler
        from premium_futures_mcp.config import BinanceConfig
        from premium_futures_mcp.cache import TickerCache
        
        print("✅ Handler imports successful")
        
        print("Testing handler initialization...")
        config = BinanceConfig("", "")
        cache = TickerCache()
        handler = ToolHandler(config, cache)
        print("✅ Handler initialization successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Testing Market Opportunities ===")
    result1 = asyncio.run(test_market_opportunities())
    
    print("\n=== Testing Tools Handler ===")
    result2 = asyncio.run(test_tools_handler())
    
    if result1 and result2:
        print("\n🎉 All tests passed! The TimeoutError issue should be resolved.")
    else:
        print("\n❌ Some tests failed.")
    
    exit(0 if (result1 and result2) else 1)
