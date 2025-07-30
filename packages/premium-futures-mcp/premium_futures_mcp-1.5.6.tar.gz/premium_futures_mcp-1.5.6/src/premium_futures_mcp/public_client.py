"""
Public Binance Client for Market Data
No authentication required - for public market data only
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
import json


class PublicBinanceClient:
    """Public Binance client for market data - no API keys required"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.base_url = "https://fapi.binance.com" if not testnet else "https://testnet.binancefuture.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=50)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a public API request to Binance"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(f"API error {response.status}: {error_text}")
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                    
        except TimeoutError as e:
            self.logger.error(f"Timeout for {method} {url}: {e}")
            raise Exception("Request timeout")
        except Exception as e:
            self.logger.error(f"Request error for {method} {url}: {e}")
            raise
    
    # Public Market Data Methods
    
    async def get_all_tickers(self) -> list:
        """Get 24hr ticker data for all symbols"""
        return await self._make_request("GET", "/fapi/v1/ticker/24hr")
    
    async def get_ticker(self, symbol: str) -> dict:
        """Get 24hr ticker data for a specific symbol"""
        result = await self._make_request("GET", "/fapi/v1/ticker/24hr", {"symbol": symbol})
        return result[0] if isinstance(result, list) else result
    
    async def get_exchange_info(self) -> dict:
        """Get exchange trading rules and symbol information"""
        return await self._make_request("GET", "/fapi/v1/exchangeInfo")
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> dict:
        """Get order book for a symbol"""
        return await self._make_request("GET", "/fapi/v1/depth", {"symbol": symbol, "limit": limit})
    
    async def get_klines(self, symbol: str, interval: str, limit: int = 500, **kwargs) -> list:
        """Get kline/candlestick data"""
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        params.update(kwargs)
        return await self._make_request("GET", "/fapi/v1/klines", params)
    
    async def get_mark_price(self, symbol: str = None) -> dict:
        """Get mark price and funding rate"""
        params = {"symbol": symbol} if symbol else {}
        return await self._make_request("GET", "/fapi/v1/premiumIndex", params)
    
    async def get_funding_rate_history(self, symbol: str = None, **kwargs) -> list:
        """Get funding rate history"""
        params = kwargs.copy()
        if symbol:
            params["symbol"] = symbol
        return await self._make_request("GET", "/fapi/v1/fundingRate", params)
    
    async def get_open_interest(self, symbol: str) -> dict:
        """Get open interest for a symbol"""
        return await self._make_request("GET", "/fapi/v1/openInterest", {"symbol": symbol})
    
    async def get_open_interest_stats(self, symbol: str, period: str = "5m", limit: int = 30) -> List[Dict[str, Any]]:
        """
        Get Open Interest Statistics
        
        Args:
            symbol: Trading pair symbol
            period: Period for statistics (5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d)
            limit: Number of records to return (max 500, default 30)
        """
        endpoint = "/futures/data/openInterestHist"
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }
        
        return await self._make_request("GET", endpoint, params)
    
    async def get_top_long_short_account_ratio(self, symbol: str, period: str = "5m", limit: int = 30) -> List[Dict[str, Any]]:
        """Get top trader long/short account ratio statistics"""
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }
        return await self._make_request("GET", "/futures/data/topLongShortAccountRatio", params)
    
    async def get_top_long_short_position_ratio(self, symbol: str, period: str = "5m", limit: int = 30) -> List[Dict[str, Any]]:
        """Get top trader long/short position ratio statistics"""
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }
        return await self._make_request("GET", "/futures/data/topLongShortPositionRatio", params)
    
    async def get_taker_buy_sell_volume(self, symbol: str, period: str, **kwargs) -> list:
        """Get taker buy/sell volume"""
        params = {"symbol": symbol, "period": period}
        params.update(kwargs)
        return await self._make_request("GET", "/futures/data/takerlongshortRatio", params)


class PublicMarketDataCache:
    """Simple in-memory cache for public market data"""
    
    def __init__(self, cache_duration: int = 60):
        self.cache_duration = cache_duration  # seconds
        self._cache: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key"""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{endpoint}?{param_str}"
        return endpoint
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        """Get cached data"""
        key = self._get_cache_key(endpoint, params)
        
        if key in self._cache:
            cache_entry = self._cache[key]
            import time
            if time.time() - cache_entry['timestamp'] < self.cache_duration:
                return cache_entry['data']
            else:
                # Cache expired
                del self._cache[key]
        
        return None
    
    def set(self, endpoint: str, data: Any, params: Dict = None):
        """Set cached data"""
        key = self._get_cache_key(endpoint, params)
        import time
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'entries': len(self._cache),
            'cache_duration': self.cache_duration
        }
