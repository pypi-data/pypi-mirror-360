#!/usr/bin/env python3
"""
Tool Handlers for Binance MCP Server
"""

from typing import Any, Dict
import logging
import asyncio
import redis.asyncio as redis

from .config import BinanceConfig
from .client import BinanceClient
from .public_client import PublicBinanceClient
from .response_optimizer import ResponseOptimizer
from .cache import TickerCache
from .market_intelligence import MarketIntelligenceService


class ToolHandler:
    """Handles tool execution for the MCP server"""
    
    def __init__(self, config: BinanceConfig, ticker_cache: TickerCache):
        self.config = config
        self.ticker_cache = ticker_cache
        self.market_intelligence = None
        self._redis_setup_pending = False
        self.logger = logging.getLogger(__name__)
        
        # Initialize MarketIntelligence service
        self._initialize_market_intelligence()
    
    def _initialize_market_intelligence(self):
        """Initialize MarketIntelligence service"""
        try:
            import asyncio
            from .market_intelligence import MarketIntelligenceService
            # Initialize with Redis client
            self.market_intelligence = MarketIntelligenceService()
            
            # Initialize Redis client for the service (will be done in async context)
            self._redis_setup_pending = True
            
            # Keep normal logging level for debugging
            # self.logger.setLevel(logging.WARNING)  # Commented out to see Redis debug messages
        except Exception as e:
            self.logger.error(f"Failed to initialize MarketIntelligence: {e}")
            self.market_intelligence = None
    
    async def _setup_redis_connection(self):
        """Setup Redis connection - non-blocking approach"""
        # Skip if already attempted
        if hasattr(self, '_redis_connection_attempted'):
            return
        
        self._redis_connection_attempted = True
        self.redis_client = None  # Default to None (fallback mode)
        
        # Don't await, just set a flag to attempt later
        self._redis_available = False
        
        # Quick test without blocking
        try:
            import redis.asyncio as redis
            
            # Create client but don't test connection yet
            self.redis_client = redis.Redis(
                host='localhost',
                port=6380,
                password='ilikeMyself1100',
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
                retry_on_timeout=False,
                max_connections=1
            )
            
            self.logger.info("🔄 Redis client created, will test on first use")
            
        except Exception as e:
            self.logger.info(f"🔄 Redis client creation failed: {e}")
            self.redis_client = None
    
    async def _setup_redis_for_intelligence(self):
        """Setup Redis client for MarketIntelligence service"""
        # This method is now deprecated - using _setup_redis_connection instead
        await self._setup_redis_connection()
    
    async def _get_redis_data(self, key: str) -> Any:
        """Direct Redis data access for intelligent tools"""
        try:
            # Quick check if Redis client exists
            if not hasattr(self, 'redis_client') or self.redis_client is None:
                return None
            
            # Test connection on first use if not tested yet
            if not hasattr(self, '_redis_tested'):
                try:
                    await asyncio.wait_for(self.redis_client.ping(), timeout=0.5)
                    self._redis_tested = True
                    self.logger.info("✅ Redis connection verified")
                except Exception as e:
                    self.logger.info(f"🔄 Redis not available: {e}")
                    self.redis_client = None
                    return None
            
            # Get data from Redis with very short timeout
            data = await asyncio.wait_for(self.redis_client.get(key), timeout=0.5)
            if data:
                import json
                return json.loads(data)
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            return None
    
    async def _get_market_opportunities_from_redis(self) -> list:
        """Get market opportunities directly from Redis cache"""
        try:
            # Quick Redis availability check
            if not hasattr(self, 'redis_client') or self.redis_client is None:
                return []
            
            # Get cached opportunities from Redis with very short timeout
            cache_data = await asyncio.wait_for(
                self._get_redis_data("market_opportunities"), 
                timeout=1.0
            )
            
            if cache_data and isinstance(cache_data, dict):
                opportunities = cache_data.get("opportunities", [])
                timestamp = cache_data.get("timestamp", "Unknown")
                
                if opportunities:
                    self.logger.info(f"✅ Retrieved {len(opportunities)} opportunities from Redis")
                    return opportunities
                
            return []
                
        except asyncio.TimeoutError:
            self.logger.debug("Redis timeout - returning empty list")
            return []
        except Exception as e:
            self.logger.debug(f"Redis error: {e}")
            return []
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        
        async with BinanceClient(self.config) as client:
            
            # Account Information Tools
            if name == "get_account_info":
                account_data = await client._make_request("GET", "/fapi/v3/account", security_type="USER_DATA")
                # Filter out zero balances to reduce token usage
                if "assets" in account_data:
                    original_asset_count = len(account_data["assets"])
                    non_zero_assets = []
                    for asset in account_data["assets"]:
                        # Keep only assets with non-zero values
                        if float(asset.get("walletBalance", 0)) > 0 or float(asset.get("unrealizedProfit", 0)) != 0:
                            # Simplify the asset data to essential fields
                            non_zero_assets.append({
                                "asset": asset.get("asset"),
                                "walletBalance": float(asset.get("walletBalance", 0)),
                                "unrealizedProfit": float(asset.get("unrealizedProfit", 0)),
                                "marginBalance": float(asset.get("marginBalance", 0)),
                                "availableBalance": float(asset.get("availableBalance", 0))
                            })
                    
                    # Replace the full assets list with filtered one
                    account_data["assets"] = non_zero_assets
                
                return account_data
            elif name == "get_balance":
                balance_data = await client._make_request("GET", "/fapi/v3/balance", security_type="USER_DATA")
                result = ResponseOptimizer.optimize_balance(balance_data)
                
                if "error" in result:
                    return {"error": result["error"]}
                
                return result
            elif name == "get_position_info":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                    return await client._make_request("GET", "/fapi/v2/positionRisk", params, "USER_DATA")
                else:
                    # Get all positions but filter to only open positions (non-zero size)
                    all_positions = await client._make_request("GET", "/fapi/v2/positionRisk", {}, "USER_DATA")
                    open_positions = [
                        pos for pos in all_positions 
                        if float(pos.get('positionAmt', 0)) != 0
                    ]
                    # Optimize response to reduce tokens
                    optimized_positions = ResponseOptimizer.optimize_positions(open_positions)
                    return {
                        "open_positions": optimized_positions,
                        "total_open_positions": len(optimized_positions),
                        "note": "Optimized response - showing only open positions with essential data"
                    }
            elif name == "get_position_mode":
                return await client._make_request("GET", "/fapi/v1/positionSide/dual", security_type="USER_DATA")
            elif name == "get_commission_rate":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("GET", "/fapi/v1/commissionRate", params, "USER_DATA")
            
            # Risk Management Tools
            elif name == "get_adl_quantile":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/adlQuantile", params, "USER_DATA")
            elif name == "get_leverage_brackets":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                    return await client._make_request("GET", "/fapi/v1/leverageBracket", params, "USER_DATA")
                else:
                    # Get all leverage brackets but limit to reduce token usage
                    all_brackets = await client._make_request("GET", "/fapi/v1/leverageBracket", params, "USER_DATA")
                    # Limit to first 50 symbols to avoid token bloat
                    limited_brackets = all_brackets[:50] if isinstance(all_brackets, list) else all_brackets
                    return {
                        "leverage_brackets": limited_brackets,
                        "total_symbols_available": len(all_brackets) if isinstance(all_brackets, list) else 1,
                        "showing_count": len(limited_brackets) if isinstance(limited_brackets, list) else 1,
                        "note": "Optimized response - showing first 50 symbols to reduce token usage"
                    }
            elif name == "get_force_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/forceOrders", params, "USER_DATA")
            elif name == "get_position_margin_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/positionMargin/history", params, "USER_DATA")
            
            # Order Management Tools
            elif name == "place_order":
                return await self._handle_place_order(client, arguments)
            elif name == "place_bracket_order":
                return await self._handle_place_bracket_order(client, arguments)
            elif name == "place_multiple_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("POST", "/fapi/v1/batchOrders", params, "TRADE")
            elif name == "cancel_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("DELETE", "/fapi/v1/order", params, "TRADE")
            elif name == "cancel_multiple_orders":
                params = {
                    "symbol": arguments["symbol"],
                    "orderIdList": arguments["order_id_list"]
                }
                return await client._make_request("DELETE", "/fapi/v1/batchOrders", params, "TRADE")
            elif name == "cancel_all_orders":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("DELETE", "/fapi/v1/allOpenOrders", params, "TRADE")
            elif name == "auto_cancel_all_orders":
                params = {
                    "symbol": arguments["symbol"],
                    "countdownTime": arguments["countdown_time"]
                }
                return await client._make_request("POST", "/fapi/v1/countdownCancelAll", params, "TRADE")
            
            # Order Query Tools
            elif name == "get_open_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("GET", "/fapi/v1/openOrder", params, "USER_DATA")
            elif name == "get_open_orders":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("GET", "/fapi/v1/openOrders", params, "USER_DATA")
            elif name == "get_all_orders":
                params = {k: v for k, v in arguments.items() if v is not None}
                # Limit to recent orders if no limit specified to avoid token bloat
                if "limit" not in params:
                    params["limit"] = 50  # Default to 50 most recent orders
                orders_data = await client._make_request("GET", "/fapi/v1/allOrders", params, "USER_DATA")
                # Optimize response format
                return {
                    "orders": ResponseOptimizer.optimize_orders(orders_data),
                    "total_orders": len(orders_data),
                    "note": "Optimized response - showing essential order data only"
                }
            elif name == "query_order":
                params = {"symbol": arguments["symbol"], "orderId": arguments["order_id"]}
                return await client._make_request("GET", "/fapi/v1/order", params, "USER_DATA")
            
            # Position Management Tools
            elif name == "close_position":
                return await self._handle_close_position(client, arguments)
            elif name == "modify_order":
                return await self._handle_modify_order(client, arguments)
            elif name == "add_tp_sl_to_position":
                return await self._handle_add_tp_sl(client, arguments)
            
            # Trading Configuration Tools
            elif name == "change_leverage":
                params = {"symbol": arguments["symbol"], "leverage": arguments["leverage"]}
                return await client._make_request("POST", "/fapi/v1/leverage", params, "TRADE")
            elif name == "change_margin_type":
                params = {"symbol": arguments["symbol"], "marginType": arguments["margin_type"]}
                return await client._make_request("POST", "/fapi/v1/marginType", params, "TRADE")
            elif name == "change_position_mode":
                params = {"dualSidePosition": arguments["dual_side"]}
                return await client._make_request("POST", "/fapi/v1/positionSide/dual", params, "TRADE")
            elif name == "modify_position_margin":
                params = {
                    "symbol": arguments["symbol"],
                    "amount": arguments["amount"],
                    "positionSide": arguments["position_side"],
                    "type": arguments["margin_type"]
                }
                return await client._make_request("POST", "/fapi/v1/positionMargin", params, "TRADE")
            
            # Market Data Tools
            elif name == "get_exchange_info":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                    return await client._make_request("GET", "/fapi/v1/exchangeInfo", params)
                else:
                    # Get full exchange info but optimize response
                    full_info = await client._make_request("GET", "/fapi/v1/exchangeInfo", params)
                    # Extract only essential info to reduce tokens
                    symbols = full_info.get('symbols', [])
                    # Filter to active symbols only and limit fields
                    active_symbols = [
                        {
                            "symbol": s.get('symbol'),
                            "status": s.get('status'),
                            "baseAsset": s.get('baseAsset'),
                            "quoteAsset": s.get('quoteAsset'),
                            "pricePrecision": s.get('pricePrecision'),
                            "quantityPrecision": s.get('quantityPrecision')
                        }
                        for s in symbols if s.get('status') == 'TRADING'
                    ]
                    return {
                        "timezone": full_info.get('timezone'),
                        "serverTime": full_info.get('serverTime'),
                        "symbols": active_symbols[:100],  # Limit to first 100 active symbols
                        "total_active_symbols": len(active_symbols),
                        "note": "Optimized response - showing first 100 active symbols with essential data only"
                    }
            elif name == "get_book_ticker":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/ticker/bookTicker", params)
            elif name == "get_price_ticker":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/ticker/price", params)
            elif name == "get_24hr_ticker":
                if "symbol" in arguments:
                    # Single symbol from cache
                    symbol_data = self.ticker_cache.get_symbol_data(arguments["symbol"])
                    if symbol_data:
                        return symbol_data
                    else:
                        # Fallback to API if not in cache
                        params = {"symbol": arguments["symbol"]}
                        return await client._make_request("GET", "/fapi/v1/ticker/24hr", params)
                else:
                    # Optimize: Return top 50 by volume to avoid massive token usage
                    all_data = self.ticker_cache.data
                    # Sort by volume and take top 50
                    sorted_data = sorted(all_data, key=lambda x: float(x.get('volume', 0)), reverse=True)[:50]
                    optimized_data = ResponseOptimizer.optimize_ticker_data(sorted_data, limit=50)
                    return {
                        "tickers": optimized_data,
                        "total_symbols_available": len(all_data),
                        "showing_top_by_volume": 50,
                        "note": "Optimized response - showing top 50 symbols by volume to reduce token usage"
                    }
            elif name == "get_top_gainers_losers":
                # Ensure cache is fresh before processing
                if self.ticker_cache.is_expired() or not self.ticker_cache.data:
                    try:
                        result = await client._make_request("GET", "/fapi/v1/ticker/24hr")
                        self.ticker_cache.update_cache(result)
                    except Exception as e:
                        return {"error": f"Failed to refresh market data: {str(e)}"}
                return self._handle_top_gainers_losers(arguments)
            elif name == "get_market_overview":
                # Ensure cache is fresh before processing
                if self.ticker_cache.is_expired() or not self.ticker_cache.data:
                    try:
                        result = await client._make_request("GET", "/fapi/v1/ticker/24hr")
                        self.ticker_cache.update_cache(result)
                    except Exception as e:
                        return {"error": f"Failed to refresh market data: {str(e)}"}
                return self._handle_market_overview(arguments)
            elif name == "get_order_book":
                params = {
                    "symbol": arguments["symbol"],
                    "limit": arguments["limit"]
                }
                return await client._make_request("GET", "/fapi/v1/depth", params)
            elif name == "get_klines":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/klines", params)
            elif name == "get_mark_price":
                params = {}
                if "symbol" in arguments:
                    params["symbol"] = arguments["symbol"]
                return await client._make_request("GET", "/fapi/v1/premiumIndex", params)
            elif name == "get_aggregate_trades":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/aggTrades", params)
            elif name == "get_funding_rate_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/fundingRate", params)
            elif name == "get_taker_buy_sell_volume":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/futures/data/takerlongshortRatio", params)
            
            # Premium Sentiment Analysis Tools
            elif name == "get_open_interest":
                params = {"symbol": arguments["symbol"]}
                return await client._make_request("GET", "/fapi/v1/openInterest", params)
            elif name == "get_open_interest_stats":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/futures/data/openInterestHist", params)
            elif name == "get_top_trader_long_short_ratio":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/futures/data/topLongShortPositionRatio", params)
            elif name == "get_top_long_short_account_ratio":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/futures/data/topLongShortAccountRatio", params)
            
            # Trading History Tools
            elif name == "get_account_trades":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/userTrades", params, "USER_DATA")
            elif name == "get_income_history":
                params = {k: v for k, v in arguments.items() if v is not None}
                return await client._make_request("GET", "/fapi/v1/income", params, "USER_DATA")
            
            # Market Intelligence Tools - Use direct Redis access
            elif name in ["get_market_opportunities", "get_token_analysis", "get_market_dashboard", 
                         "get_funding_extremes", "get_volume_leaders", "get_volatility_squeeze",
                         "get_whale_activity", "get_narrative_plays", "get_quick_scan"]:
                
                # Setup Redis connection once if not already attempted
                if not hasattr(self, '_redis_connection_attempted'):
                    await self._setup_redis_connection()
                
                return await self._handle_intelligent_tools(name, arguments, client)
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_place_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle place_order tool - Places a single order only
        
        For bracket orders with TP/SL, use place_bracket_order tool instead.
        """
        leverage = arguments.pop("leverage", None)
        
        # Filter out precision parameters and pass through all other parameters directly
        params = {k: v for k, v in arguments.items() if v is not None and k not in ["quantity_precision", "price_precision"]}
        
        # Handle backward compatibility for order_type parameter
        if "order_type" in params:
            params["type"] = params.pop("order_type")
        
        # Check if type parameter is present
        if "type" not in params:
            raise ValueError("Missing required parameter 'type'. Please specify the order type (e.g., 'MARKET', 'LIMIT', 'STOP', etc.)")
        
        # Validate mandatory parameters based on order type
        order_type = params.get("type")
        if order_type == "LIMIT":
            required_params = ["timeInForce", "quantity", "price"]
            missing = [p for p in required_params if p not in params]
            if missing:
                raise ValueError(f"LIMIT order missing required parameters: {missing}")
        elif order_type == "MARKET":
            if "quantity" not in params:
                raise ValueError("MARKET order missing required parameter: quantity")
        elif order_type in ["STOP", "TAKE_PROFIT"]:
            required_params = ["quantity", "price", "stopPrice"]
            missing = [p for p in required_params if p not in params]
            if missing:
                raise ValueError(f"{order_type} order missing required parameters: {missing}")
        elif order_type in ["STOP_MARKET", "TAKE_PROFIT_MARKET"]:
            if "stopPrice" not in params:
                raise ValueError(f"{order_type} order missing required parameter: stopPrice")
        elif order_type == "TRAILING_STOP_MARKET":
            if "callbackRate" not in params:
                raise ValueError("TRAILING_STOP_MARKET order missing required parameter: callbackRate")
        
        # Set leverage if provided
        if leverage:
            try:
                await client._make_request(
                    "POST", 
                    "/fapi/v1/leverage", 
                    {"symbol": params["symbol"], "leverage": leverage},
                    "USER_DATA"
                )
            except Exception as e:
                print(f"Warning: Failed to set leverage: {e}")
        
        # Place the single order
        return await client._make_request("POST", "/fapi/v1/order", params, "TRADE")
        
        # For bracket orders, we need to place the entry order first, then TP and SL
        result = {
            "order": {
                "symbol": params["symbol"],
                "side": params["side"],
                "type": params["type"],
                "orders": {}
            }
        }
        
        try:
            # 1. Place entry order
            entry_order = await client._make_request("POST", "/fapi/v1/order", params, "TRADE")
            result["order"]["orders"]["entry"] = entry_order
            
            # Determine opposite side for TP and SL orders
            side = params["side"]
            opposite_side = "SELL" if side == "BUY" else "BUY"
            position_side = params.get("positionSide", "BOTH")
            symbol = params["symbol"]
            quantity = params["quantity"]
            time_in_force = params.get("timeInForce", "GTC")
            
            # 2. Place take-profit order if specified
            if take_profit_price:
                tp_order_type = "TAKE_PROFIT" if tp_type == "LIMIT" else "TAKE_PROFIT_MARKET"
                tp_params = {
                    "symbol": symbol,
                    "side": opposite_side,
                    "positionSide": position_side,
                    "quantity": quantity,
                    "type": tp_order_type,
                    "stopPrice": take_profit_price,
                    "reduceOnly": "true" # Ensure it only reduces the position
                }
                
                # Add price and timeInForce only for LIMIT take-profit orders
                if tp_type == "LIMIT":
                    tp_params["price"] = take_profit_price
                    tp_params["timeInForce"] = time_in_force
                
                tp_order = await client._make_request(
                    "POST", 
                    "/fapi/v1/order", 
                    tp_params,
                    "TRADE"
                )
                
                result["order"]["orders"]["take_profit"] = tp_order
            
            # 3. Place stop-loss order if specified
            if stop_loss_price:
                sl_order_type = "STOP" if sl_type == "LIMIT" else "STOP_MARKET"
                sl_params = {
                    "symbol": symbol,
                    "side": opposite_side,
                    "positionSide": position_side,
                    "quantity": quantity,
                    "type": sl_order_type,
                    "stopPrice": stop_loss_price,
                    "reduceOnly": "true" # Ensure it only reduces the position
                }
                
                # Add price and timeInForce only for LIMIT stop-loss orders
                if sl_type == "LIMIT":
                    sl_params["price"] = stop_loss_price
                    sl_params["timeInForce"] = time_in_force
                
                sl_order = await client._make_request(
                    "POST", 
                    "/fapi/v1/order", 
                    sl_params,
                    "TRADE"
                )
                
                result["order"]["orders"]["stop_loss"] = sl_order
            
            return result
            
        except Exception as e:
            # If any order fails, attempt to cancel any successful orders
            if "orders" in result["order"]:
                for order_type, order in result["order"]["orders"].items():
                    if "orderId" in order:
                        try:
                            await client._make_request(
                                "DELETE", 
                                "/fapi/v1/order", 
                                {"symbol": symbol, "orderId": order["orderId"]},
                                "TRADE"
                            )
                        except Exception as cancel_error:
                            print(f"Failed to cancel {order_type} order: {cancel_error}")
            
            # Re-raise the original exception
            raise ValueError(f"Failed to place order: {str(e)}")
        raise ValueError(f"Failed to place order: {str(e)}")
    
    async def _handle_close_position(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle close_position tool"""
        symbol = arguments["symbol"]
        position_side = arguments.get("position_side", "BOTH")
        quantity = arguments.get("quantity")
        close_all = arguments.get("close_all", False)
        
        # First, get current position to determine the side and quantity to close
        position_params = {"symbol": symbol}
        positions = await client._make_request("GET", "/fapi/v2/positionRisk", position_params, "USER_DATA")
        
        # Find the position to close
        position_to_close = None
        for pos in positions:
            if pos["symbol"] == symbol and float(pos["positionAmt"]) != 0:
                if position_side == "BOTH" or pos["positionSide"] == position_side:
                    position_to_close = pos
                    break
        
        if not position_to_close:
            raise ValueError(f"No open position found for {symbol} with position side {position_side}")
        
        position_amt = float(position_to_close["positionAmt"])
        current_position_side = position_to_close["positionSide"]
        
        # Determine order side (opposite of position)
        if position_amt > 0:  # Long position
            order_side = "SELL"
        else:  # Short position
            order_side = "BUY"
            position_amt = abs(position_amt)  # Make positive for order quantity
        
        # Determine quantity to close
        if close_all:
            # Use closePosition parameter to close entire position
            order_params = {
                "symbol": symbol,
                "side": order_side,
                "type": "MARKET",
                "closePosition": "true"
            }
            if current_position_side != "BOTH":
                order_params["positionSide"] = current_position_side
        else:
            # Close specific quantity or entire position
            close_quantity = quantity if quantity else position_amt
            order_params = {
                "symbol": symbol,
                "side": order_side,
                "type": "MARKET",
                "quantity": close_quantity
            }
            if current_position_side != "BOTH":
                order_params["positionSide"] = current_position_side
        
        return await client._make_request("POST", "/fapi/v1/order", order_params, "TRADE")
    
    async def _handle_modify_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle modify_order tool"""
        params = {
            "symbol": arguments["symbol"],
            "orderId": arguments["order_id"],
            "side": arguments["side"],
            "quantity": arguments["quantity"],
            "price": arguments["price"]
        }
        if "priceMatch" in arguments:
            params["priceMatch"] = arguments["priceMatch"]
        return await client._make_request("PUT", "/fapi/v1/order", params, "TRADE")
    
    async def _handle_add_tp_sl(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add_tp_sl_to_position tool"""
        symbol = arguments["symbol"]
        position_side = arguments.get("position_side", "BOTH")
        take_profit_price = arguments.get("take_profit_price")
        stop_loss_price = arguments.get("stop_loss_price")
        quantity = arguments.get("quantity")
        tp_order_type = arguments.get("tp_order_type", "TAKE_PROFIT_MARKET")
        sl_order_type = arguments.get("sl_order_type", "STOP_MARKET")
        time_in_force = arguments.get("time_in_force", "GTC")
        
        if not take_profit_price and not stop_loss_price:
            raise ValueError("At least one of take_profit_price or stop_loss_price must be provided")
        
        # Get current position to determine side and quantity
        position_params = {"symbol": symbol}
        positions = await client._make_request("GET", "/fapi/v2/positionRisk", position_params, "USER_DATA")
        
        # Find the position
        position = None
        for pos in positions:
            if pos["symbol"] == symbol and float(pos["positionAmt"]) != 0:
                if position_side == "BOTH" or pos["positionSide"] == position_side:
                    position = pos
                    break
        
        if not position:
            raise ValueError(f"No open position found for {symbol}")
        
        position_amt = float(position["positionAmt"])
        current_position_side = position["positionSide"]
        
        # Determine order side (opposite of position)
        order_side = "SELL" if position_amt > 0 else "BUY"
        order_quantity = quantity if quantity else abs(position_amt)
        
        result = {"symbol": symbol, "orders": {}}
        
        # Place take profit order if specified
        if take_profit_price:
            tp_params = {
                "symbol": symbol,
                "side": order_side,
                "type": tp_order_type,
                "quantity": order_quantity,
                "reduceOnly": "true"
            }
            
            if tp_order_type == "LIMIT":
                tp_params["price"] = take_profit_price
                tp_params["timeInForce"] = time_in_force
            elif tp_order_type == "TAKE_PROFIT_MARKET":
                tp_params["stopPrice"] = take_profit_price
            
            if current_position_side != "BOTH":
                tp_params["positionSide"] = current_position_side
            
            try:
                tp_order = await client._make_request("POST", "/fapi/v1/order", tp_params, "TRADE")
                result["orders"]["take_profit"] = tp_order
            except Exception as e:
                result["orders"]["take_profit"] = {"error": str(e)}
        
        # Place stop loss order if specified
        if stop_loss_price:
            sl_params = {
                "symbol": symbol,
                "side": order_side,
                "type": sl_order_type,
                "quantity": order_quantity,
                "reduceOnly": "true"
            }
            
            if sl_order_type == "LIMIT":
                sl_params["price"] = stop_loss_price
                sl_params["timeInForce"] = time_in_force
            elif sl_order_type == "STOP_MARKET":
                sl_params["stopPrice"] = stop_loss_price
            
            if current_position_side != "BOTH":
                sl_params["positionSide"] = current_position_side
            
            try:
                sl_order = await client._make_request("POST", "/fapi/v1/order", sl_params, "TRADE")
                result["orders"]["stop_loss"] = sl_order
            except Exception as e:
                result["orders"]["stop_loss"] = {"error": str(e)}
        
        return result

    async def _handle_place_bracket_order(self, client: BinanceClient, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle place_bracket_order tool - Uses batch orders for efficient TP/SL placement"""
        
        # Extract parameters
        symbol = arguments["symbol"]
        side = arguments["side"]
        quantity = arguments["quantity"]
        entry_order_type = arguments.get("entry_order_type", "MARKET")
        entry_price = arguments.get("entry_price")
        take_profit_price = arguments["take_profit_price"]
        stop_loss_price = arguments["stop_loss_price"]
        position_side = arguments.get("positionSide", "BOTH")
        time_in_force = arguments.get("timeInForce", "GTC")
        tp_order_type = arguments.get("tp_order_type", "TAKE_PROFIT_MARKET")
        sl_order_type = arguments.get("sl_order_type", "STOP_MARKET")
        leverage = arguments.get("leverage")
        
        # Set leverage if provided
        if leverage:
            try:
                await client._make_request(
                    "POST", 
                    "/fapi/v1/leverage", 
                    {"symbol": symbol, "leverage": leverage},
                    "USER_DATA"
                )
            except Exception as e:
                print(f"Warning: Failed to set leverage: {e}")
        
        # Determine opposite side for TP and SL orders
        opposite_side = "SELL" if side == "BUY" else "BUY"
        
        # Build entry order
        entry_order = {
            "symbol": symbol,
            "side": side,
            "type": entry_order_type,
            "quantity": str(quantity)
        }
        
        if position_side != "BOTH":
            entry_order["positionSide"] = position_side
            
        if entry_order_type == "LIMIT":
            if not entry_price:
                raise ValueError("entry_price is required for LIMIT entry orders")
            entry_order["price"] = str(entry_price)
            entry_order["timeInForce"] = time_in_force
        
        # Build take profit order
        tp_order = {
            "symbol": symbol,
            "side": opposite_side,
            "type": tp_order_type,
            "quantity": str(quantity),
            "reduceOnly": "true"
        }
        
        if position_side != "BOTH":
            tp_order["positionSide"] = position_side
            
        if tp_order_type == "TAKE_PROFIT":
            tp_order["price"] = str(take_profit_price)
            tp_order["stopPrice"] = str(take_profit_price)
            tp_order["timeInForce"] = time_in_force
        else:  # TAKE_PROFIT_MARKET
            tp_order["stopPrice"] = str(take_profit_price)
        
        # Build stop loss order
        sl_order = {
            "symbol": symbol,
            "side": opposite_side,
            "type": sl_order_type,
            "quantity": str(quantity),
            "reduceOnly": "true"
        }
        
        if position_side != "BOTH":
            sl_order["positionSide"] = position_side
            
        if sl_order_type == "STOP":
            sl_order["price"] = str(stop_loss_price)
            sl_order["stopPrice"] = str(stop_loss_price)
            sl_order["timeInForce"] = time_in_force
        else:  # STOP_MARKET
            sl_order["stopPrice"] = str(stop_loss_price)
        
        # Prepare batch order request
        batch_orders = [entry_order, tp_order, sl_order]
        
        batch_params = {
            "batchOrders": batch_orders
        }
        
        try:
            # Place all orders in a single batch request
            result = await client._make_request("POST", "/fapi/v1/batchOrders", batch_params, "TRADE")
            
            # Structure the response for better readability
            structured_result = {
                "bracket_order": {
                    "symbol": symbol,
                    "side": side,
                    "quantity": quantity,
                    "orders": {
                        "entry": result[0] if len(result) > 0 else None,
                        "take_profit": result[1] if len(result) > 1 else None,
                        "stop_loss": result[2] if len(result) > 2 else None
                    }
                }
            }
            
            return structured_result
            
        except Exception as e:
            raise ValueError(f"Failed to place bracket order: {str(e)}")
    
    def _handle_top_gainers_losers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_top_gainers_losers tool"""
        request_type = arguments.get("type", "both").lower()
        limit = min(arguments.get("limit", 10), 200)  # Max 200
        min_volume = arguments.get("min_volume", 0)
        
        # Check if cache has data
        if not self.ticker_cache.data:
            return {
                "error": "No market data available",
                "cache_status": "empty"
            }
        
        result = {}
        
        if request_type in ["gainers", "both"]:
            gainers = self.ticker_cache.get_top_gainers(limit)
            if min_volume > 0:
                gainers = [g for g in gainers if float(g.get('volume', 0)) >= min_volume]
            
            # Create a more compact representation of gainers
            compact_gainers = []
            for g in gainers[:limit]:
                compact_gainers.append({
                    "symbol": g.get("symbol", ""),
                    "pct": float(g.get("priceChangePercent", 0)),
                    "price": g.get("lastPrice", ""),
                    "volume": g.get("volume", ""),
                    "priceChange": g.get("priceChange", "")
                })
            result["gainers"] = compact_gainers
        
        if request_type in ["losers", "both"]:
            losers = self.ticker_cache.get_top_losers(limit)
            if min_volume > 0:
                losers = [l for l in losers if float(l.get('volume', 0)) >= min_volume]
            
            # Create a more compact representation of losers
            compact_losers = []
            for l in losers[:limit]:
                compact_losers.append({
                    "symbol": l.get("symbol", ""),
                    "pct": float(l.get("priceChangePercent", 0)),
                    "price": l.get("lastPrice", ""),
                    "volume": l.get("volume", ""),
                    "priceChange": l.get("priceChange", "")
                })
            result["losers"] = compact_losers
        
        return result
    
    def _handle_market_overview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_market_overview tool"""
        include_top_movers = arguments.get("include_top_movers", True)
        volume_threshold = arguments.get("volume_threshold", 0)
        
        # Check if cache has data
        if not self.ticker_cache.data:
            return {
                "error": "No market data available",
                "cache_status": "empty"
            }
        
        # Filter data by volume threshold
        filtered_data = self.ticker_cache.data
        if volume_threshold > 0:
            filtered_data = [d for d in self.ticker_cache.data if float(d.get('volume', 0)) >= volume_threshold]
        
        # Calculate market statistics
        total_symbols = len(filtered_data)
        gainers_count = len([d for d in filtered_data if float(d.get('priceChangePercent', 0)) > 0])
        losers_count = len([d for d in filtered_data if float(d.get('priceChangePercent', 0)) < 0])
        unchanged_count = total_symbols - gainers_count - losers_count
        
        # Calculate total market volume
        total_volume = sum(float(d.get('volume', 0)) for d in filtered_data)
        
        result = {
            "market_summary": {
                "total_symbols": total_symbols,
                "gainers": gainers_count,
                "losers": losers_count,
                "unchanged": unchanged_count,
                "total_24h_volume": total_volume
            }
        }
        
        if include_top_movers:
            top_gainers = self.ticker_cache.get_top_gainers(5)
            top_losers = self.ticker_cache.get_top_losers(5)
            
            if volume_threshold > 0:
                top_gainers = [g for g in top_gainers if float(g.get('volume', 0)) >= volume_threshold][:5]
                top_losers = [l for l in top_losers if float(l.get('volume', 0)) >= volume_threshold][:5]
            
            result["top_movers"] = {
                "top_gainers": top_gainers,
                "top_losers": top_losers
            }
        
        return result
    
    async def _handle_intelligent_tools(self, name: str, arguments: Dict[str, Any], client: BinanceClient) -> Dict[str, Any]:
        """Handle intelligent market analysis tools"""
        
        # Log tool execution
        self.logger.info(f"Executing intelligent tool: {name}")
        
        try:
            if name == "get_market_opportunities":
                limit = arguments.get("limit", 10)
                min_score = arguments.get("min_score", 25)
                direction_filter = arguments.get("direction", "ALL")
                confidence_filter = arguments.get("confidence", "ALL")
                risk_filter = arguments.get("risk_level", "ALL")
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting market opportunities directly from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("� Redis cache empty, using fallback data")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                # Apply filters
                filtered_opportunities = []
                for opp in opportunities:
                    if opp.get('total_score', 0) < min_score:
                        continue
                    if direction_filter != "ALL" and opp.get('direction') != direction_filter:
                        continue
                    if confidence_filter != "ALL" and opp.get('confidence') != confidence_filter:
                        continue
                    if risk_filter != "ALL" and opp.get('risk_level') != risk_filter:
                        continue
                    filtered_opportunities.append(opp)
                
                # Sort and limit
                filtered_opportunities.sort(key=lambda x: x.get('total_score', 0), reverse=True)
                
                # Check data source
                is_redis_data = len(opportunities) > 0 and hasattr(self, 'redis_client') and self.redis_client is not None
                
                result = {
                    "opportunities": filtered_opportunities[:limit],
                    "total_found": len(filtered_opportunities),
                    "total_available": len(opportunities),
                    "filters_applied": {
                        "min_score": min_score,
                        "direction": direction_filter,
                        "confidence": confidence_filter,
                        "risk_level": risk_filter
                    },
                    "analysis_timestamp": opportunities[0].get('timestamp') if opportunities else None,
                    "source": "redis_cache_localhost:6380" if is_redis_data else "fallback_data",
                    "redis_connection": "active" if is_redis_data else "unavailable",
                    "cache_status": "hit" if is_redis_data else "miss"
                }
                
                return result
            
            elif name == "get_token_analysis":
                symbol = arguments["symbol"].upper()
                include_context = arguments.get("include_context", True)
                
                # Get opportunities directly from Redis cache
                self.logger.info(f"🔍 Getting token analysis for {symbol} from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for token analysis")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                # Find the symbol in cached opportunities
                token_analysis = None
                for opp in opportunities:
                    if opp.get('symbol') == symbol:
                        token_analysis = opp
                        break
                
                if not token_analysis:
                    return {
                        "error": f"Symbol {symbol} not found in cached opportunities", 
                        "suggestion": "Symbol may not be actively trading or market scan may be in progress",
                        "available_symbols_sample": [opp.get('symbol') for opp in opportunities[:10]],
                        "source": "redis_cache_localhost:6380"
                    }
                
                if include_context:
                    # Add market context using cached data
                    if opportunities:
                        # Find rank among all tokens
                        symbol_rank = None
                        for i, opp in enumerate(opportunities, 1):
                            if opp['symbol'] == symbol:
                                symbol_rank = i
                                break
                        
                        token_analysis["market_context"] = {
                            "rank_among_opportunities": symbol_rank,
                            "total_analyzed": len(opportunities),
                            "percentile": round((1 - (symbol_rank - 1) / len(opportunities)) * 100, 1) if symbol_rank else None
                        }
                
                # Add source information
                is_redis_data = hasattr(self, 'redis_client') and self.redis_client is not None
                token_analysis["source"] = "redis_cache_localhost:6380" if is_redis_data else "fallback_data"
                token_analysis["redis_connection"] = "active" if is_redis_data else "unavailable"
                
                return token_analysis
            
            elif name == "get_market_dashboard":
                include_breakdown = arguments.get("include_breakdown", False)
                category_limit = arguments.get("category_limit", 5)
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting market dashboard data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for dashboard")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                if not opportunities:
                    return {"error": "No market data available", "suggestion": "Market scan may be in progress"}
                
                # Create comprehensive dashboard
                dashboard = {
                    "market_overview": {
                        "total_tokens_analyzed": len(opportunities),
                        "high_confidence_count": len([o for o in opportunities if o.get('confidence') == 'HIGH']),
                        "medium_confidence_count": len([o for o in opportunities if o.get('confidence') == 'MEDIUM']),
                        "long_signals": len([o for o in opportunities if o.get('direction') == 'LONG']),
                        "short_signals": len([o for o in opportunities if o.get('direction') == 'SHORT']),
                        "watch_signals": len([o for o in opportunities if o.get('direction') == 'WATCH']),
                        "avg_score": round(sum(o.get('total_score', 0) for o in opportunities) / len(opportunities), 2),
                        "last_updated": opportunities[0].get('timestamp') if opportunities else None
                    },
                    "categories": {
                        "top_opportunities": opportunities[:category_limit],
                        "funding_extremes": sorted([o for o in opportunities 
                                                  if o.get('score_breakdown', {}).get('funding_rate', 0) >= 4],
                                                 key=lambda x: x['score_breakdown']['funding_rate'], reverse=True)[:category_limit],
                        "volume_leaders": sorted([o for o in opportunities 
                                                if o.get('score_breakdown', {}).get('volume_spike', 0) >= 6],
                                               key=lambda x: x['score_breakdown']['volume_spike'], reverse=True)[:category_limit],
                        "volatility_squeeze": [o for o in opportunities 
                                             if o.get('score_breakdown', {}).get('volatility_squeeze', 0) >= 3][:category_limit],
                        "whale_activity": sorted([o for o in opportunities 
                                                if o.get('score_breakdown', {}).get('whale_activity', 0) >= 4],
                                               key=lambda x: x['score_breakdown']['whale_activity'], reverse=True)[:category_limit]
                    }
                }
                
                if include_breakdown:
                    dashboard["detailed_breakdown"] = opportunities[:10]
                
                # Add source information
                is_redis_data = hasattr(self, 'redis_client') and self.redis_client is not None
                
                dashboard["source"] = "redis_cache_localhost:6380" if is_redis_data else "fallback_data"
                dashboard["redis_connection"] = "active" if is_redis_data else "unavailable"
                dashboard["processing_mode"] = "vps_direct_redis"
                
                return dashboard
            
            elif name == "get_funding_extremes":
                threshold = arguments.get("threshold", 0.05)
                include_direction = arguments.get("include_direction", "BOTH")
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting funding extremes data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for funding extremes")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                funding_extremes = []
                for opp in opportunities:
                    funding_score = opp.get('score_breakdown', {}).get('funding_rate', 0)
                    direction = opp.get('direction', 'NEUTRAL')
                    
                    # Filter based on funding score (score >= 4 indicates extreme funding)
                    if funding_score >= 4:
                        if include_direction == "BOTH":
                            funding_extremes.append(opp)
                        elif include_direction == "LONG_SQUEEZE" and direction == "LONG":
                            funding_extremes.append(opp)
                        elif include_direction == "SHORT_SQUEEZE" and direction == "SHORT":
                            funding_extremes.append(opp)
                
                # Sort by funding score
                funding_extremes.sort(key=lambda x: x.get('score_breakdown', {}).get('funding_rate', 0), reverse=True)
                
                # Add squeeze analysis
                long_squeezes = [opp for opp in funding_extremes if opp.get('direction') == 'LONG']
                short_squeezes = [opp for opp in funding_extremes if opp.get('direction') == 'SHORT']
                
                return {
                    "funding_extremes": funding_extremes,
                    "squeeze_analysis": {
                        "long_squeeze_candidates": len(long_squeezes),
                        "short_squeeze_candidates": len(short_squeezes),
                        "top_long_squeeze": long_squeezes[0].get('symbol') if long_squeezes else None,
                        "top_short_squeeze": short_squeezes[0].get('symbol') if short_squeezes else None,
                        "trading_signals": {
                            "long_squeeze_trade": "SHORT (sell when over-leveraged longs get squeezed)",
                            "short_squeeze_trade": "LONG (buy when over-leveraged shorts get squeezed)"
                        }
                    },
                    "total_found": len(funding_extremes),
                    "threshold_used": threshold,
                    "direction_filter": include_direction,
                    "source": "redis_cache_localhost:6380" if hasattr(self, 'redis_client') and self.redis_client is not None else "fallback_data",
                    "redis_connection": "active" if hasattr(self, 'redis_client') and self.redis_client is not None else "unavailable",
                    "note": "Squeeze strategy: Trade OPPOSITE to squeeze direction",
                    "trading_logic": "LONG_SQUEEZE → SHORT trade | SHORT_SQUEEZE → LONG trade"
                }
            
            elif name == "get_volume_leaders":
                multiplier = arguments.get("multiplier", 2.0)
                timeframe = arguments.get("timeframe", "24h")
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting volume leaders data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for volume leaders")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                # Calculate average volume across all tokens
                all_volumes = [float(o.get('volume_24h', 0)) for o in opportunities if o.get('volume_24h')]
                avg_volume = sum(all_volumes) / len(all_volumes) if all_volumes else 0
                volume_threshold = avg_volume * multiplier
                
                # Filter tokens with volume above threshold AND high volume score
                volume_leaders = []
                for opp in opportunities:
                    volume_24h = float(opp.get('volume_24h', 0))
                    volume_score = opp.get('score_breakdown', {}).get('volume_spike', 0)
                    
                    # Must have both: volume above average * multiplier AND high volume score
                    if volume_24h >= volume_threshold and volume_score >= 4:
                        volume_leaders.append(opp)
                
                # Sort by actual 24h volume
                volume_leaders.sort(key=lambda x: float(x.get('volume_24h', 0)), reverse=True)
                
                return {
                    "volume_leaders": volume_leaders,
                    "total_found": len(volume_leaders),
                    "multiplier_threshold": multiplier,
                    "average_volume": round(avg_volume, 2),
                    "volume_threshold": round(volume_threshold, 2),
                    "timeframe": timeframe,
                    "source": "redis_cache_localhost:6380" if hasattr(self, 'redis_client') and self.redis_client is not None else "fallback_data",
                    "redis_connection": "active" if hasattr(self, 'redis_client') and self.redis_client is not None else "unavailable",
                    "note": f"Tokens with volume ≥ {multiplier}x average ({round(volume_threshold/1000000, 1)}M USDT) AND volume spike score ≥ 4"
                }
            
            elif name == "get_volatility_squeeze":
                compression_level = arguments.get("compression_level", "HIGH")
                min_volume = arguments.get("min_volume", 500000)
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting volatility squeeze data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for volatility squeeze")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                # Filter based on compression level
                min_volatility_score = {
                    "EXTREME": 5,
                    "HIGH": 4,
                    "MODERATE": 3,
                    "ALL": 1
                }.get(compression_level, 4)
                
                squeeze_candidates = []
                for opp in opportunities:
                    vol_score = opp.get('score_breakdown', {}).get('volatility_squeeze', 0)
                    volume_24h = opp.get('volume_24h', 0)
                    
                    if vol_score >= min_volatility_score and volume_24h >= min_volume:
                        squeeze_candidates.append(opp)
                
                # Sort by volatility squeeze score
                squeeze_candidates.sort(key=lambda x: x['score_breakdown']['volatility_squeeze'], reverse=True)
                
                return {
                    "volatility_squeeze_candidates": squeeze_candidates,
                    "total_found": len(squeeze_candidates),
                    "compression_level": compression_level,
                    "min_volume_filter": min_volume,
                    "source": "redis_cache_localhost:6380" if hasattr(self, 'redis_client') and self.redis_client is not None else "fallback_data",
                    "redis_connection": "active" if hasattr(self, 'redis_client') and self.redis_client is not None else "unavailable",
                    "note": "Low volatility often precedes explosive breakouts"
                }
            
            elif name == "get_whale_activity":
                min_whale_score = arguments.get("min_whale_score", 3)
                whale_direction = arguments.get("whale_direction", "ALL")
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting whale activity data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for whale activity")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                whale_tokens = []
                for opp in opportunities:
                    whale_score = opp.get('score_breakdown', {}).get('whale_activity', 0)
                    direction = opp.get('direction', 'NEUTRAL')
                    
                    if whale_score >= min_whale_score:
                        if whale_direction == "ALL":
                            whale_tokens.append(opp)
                        elif whale_direction == direction:
                            whale_tokens.append(opp)
                
                # Sort by whale activity score
                whale_tokens.sort(key=lambda x: x['score_breakdown']['whale_activity'], reverse=True)
                
                return {
                    "whale_activity_tokens": whale_tokens,
                    "total_found": len(whale_tokens),
                    "min_whale_score": min_whale_score,
                    "direction_filter": whale_direction,
                    "source": "redis_cache_localhost:6380" if hasattr(self, 'redis_client') and self.redis_client is not None else "fallback_data",
                    "redis_connection": "active" if hasattr(self, 'redis_client') and self.redis_client is not None else "unavailable",
                    "note": "Whale activity often indicates institutional interest"
                }
            
            elif name == "get_narrative_plays":
                narrative = arguments.get("narrative", "ALL")
                min_sentiment_score = arguments.get("min_sentiment_score", 1)
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting narrative plays data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for narrative plays")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                narrative_tokens = []
                for opp in opportunities:
                    sentiment_score = opp.get('score_breakdown', {}).get('sentiment', 0)
                    category_scores = opp.get('category_scores', {})
                    opp_narrative = opp.get('narrative_type', '')

                    # Dynamic narrative/category scoring logic
                    if narrative == "ALL":
                        # Include if any category score is nonzero and sentiment is high enough
                        if any(v > 0 for v in category_scores.values()) and sentiment_score >= min_sentiment_score:
                            narrative_tokens.append(opp)
                    else:
                        # Only include if this narrative/category score is nonzero and sentiment is high enough
                        if category_scores.get(narrative, 0) > 0 and sentiment_score >= min_sentiment_score:
                            narrative_tokens.append(opp)
                
                # Sort by category score (for narrative), then sentiment, then total score
                if narrative == "ALL":
                    narrative_tokens.sort(key=lambda x: (max(x.get('category_scores', {}).values(), default=0), x.get('score_breakdown', {}).get('sentiment', 0), x.get('total_score', 0)), reverse=True)
                else:
                    narrative_tokens.sort(key=lambda x: (x.get('category_scores', {}).get(narrative, 0), x.get('score_breakdown', {}).get('sentiment', 0), x.get('total_score', 0)), reverse=True)
                
                # Only include category_scores in output for clarity
                for opp in narrative_tokens:
                    if 'category_scores' not in opp:
                        opp['category_scores'] = {}
                
                return {
                    "narrative_tokens": narrative_tokens,
                    "total_found": len(narrative_tokens),
                    "narrative_filter": narrative,
                    "min_sentiment_score": min_sentiment_score,
                    "scoring_method": "Dynamic category scoring (OI/volume per category) + sentiment",
                    "source": "redis_cache_localhost:6380" if hasattr(self, 'redis_client') and self.redis_client is not None else "fallback_data",
                    "redis_connection": "active" if hasattr(self, 'redis_client') and self.redis_client is not None else "unavailable",
                    "note": "Narrative/category analytics use dynamic OI/volume scoring and sentiment. category_scores field shows per-narrative score."
                }
            
            elif name == "get_quick_scan":
                urgency = arguments.get("urgency", "NORMAL")
                
                # Get opportunities directly from Redis cache
                self.logger.info("🔍 Getting quick scan data from Redis...")
                opportunities = await self._get_market_opportunities_from_redis()
                
                # Use fallback data if Redis is empty or unavailable
                if not opportunities:
                    self.logger.warning("🔄 Redis cache empty, using fallback data for quick scan")
                    from .fallback_data import get_fallback_opportunities
                    opportunities = get_fallback_opportunities()
                
                # Filter based on urgency level
                if urgency == "IMMEDIATE":
                    # Highest priority: Score ≥ 28, HIGH confidence only
                    quick_opportunities = [o for o in opportunities 
                                         if o.get('total_score', 0) >= 28 and o.get('confidence') == 'HIGH']
                elif urgency == "URGENT":
                    # High priority: Score ≥ 25, HIGH or MEDIUM confidence
                    quick_opportunities = [o for o in opportunities 
                                         if o.get('total_score', 0) >= 25 and o.get('confidence') in ['HIGH', 'MEDIUM']]
                else:  # NORMAL
                    # Standard priority: Score ≥ 22, any confidence
                    quick_opportunities = [o for o in opportunities 
                                         if o.get('total_score', 0) >= 22]
                
                # Sort by total score
                quick_opportunities.sort(key=lambda x: x.get('total_score', 0), reverse=True)
                
                # Limit results based on urgency
                limit_map = {"IMMEDIATE": 5, "URGENT": 8, "NORMAL": 10}
                result_limit = limit_map.get(urgency, 10)
                
                # Add source information
                is_redis_data = hasattr(self, 'redis_client') and self.redis_client is not None
                
                return {
                    "quick_opportunities": quick_opportunities[:result_limit],
                    "total_found": len(quick_opportunities),
                    "urgency_level": urgency,
                    "scan_criteria": {
                        "IMMEDIATE": "Score ≥ 28, HIGH confidence only",
                        "URGENT": "Score ≥ 25, HIGH/MEDIUM confidence", 
                        "NORMAL": "Score ≥ 22, any confidence"
                    }[urgency],
                    "source": "redis_cache_localhost:6380" if is_redis_data else "fallback_data",
                    "redis_connection": "active" if is_redis_data else "unavailable",
                    "note": "Quick scan for time-sensitive opportunities"
                }
            
            else:
                return {"error": f"Unknown intelligent tool: {name}"}
                
        except Exception as e:
            # Handle any unexpected errors gracefully
            error_msg = str(e)
            return {
                "error": f"Failed to execute {name}: {error_msg}",
                "tool_name": name,
                "arguments": arguments,
                "suggestion": "Check Redis connection and ensure market monitor is running"
            }
