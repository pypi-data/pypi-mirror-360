#!/usr/bin/env python3
"""
Premium Member Key Authentication System
Handles generation, validation, and management of member keys
"""

import os
import json
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class KeyStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired" 
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class MemberKey:
    key_id: str
    key_hash: str
    member_id: str
    member_email: str
    status: KeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    max_usage: Optional[int]
    permissions: List[str]


class PremiumKeyManager:
    """Manages premium member keys with SQLite backend"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use /app/data in Docker, current directory otherwise
            if os.path.exists("/app/data"):
                db_path = "/app/data/premium_keys.db"
            else:
                db_path = "premium_keys.db"
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists and is writable"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except PermissionError:
                # Fallback to temp directory if we can't write to the preferred location
                import tempfile
                self.db_path = os.path.join(tempfile.gettempdir(), "premium_keys.db")
    
    def _init_database(self):
        """Initialize the SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_keys (
                key_id TEXT PRIMARY KEY,
                key_hash TEXT UNIQUE NOT NULL,
                member_id TEXT NOT NULL,
                member_email TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                max_usage INTEGER,
                permissions TEXT DEFAULT '[]'
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_key_hash ON member_keys(key_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_member_id ON member_keys(member_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON member_keys(status)
        """)
        
        conn.commit()
        conn.close()
    
    def generate_member_key(
        self, 
        member_id: str, 
        member_email: str,
        validity_days: int = 365,
        max_usage: Optional[int] = None,
        permissions: List[str] = None
    ) -> Tuple[str, str]:
        """
        Generate a new premium member key
        
        Returns:
            Tuple of (key_id, raw_key)
        """
        if permissions is None:
            permissions = ["premium_trading", "advanced_analytics"]
        
        # Generate a cryptographically secure random key
        raw_key = self._generate_secure_key()
        key_hash = self._hash_key(raw_key)
        key_id = self._generate_key_id()
        
        expires_at = datetime.now() + timedelta(days=validity_days) if validity_days > 0 else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO member_keys 
            (key_id, key_hash, member_id, member_email, status, expires_at, max_usage, permissions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key_id, key_hash, member_id, member_email, 
            KeyStatus.ACTIVE.value, expires_at, max_usage, json.dumps(permissions)
        ))
        
        conn.commit()
        conn.close()
        
        return key_id, raw_key
    
    def validate_key(self, raw_key: str) -> Optional[MemberKey]:
        """Validate a member key and return member info if valid"""
        key_hash = self._hash_key(raw_key)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT key_id, key_hash, member_id, member_email, status, 
                   created_at, expires_at, last_used_at, usage_count, max_usage, permissions
            FROM member_keys 
            WHERE key_hash = ?
        """, (key_hash,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        member_key = MemberKey(
            key_id=row[0],
            key_hash=row[1], 
            member_id=row[2],
            member_email=row[3],
            status=KeyStatus(row[4]),
            created_at=datetime.fromisoformat(row[5]) if row[5] else None,
            expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
            last_used_at=datetime.fromisoformat(row[7]) if row[7] else None,
            usage_count=row[8],
            max_usage=row[9],
            permissions=json.loads(row[10]) if row[10] else []
        )
        
        # Check if key is valid
        if not self._is_key_valid(member_key):
            conn.close()
            return None
        
        # Update usage tracking
        cursor.execute("""
            UPDATE member_keys 
            SET last_used_at = CURRENT_TIMESTAMP, usage_count = usage_count + 1
            WHERE key_hash = ?
        """, (key_hash,))
        
        conn.commit()
        conn.close()
        
        return member_key
    
    def _is_key_valid(self, member_key: MemberKey) -> bool:
        """Check if a member key is valid for use"""
        # Check status
        if member_key.status != KeyStatus.ACTIVE:
            return False
        
        # Check expiration
        if member_key.expires_at and datetime.now() > member_key.expires_at:
            return False
        
        # Check usage limits
        if member_key.max_usage and member_key.usage_count >= member_key.max_usage:
            return False
        
        return True
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke a member key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE member_keys 
            SET status = ? 
            WHERE key_id = ?
        """, (KeyStatus.REVOKED.value, key_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def list_member_keys(self, member_id: Optional[str] = None) -> List[MemberKey]:
        """List all member keys, optionally filtered by member_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if member_id:
            cursor.execute("""
                SELECT key_id, key_hash, member_id, member_email, status,
                       created_at, expires_at, last_used_at, usage_count, max_usage, permissions
                FROM member_keys 
                WHERE member_id = ?
                ORDER BY created_at DESC
            """, (member_id,))
        else:
            cursor.execute("""
                SELECT key_id, key_hash, member_id, member_email, status,
                       created_at, expires_at, last_used_at, usage_count, max_usage, permissions
                FROM member_keys 
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        keys = []
        for row in rows:
            keys.append(MemberKey(
                key_id=row[0],
                key_hash=row[1], 
                member_id=row[2],
                member_email=row[3],
                status=KeyStatus(row[4]),
                created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                expires_at=datetime.fromisoformat(row[6]) if row[6] else None,
                last_used_at=datetime.fromisoformat(row[7]) if row[7] else None,
                usage_count=row[8],
                max_usage=row[9],
                permissions=json.loads(row[10]) if row[10] else []
            ))
        
        return keys
    
    def get_key_stats(self) -> Dict:
        """Get statistics about member keys"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM member_keys")
        total_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM member_keys WHERE status = 'active'")
        active_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM member_keys WHERE status = 'revoked'")
        revoked_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM member_keys WHERE expires_at < CURRENT_TIMESTAMP")
        expired_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(usage_count) FROM member_keys")
        total_usage = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "revoked_keys": revoked_keys,
            "expired_keys": expired_keys,
            "total_usage": total_usage
        }
    
    def cleanup_expired_keys(self) -> int:
        """Mark expired keys as expired and return count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE member_keys 
            SET status = ? 
            WHERE expires_at < CURRENT_TIMESTAMP AND status = ?
        """, (KeyStatus.EXPIRED.value, KeyStatus.ACTIVE.value))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def _generate_secure_key(self) -> str:
        """Generate a cryptographically secure member key"""
        # Generate 32 bytes of random data and encode as hex
        random_bytes = secrets.token_bytes(32)
        timestamp = str(int(datetime.now().timestamp()))
        
        # Combine with timestamp and create final key
        combined = random_bytes + timestamp.encode()
        key_hash = hashlib.sha256(combined).hexdigest()
        
        # Format as premium key with prefix
        return f"pmk_{key_hash[:32]}"
    
    def _hash_key(self, raw_key: str) -> str:
        """Hash a raw key for secure storage"""
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def _generate_key_id(self) -> str:
        """Generate a unique key ID"""
        return f"key_{secrets.token_hex(8)}"


# Global key manager instance
_key_manager = None

def get_key_manager() -> PremiumKeyManager:
    """Get the global key manager instance"""
    global _key_manager
    if _key_manager is None:
        # Let PremiumKeyManager choose the right path
        db_path = os.getenv("PREMIUM_KEYS_DB", None)
        _key_manager = PremiumKeyManager(db_path)
    return _key_manager


def validate_member_key(raw_key: str) -> Optional[MemberKey]:
    """Convenience function to validate a member key"""
    return get_key_manager().validate_key(raw_key)


def require_premium_access(func):
    """Decorator to require premium member key validation"""
    def wrapper(self, *args, **kwargs):
        member_key = getattr(self, '_member_key', None)
        if not member_key:
            raise ValueError("Premium access required - no valid member key provided")
        
        return func(self, *args, **kwargs)
    
    return wrapper
