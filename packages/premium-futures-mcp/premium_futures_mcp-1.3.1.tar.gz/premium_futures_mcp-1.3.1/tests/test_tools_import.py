#!/usr/bin/env python3
"""
Test script to check if the tools import issue is resolved
"""

import asyncio
import sys
import traceback

async def test_tools_import():
    """Test if tools can be imported without circular import issues"""
    try:
        print("Testing tools.py import...")
        from premium_futures_mcp.tools import get_all_tools
        tools1 = get_all_tools()
        print(f"✅ Existing tools import successful: {len(tools1)} tools")
        
        print("Testing intelligent_tools.py import...")
        from premium_futures_mcp.intelligent_tools import get_intelligent_market_tools
        tools2 = get_intelligent_market_tools()
        print(f"✅ Intelligent tools import successful: {len(tools2)} tools")
        
        print("Testing combined tools...")
        all_tools = tools1 + tools2
        print(f"✅ Combined tools successful: {len(all_tools)} total tools")
        
        print("Testing server import...")
        from premium_futures_mcp.server import BinanceMCPServer
        print("✅ Server import successful")
        
        print("All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error type: {type(e)}")
        print("❌ Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    
    result = asyncio.run(test_tools_import())
    exit(0 if result else 1)
