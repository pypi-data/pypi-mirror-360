#!/usr/bin/env python3
"""
Premium Futures MCP Public API
Public endpoints for market data access with premium member key authentication
"""
import os
import json
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


class MarketOpportunityResponse(BaseModel):
    """Response model for market opportunities"""
    opportunities: List[Dict[str, Any]]
    total_analyzed: int
    timestamp: str
    cache_version: str
    metadata: Optional[Dict[str, Any]] = None


class MarketSummaryResponse(BaseModel):
    """Response model for market summary"""
    total_opportunities: int
    high_confidence: int
    long_signals: int
    short_signals: int
    watch_signals: int
    avg_score: float
    top_5: List[Dict[str, Any]]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: str


class PremiumPublicAPI:
    """Public API for premium market data access"""
    
    def __init__(self, 
                 key_server_url: str = "http://localhost:8080",
                 data_path: str = "/root/premium_futures_mcp/redis_cache_exports"):
        
        self.app = FastAPI(
            title="Premium Futures MCP Public API",
            description="Public access to premium market analysis data",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.key_server_url = key_server_url
        self.data_path = Path(data_path)
        self.security = HTTPBearer(description="Premium Member Key Authentication")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on your needs
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    async def _validate_premium_key(self, 
                                  credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """Validate premium member key with key server"""
        try:
            # Extract the key from Bearer token
            member_key = credentials.credentials
            
            # Validate key with the key server
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.key_server_url}/validate-key",
                    json={"member_key": member_key}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid premium member key",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                validation_result = response.json()
                
                if not validation_result.get("valid", False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Premium member key is invalid or expired",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                return validation_result
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Key validation service unavailable"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def _load_json_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from exports directory"""
        try:
            file_path = self.data_path / filename
            if not file_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Data file {filename} not found"
                )
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return data
            
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid JSON data format"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading data: {str(e)}"
            )
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", 
                     response_model=APIResponse,
                     tags=["General"])
        async def root():
            """API root endpoint with service information"""
            return APIResponse(
                success=True,
                data={
                    "service": "Premium Futures MCP Public API",
                    "version": "1.0.0",
                    "description": "Access premium market analysis data with member key",
                    "endpoints": [
                        "/market-opportunities",
                        "/market-summary", 
                        "/health"
                    ],
                    "authentication": "Bearer token with premium member key required"
                },
                message="Service is running",
                timestamp=datetime.utcnow().isoformat()
            )
        
        @self.app.get("/health", 
                     tags=["General"])
        async def health_check():
            """Health check endpoint"""
            try:
                # Check key server connectivity
                async with httpx.AsyncClient(timeout=5.0) as client:
                    key_server_response = await client.get(f"{self.key_server_url}/")
                    key_server_status = "up" if key_server_response.status_code == 200 else "down"
            except:
                key_server_status = "down"
            
            # Check data files
            opportunities_exists = (self.data_path / "market_opportunities.json").exists()
            summary_exists = (self.data_path / "market_summary.json").exists()
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "key_server": key_server_status,
                    "data_files": {
                        "market_opportunities": "available" if opportunities_exists else "missing",
                        "market_summary": "available" if summary_exists else "missing"
                    }
                }
            }
        
        @self.app.get("/market-opportunities",
                     response_model=MarketOpportunityResponse,
                     tags=["Market Data"])
        async def get_market_opportunities(
            key_validation: dict = Depends(self._validate_premium_key),
            limit: Optional[int] = None,
            min_score: Optional[float] = None,
            direction: Optional[str] = None
        ):
            """
            Get market opportunities data
            
            - **limit**: Maximum number of opportunities to return
            - **min_score**: Minimum score filter (0-50)
            - **direction**: Filter by direction (LONG_PRIORITY, SHORT_PRIORITY, WATCH)
            """
            
            # Load market opportunities data
            data = self._load_json_data("market_opportunities.json")
            opportunities = data.get("value", {}).get("opportunities", [])
            
            # Apply filters
            if min_score is not None:
                opportunities = [
                    opp for opp in opportunities 
                    if opp.get("total_score", 0) >= min_score
                ]
            
            if direction:
                opportunities = [
                    opp for opp in opportunities 
                    if opp.get("direction", "").upper() == direction.upper()
                ]
            
            if limit:
                opportunities = opportunities[:limit]
            
            return MarketOpportunityResponse(
                opportunities=opportunities,
                total_analyzed=data.get("value", {}).get("total_analyzed", len(opportunities)),
                timestamp=data.get("value", {}).get("timestamp", datetime.utcnow().isoformat()),
                cache_version=data.get("value", {}).get("cache_version", "1.0"),
                metadata={
                    "member_id": key_validation.get("member_id"),
                    "filters_applied": {
                        "limit": limit,
                        "min_score": min_score,
                        "direction": direction
                    },
                    "data_metadata": data.get("metadata", {})
                }
            )
        
        @self.app.get("/market-summary",
                     response_model=MarketSummaryResponse, 
                     tags=["Market Data"])
        async def get_market_summary(
            key_validation: dict = Depends(self._validate_premium_key)
        ):
            """
            Get market summary data with top opportunities
            """
            
            # Load market summary data
            data = self._load_json_data("market_summary.json")
            summary_data = data.get("value", {})
            
            return MarketSummaryResponse(
                total_opportunities=summary_data.get("total_opportunities", 0),
                high_confidence=summary_data.get("high_confidence", 0),
                long_signals=summary_data.get("long_signals", 0),
                short_signals=summary_data.get("short_signals", 0),
                watch_signals=summary_data.get("watch_signals", 0),
                avg_score=summary_data.get("avg_score", 0.0),
                top_5=summary_data.get("top_5", []),
                timestamp=summary_data.get("timestamp", datetime.utcnow().isoformat()),
                metadata={
                    "member_id": key_validation.get("member_id"),
                    "data_metadata": data.get("metadata", {})
                }
            )
        
        @self.app.get("/market-opportunities/{symbol}",
                     tags=["Market Data"])
        async def get_symbol_opportunity(
            symbol: str,
            key_validation: dict = Depends(self._validate_premium_key)
        ):
            """
            Get specific symbol opportunity data
            
            - **symbol**: Trading pair symbol (e.g., BTCUSDT, ETHUSDT)
            """
            
            # Load market opportunities data
            data = self._load_json_data("market_opportunities.json")
            opportunities = data.get("value", {}).get("opportunities", [])
            
            # Find symbol
            symbol_data = None
            for opp in opportunities:
                if opp.get("symbol", "").upper() == symbol.upper():
                    symbol_data = opp
                    break
            
            if not symbol_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Symbol {symbol} not found in current opportunities"
                )
            
            return APIResponse(
                success=True,
                data=symbol_data,
                message=f"Opportunity data for {symbol}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def run(self, host: str = "0.0.0.0", port: int = 8081, reload: bool = False):
        """Run the public API server"""
        print(f"🚀 Starting Premium Futures MCP Public API...")
        print(f"📡 Server will be available at: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🔐 Key Server: {self.key_server_url}")
        print(f"📊 Data Path: {self.data_path}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )


def create_public_api() -> FastAPI:
    """Factory function to create the public API app"""
    api = PremiumPublicAPI()
    return api.app


def main():
    """CLI entry point for the public API"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Premium Futures MCP Public API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8081, help="Port to bind to")
    parser.add_argument("--key-server", default="http://localhost:8080", 
                       help="Premium key server URL")
    parser.add_argument("--data-path", 
                       default="/root/premium_futures_mcp/redis_cache_exports",
                       help="Path to JSON data files")
    parser.add_argument("--reload", action="store_true", 
                       help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    api = PremiumPublicAPI(
        key_server_url=args.key_server,
        data_path=args.data_path
    )
    api.run(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
