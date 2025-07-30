# TimeoutError Fix Guide

## Problem: "duplicate base class TimeoutError"

If you're getting this error when using intelligent tools like `get_market_opportunities`:

```
Error executing get_market_opportunities: duplicate base class TimeoutError
```

## Root Cause

This was caused by conflicting dependencies in versions 1.2.3 and earlier, where `fastapi` and `uvicorn` were incorrectly included as main dependencies. These web framework libraries have their own async exception hierarchies that conflict with the MCP server's exception handling.

## Solution

### 1. Update to Version 1.2.4+

```bash
pip install --upgrade premium-futures-mcp>=1.2.4
```

Version 1.2.4+ removes `fastapi`/`uvicorn` from the main dependencies. These are only needed in the Docker container for the premium key server, not for local MCP usage.

### 2. Clean Installation (if upgrading doesn't work)

```bash
# Uninstall old version
pip uninstall premium-futures-mcp

# Clean install new version
pip install premium-futures-mcp>=1.2.4
```

### 3. For Development/Source Installations

If installing from source:

```bash
cd premium_futures_mcp
git pull  # Get latest fixes
pip uninstall premium-futures-mcp
pip install -e .
```

## Architecture Explanation

**Local MCP Client** (what users install):
- Only includes core MCP dependencies
- Connects to Redis cache in Docker
- No web server dependencies needed

**Docker Services** (what runs on server):
- Includes `fastapi`/`uvicorn` for key server
- Includes `numpy`/`pandas` for analytics
- Runs market monitor and Redis cache

This separation prevents dependency conflicts while maintaining full functionality.

## Verification

Test that the fix worked:

```python
import asyncio
from premium_futures_mcp.handlers import ToolHandler
from premium_futures_mcp.config import BinanceConfig
from premium_futures_mcp.cache import TickerCache
from premium_futures_mcp.client import BinanceClient

async def test():
    config = BinanceConfig('', '')
    handler = ToolHandler(config, TickerCache())
    
    async with BinanceClient(config) as client:
        result = await handler.handle_tool_call('get_market_opportunities', {'limit': 5})
        print(f"✅ Success: {result.get('total_found', 0)} opportunities found")

asyncio.run(test())
```

If this runs without errors, the fix is working!
