#!/usr/bin/env python3
"""
Premium Member Key Bot API
RESTful API for automated member key generation and management
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import uvicorn

from .auth import PremiumKeyManager, KeyStatus, MemberKey


# Pydantic models for API requests/responses
class KeyGenerationRequest(BaseModel):
    member_id: str
    member_email: EmailStr
    validity_days: int = 365
    max_usage: Optional[int] = None
    permissions: List[str] = ["premium_trading", "advanced_analytics"]


class KeyGenerationResponse(BaseModel):
    success: bool
    key_id: str
    member_key: str
    member_id: str
    member_email: str
    validity_days: int
    max_usage: Optional[int]
    permissions: List[str]
    expires_at: Optional[str]


class KeyValidationRequest(BaseModel):
    member_key: str


class KeyValidationResponse(BaseModel):
    valid: bool
    key_id: Optional[str] = None
    member_id: Optional[str] = None
    member_email: Optional[str] = None
    status: Optional[str] = None
    usage_count: Optional[int] = None
    permissions: Optional[List[str]] = None


class KeyListResponse(BaseModel):
    keys: List[Dict]
    total_count: int


class KeyStatsResponse(BaseModel):
    total_keys: int
    active_keys: int
    revoked_keys: int
    expired_keys: int
    total_usage: int


class PremiumKeyBot:
    """Bot API for premium member key management"""
    
    def __init__(self, admin_token: str = None):
        self.app = FastAPI(
            title="Premium Futures MCP Key Bot",
            description="Automated member key generation and management API",
            version="1.0.0"
        )
        self.key_manager = PremiumKeyManager()
        self.admin_token = admin_token or os.getenv("PREMIUM_BOT_ADMIN_TOKEN", "admin-token-change-me")
        self.security = HTTPBearer()
        
        self._setup_routes()
    
    def _verify_admin_token(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        """Verify admin authentication token"""
        if credentials.credentials != self.admin_token:
            raise HTTPException(status_code=401, detail="Invalid admin token")
        return credentials.credentials
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/", tags=["General"])
        async def root():
            """API health check"""
            return {
                "service": "Premium Futures MCP Key Bot",
                "status": "online",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/generate-key", response_model=KeyGenerationResponse, tags=["Key Management"])
        async def generate_key(
            request: KeyGenerationRequest,
            token: str = Depends(self._verify_admin_token)
        ):
            """Generate a new premium member key"""
            try:
                key_id, raw_key = self.key_manager.generate_member_key(
                    member_id=request.member_id,
                    member_email=request.member_email,
                    validity_days=request.validity_days,
                    max_usage=request.max_usage,
                    permissions=request.permissions
                )
                
                # Calculate expiration date
                expires_at = None
                if request.validity_days > 0:
                    from datetime import timedelta
                    expires_at = (datetime.now() + timedelta(days=request.validity_days)).isoformat()
                
                return KeyGenerationResponse(
                    success=True,
                    key_id=key_id,
                    member_key=raw_key,
                    member_id=request.member_id,
                    member_email=request.member_email,
                    validity_days=request.validity_days,
                    max_usage=request.max_usage,
                    permissions=request.permissions,
                    expires_at=expires_at
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")
        
        @self.app.post("/validate-key", response_model=KeyValidationResponse, tags=["Key Management"])
        async def validate_key(request: KeyValidationRequest):
            """Validate a premium member key"""
            try:
                member_key = self.key_manager.validate_key(request.member_key)
                
                if member_key:
                    return KeyValidationResponse(
                        valid=True,
                        key_id=member_key.key_id,
                        member_id=member_key.member_id,
                        member_email=member_key.member_email,
                        status=member_key.status.value,
                        usage_count=member_key.usage_count,
                        permissions=member_key.permissions
                    )
                else:
                    return KeyValidationResponse(valid=False)
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Key validation failed: {str(e)}")
        
        @self.app.get("/keys", response_model=KeyListResponse, tags=["Key Management"])
        async def list_keys(
            member_id: Optional[str] = None,
            token: str = Depends(self._verify_admin_token)
        ):
            """List premium member keys"""
            try:
                keys = self.key_manager.list_member_keys(member_id)
                
                # Convert to dict format for JSON response
                keys_data = []
                for key in keys:
                    key_dict = {
                        "key_id": key.key_id,
                        "member_id": key.member_id,
                        "member_email": key.member_email,
                        "status": key.status.value,
                        "created_at": key.created_at.isoformat() if key.created_at else None,
                        "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                        "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                        "usage_count": key.usage_count,
                        "max_usage": key.max_usage,
                        "permissions": key.permissions
                    }
                    keys_data.append(key_dict)
                
                return KeyListResponse(
                    keys=keys_data,
                    total_count=len(keys_data)
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")
        
        @self.app.delete("/keys/{key_id}", tags=["Key Management"])
        async def revoke_key(
            key_id: str,
            token: str = Depends(self._verify_admin_token)
        ):
            """Revoke a premium member key"""
            try:
                success = self.key_manager.revoke_key(key_id)
                
                if success:
                    return {"success": True, "message": f"Key {key_id} revoked successfully"}
                else:
                    raise HTTPException(status_code=404, detail=f"Key {key_id} not found")
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to revoke key: {str(e)}")
        
        @self.app.get("/stats", response_model=KeyStatsResponse, tags=["Statistics"])
        async def get_stats(token: str = Depends(self._verify_admin_token)):
            """Get premium member key statistics"""
            try:
                stats = self.key_manager.get_key_stats()
                return KeyStatsResponse(**stats)
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
        
        @self.app.post("/cleanup", tags=["Maintenance"])
        async def cleanup_expired_keys(token: str = Depends(self._verify_admin_token)):
            """Clean up expired member keys"""
            try:
                count = self.key_manager.cleanup_expired_keys()
                return {"success": True, "cleaned_up": count, "message": f"Cleaned up {count} expired keys"}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
        
        # Batch operations
        @self.app.post("/batch/generate-keys", tags=["Batch Operations"])
        async def batch_generate_keys(
            requests: List[KeyGenerationRequest],
            token: str = Depends(self._verify_admin_token)
        ):
            """Generate multiple premium member keys in batch"""
            if len(requests) > 100:
                raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 keys")
            
            results = []
            errors = []
            
            for i, request in enumerate(requests):
                try:
                    key_id, raw_key = self.key_manager.generate_member_key(
                        member_id=request.member_id,
                        member_email=request.member_email,
                        validity_days=request.validity_days,
                        max_usage=request.max_usage,
                        permissions=request.permissions
                    )
                    
                    expires_at = None
                    if request.validity_days > 0:
                        from datetime import timedelta
                        expires_at = (datetime.now() + timedelta(days=request.validity_days)).isoformat()
                    
                    results.append({
                        "index": i,
                        "success": True,
                        "key_id": key_id,
                        "member_key": raw_key,
                        "member_id": request.member_id,
                        "member_email": request.member_email,
                        "expires_at": expires_at
                    })
                    
                except Exception as e:
                    errors.append({
                        "index": i,
                        "member_id": request.member_id,
                        "error": str(e)
                    })
            
            return {
                "total_requests": len(requests),
                "successful": len(results),
                "failed": len(errors),
                "results": results,
                "errors": errors
            }
    
    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False):
        """Run the bot API server"""
        print(f"🚀 Starting Premium Key Bot API server...")
        print(f"📡 Server will be available at: http://{host}:{port}")
        print(f"📚 API Documentation: http://{host}:{port}/docs")
        print(f"🔐 Admin token: {self.admin_token[:8]}...")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )


def create_bot_app() -> FastAPI:
    """Factory function to create the bot app"""
    bot = PremiumKeyBot()
    return bot.app


def main():
    """CLI entry point for the bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Premium Futures MCP Key Bot API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--admin-token", help="Admin authentication token")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    # Set admin token if provided
    if args.admin_token:
        os.environ["PREMIUM_BOT_ADMIN_TOKEN"] = args.admin_token
    
    bot = PremiumKeyBot()
    bot.run(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
