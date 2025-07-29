#!/usr/bin/env python3
"""
Remote Authentication for Premium MCP
Validates member keys against your centralized API
"""

import os
import json
import httpx
from typing import Optional
from datetime import datetime, timedelta
import asyncio


class RemoteKeyValidator:
    """Validates member keys against remote API"""
    
    def __init__(self, validation_url: str = None, cache_duration: int = 300):
        self.validation_url = validation_url or os.getenv(
            "PREMIUM_KEY_VALIDATION_URL", 
            "http://188.166.184.242:8080/validate-key"
        )
        self.cache_duration = cache_duration
        self._cache = {}
    
    async def validate_key(self, member_key: str) -> Optional[dict]:
        """Validate member key against remote API with caching"""
        
        # Check cache first
        cache_key = f"key_{member_key[:16]}"  # Use partial key for cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_duration:
                return cached_data
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.validation_url,
                    json={"member_key": member_key},
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Premium-Futures-MCP/1.0"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        # Cache valid result
                        self._cache[cache_key] = (data, datetime.now())
                        return data
                
                return None
                
        except Exception as e:
            print(f"Key validation error: {e}")
            return None
    
    def clear_cache(self):
        """Clear validation cache"""
        self._cache.clear()


# Simpler validation for PyPI package
async def validate_premium_key(member_key: str) -> bool:
    """
    Simple key validation for PyPI distributed package
    
    This approach allows the package to validate keys without
    requiring users to connect to your private server
    """
    validator = RemoteKeyValidator()
    result = await validator.validate_key(member_key)
    return result is not None and result.get("valid", False)


# Usage in server.py
async def require_premium_access(member_key: str):
    """Decorator/middleware to require premium access"""
    if not member_key:
        raise ValueError("Premium member key required")
    
    is_valid = await validate_premium_key(member_key)
    if not is_valid:
        raise ValueError("Invalid or expired premium member key")
    
    return True
