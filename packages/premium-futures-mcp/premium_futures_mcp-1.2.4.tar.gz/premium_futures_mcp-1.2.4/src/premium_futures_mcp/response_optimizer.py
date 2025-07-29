#!/usr/bin/env python3
"""
Response Optimizer for reducing token usage in MCP responses
"""

from typing import Any, Dict, List
from decimal import Decimal

class ResponseOptimizer:
    """Optimizes API responses to reduce token consumption"""
    
    @staticmethod
    def optimize_positions(positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize position data by removing unnecessary fields and formatting"""
        optimized = []
        for pos in positions:
            # Only include essential fields
            optimized_pos = {
                "symbol": pos.get("symbol"),
                "size": float(pos.get("positionAmt", 0)),
                "side": "LONG" if float(pos.get("positionAmt", 0)) > 0 else "SHORT",
                "entry_price": float(pos.get("entryPrice", 0)),
                "mark_price": float(pos.get("markPrice", 0)),
                "pnl": float(pos.get("unRealizedProfit", 0)),
                "pnl_pct": float(pos.get("percentage", 0)) if pos.get("percentage") else 0,
                "margin": float(pos.get("initialMargin", 0)),
                "leverage": int(float(pos.get("leverage", 1)))
            }
            optimized.append(optimized_pos)
        return optimized
    
    @staticmethod
    def optimize_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize order data"""
        optimized = []
        for order in orders:
            optimized_order = {
                "id": order.get("orderId"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "qty": float(order.get("origQty", 0)),
                "price": float(order.get("price", 0)),
                "status": order.get("status"),
                "time": order.get("time")
            }
            optimized.append(optimized_order)
        return optimized
    
    @staticmethod
    def optimize_balance(balance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize balance data to show only non-zero balances"""
        non_zero_balances = []
        total_wallet_balance = 0
        total_unrealized_pnl = 0
        
        if not isinstance(balance_data, list):
            return {
                "error": f"Expected list but got {type(balance_data).__name__}",
                "total_wallet_balance": 0,
                "total_unrealized_pnl": 0,
                "assets": [],
                "asset_count": 0
            }
        
        for i, bal in enumerate(balance_data):
            try:
                # Validate that bal is a dict-like object
                if not isinstance(bal, dict) and not hasattr(bal, 'get'):
                    continue
                
                # Safely extract values with multiple fallbacks
                def safe_float_extract(obj, key, default=0):
                    try:
                        if hasattr(obj, 'get'):
                            value = obj.get(key, default)
                        elif isinstance(obj, dict):
                            value = obj.get(key, default)
                        else:
                            return default
                        
                        if value is None or value == "":
                            return default
                        return float(value)
                    except (ValueError, TypeError, AttributeError):
                        return default
                
                def safe_string_extract(obj, key, default=""):
                    try:
                        if hasattr(obj, 'get'):
                            value = obj.get(key, default)
                        elif isinstance(obj, dict):
                            value = obj.get(key, default)
                        else:
                            return default
                        return str(value) if value is not None else default
                    except (AttributeError, TypeError):
                        return default
                
                # Extract values using correct field names
                wallet_balance = safe_float_extract(bal, "balance", 0)
                unrealized_pnl = safe_float_extract(bal, "crossUnPnl", 0)
                available_balance = safe_float_extract(bal, "availableBalance", 0)
                cross_wallet_balance = safe_float_extract(bal, "crossWalletBalance", 0)
                max_withdraw = safe_float_extract(bal, "maxWithdrawAmount", 0)
                
                # Fallback to account info field names
                if wallet_balance == 0:
                    wallet_balance = safe_float_extract(bal, "walletBalance", 0)
                if unrealized_pnl == 0:
                    unrealized_pnl = safe_float_extract(bal, "unrealizedProfit", 0)
                
                asset_name = safe_string_extract(bal, "asset", "UNKNOWN")
                
                # Check if this balance entry has any non-zero values (including all balance fields)
                if (wallet_balance != 0 or unrealized_pnl != 0 or available_balance != 0 or 
                    cross_wallet_balance != 0 or max_withdraw != 0):
                    
                    non_zero_balances.append({
                        "asset": asset_name,
                        "balance": wallet_balance,
                        "available": available_balance,
                        "pnl": unrealized_pnl
                    })
                
                total_wallet_balance += wallet_balance
                total_unrealized_pnl += unrealized_pnl
                
            except Exception as e:
                # Skip problematic entries silently
                continue
        
        return {
            "total_balance": total_wallet_balance,
            "total_pnl": total_unrealized_pnl,
            "assets": non_zero_balances
        }
    
    @staticmethod
    def optimize_ticker_data(tickers: List[Dict[str, Any]], limit: int = 20) -> List[Dict[str, Any]]:
        """Optimize ticker data for top movers"""
        optimized = []
        for ticker in tickers[:limit]:
            optimized_ticker = {
                "symbol": ticker.get("symbol"),
                "price": float(ticker.get("lastPrice", 0)),
                "change": float(ticker.get("priceChange", 0)),
                "change_pct": float(ticker.get("priceChangePercent", 0)),
                "volume": float(ticker.get("volume", 0))
            }
            optimized.append(optimized_ticker)
        return optimized
