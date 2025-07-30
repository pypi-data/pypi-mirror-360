#!/usr/bin/env python3
"""
Binance Futures MCP Server - Modular Implementation
"""

import os
import json
import asyncio
import argparse
from typing import Any, Sequence, Optional, Dict
from datetime import datetime, timedelta

import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
from typing import List

from .tools import get_all_tools
from .intelligent_tools import get_intelligent_market_tools
from .handlers import ToolHandler
from .client import BinanceClient
from .cache import TickerCache
from .config import BinanceConfig
from .auth import validate_member_key, MemberKey
from .remote_auth import validate_premium_key

class BinanceMCPServer:
    """Binance MCP Server implementation"""
    
    def __init__(self, api_key: str = "", secret_key: str = "", member_key: str = ""):
        self.server = Server("binance-futures-mcp-server")
        self.config = BinanceConfig(api_key, secret_key)
        self.ticker_cache = TickerCache(cache_duration_minutes=5)  # Cache for 5 minutes
        self.handler = ToolHandler(self.config, self.ticker_cache)
        self._background_task = None  # Will be started when server runs
        
        # Store member key for async validation during server start
        self._member_key = None
        self._raw_member_key = member_key
        
        self._setup_tools()
    
    async def _background_ticker_refresh(self):
        """Background task to refresh ticker data every 5 minutes"""
        print("[INFO] Starting background ticker refresh task...")
        while True:
            try:
                await asyncio.sleep(300)  # Wait 5 minutes
                await self._refresh_ticker_cache()
            except Exception as e:
                print(f"Error refreshing ticker cache: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def _start_background_task_if_needed(self):
        """Start background task if not already running"""
        if self._background_task is None or self._background_task.done():
            try:
                self._background_task = asyncio.create_task(self._background_ticker_refresh())
                print("[OK] Background ticker refresh task started")
            except RuntimeError:
                # Event loop not running yet, task will be started on first cache access
                print("[WAIT] Event loop not ready, background task will start on first cache access")
    
    async def _ensure_cache_fresh(self):
        """Ensure cache is fresh, refresh if needed, and start background task"""
        # Start background task if needed
        self._start_background_task_if_needed()
        
        # If cache is expired, refresh it immediately
        if self.ticker_cache.is_expired():
            print("[INFO] Cache expired, refreshing immediately...")
            await self._refresh_ticker_cache()
    
    async def _refresh_ticker_cache(self):
        """Refresh the ticker cache with latest data, filtering out delisted tokens"""
        try:
            async with BinanceClient(self.config) as client:
                # Step 1: Update exchange info if expired (every 30 minutes)
                if self.ticker_cache.is_exchange_info_expired():
                    print("[INFO] Refreshing exchange info to filter delisted tokens...")
                    exchange_info = await client._make_request("GET", "/fapi/v1/exchangeInfo")
                    self.ticker_cache.update_active_symbols(exchange_info)
                
                # Step 2: Fetch all 24hr ticker data
                print("[INFO] Fetching 24hr ticker data...")
                result = await client._make_request("GET", "/fapi/v1/ticker/24hr")
                
                # Step 3: Update cache with filtering
                self.ticker_cache.update_cache(result)
                
                active_count = len([item for item in self.ticker_cache.data 
                                  if item.get('symbol') in self.ticker_cache.active_symbols])
                total_count = len(result)
                
                print(f"[OK] Ticker cache refreshed: {active_count}/{total_count} active symbols at {datetime.now()}")
                
        except Exception as e:
            print(f"[ERROR] Failed to refresh ticker cache: {e}")
            # Don't clear existing cache on failure
    
    def _setup_tools(self):
        """Setup all MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools():
            """Handle tools/list requests"""
            # Combine all tools
            existing_tools = get_all_tools()
            intelligent_tools = get_intelligent_market_tools()
            return existing_tools + intelligent_tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            # Check if premium member key is valid for premium features
            premium_tools = [
                # Order Management Tools (6)
                "place_order", "place_multiple_orders", "cancel_order", "cancel_multiple_orders", 
                "cancel_all_orders", "auto_cancel_all_orders",
                
                # Position Management Tools (4) 
                "close_position", "modify_order", "add_tp_sl_to_position", "place_bracket_order",
                
                # Risk Management Tools (4)
                "get_adl_quantile", "get_leverage_brackets", "get_force_orders", "get_position_margin_history",
                
                # Trading Configuration Tools (4)
                "change_leverage", "change_margin_type", "change_position_mode", "modify_position_margin",
                
                # Premium Market Data Tools (7) 
                "get_top_gainers_losers", "get_market_overview", "get_taker_buy_sell_volume", 
                
                # Premium Sentiment Analysis Tools (4)
                "get_open_interest", "get_open_interest_stats", "get_top_trader_long_short_ratio", "get_top_long_short_account_ratio",
                
                # Market Intelligence Tools (9)
                "get_market_opportunities", "get_token_analysis", "get_market_dashboard",
                "get_funding_extremes", "get_volume_leaders", "get_volatility_squeeze",
                "get_whale_activity", "get_narrative_plays", "get_quick_scan"
            ]
            
            if name in premium_tools and not self._member_key:
                return [TextContent(
                    type="text",
                    text="Error: Premium access required. Please provide a valid premium member key."
                )]
            
            # Check if API credentials are configured for authenticated endpoints
            unauthenticated_tools = [
                "get_exchange_info", "get_price_ticker", "get_book_ticker", 
                "get_order_book", "get_klines", "get_mark_price", 
                "get_aggregate_trades", "get_funding_rate_history"
            ]
            
            if not self.config.api_key or not self.config.secret_key:
                if name not in unauthenticated_tools:
                    return [TextContent(
                        type="text",
                        text="Error: API credentials not configured. Please provide valid API key and secret key."
                    )]
            
            try:
                # Ensure cache is fresh for market data tools
                if name in ["get_top_gainers_losers", "get_market_overview", "get_24hr_ticker"]:
                    await self._ensure_cache_fresh()
                
                # Delegate to handler
                result = await self.handler.handle_tool_call(name, arguments)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                print(f"[ERROR] {error_msg}")
                return [TextContent(
                    type="text",
                    text=error_msg
                )]

    async def _validate_member_key(self, member_key: str):
        """Validate the premium member key"""
        if not member_key:
            print("[WARNING] No premium member key provided. Premium features will be disabled.")
            return
            
        try:
            # Try local validation first
            key_info = validate_member_key(member_key)
            if key_info:
                print(f"[OK] Premium member key validated locally for {key_info.member_id}")
                self._member_key = key_info
                return
                
            # If local validation fails, try remote validation
            print("[INFO] Local validation failed, trying remote validation...")
            is_valid = await validate_premium_key(member_key)
            if is_valid:
                print(f"[OK] Premium member key validated remotely")
                self._member_key = True  # Just mark as valid
            else:
                print("[ERROR] Invalid premium member key. Premium features will be disabled.")
        except Exception as e:
            print(f"[ERROR] Failed to validate premium member key: {e}")


async def main():
    """Main entry point for the server"""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Binance Futures MCP Server")
    parser.add_argument("--binance-api-key", 
                       help="Binance API key", 
                       default=os.getenv("BINANCE_API_KEY", ""))
    parser.add_argument("--binance-secret-key", 
                       help="Binance secret key", 
                       default=os.getenv("BINANCE_SECRET_KEY", ""))
    parser.add_argument("--binance-member-key", 
                       help="Binance member key", 
                       default=os.getenv("BINANCE_MCP_MEMBER_KEY", ""))
    
    args = parser.parse_args()
    
    # Initialize server with credentials
    server_instance = BinanceMCPServer(member_key=args.binance_member_key, api_key=args.binance_api_key, secret_key=args.binance_secret_key)
    
    # Validate member key before starting server
    if server_instance._raw_member_key:
        await server_instance._validate_member_key(server_instance._raw_member_key)
    
    # Run server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="binance-futures-mcp-server",
                server_version="1.4.9",
                capabilities={
                    "tools": {}
                }
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
