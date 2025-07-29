#!/usr/bin/env python3
"""
Premium Member Key Management CLI Tool
Command-line interface for generating and managing premium member keys
"""

import argparse
import sys
import json
from datetime import datetime
from typing import Optional
from .auth import PremiumKeyManager, KeyStatus


class KeyManagerCLI:
    """Command-line interface for key management"""
    
    def __init__(self):
        self.key_manager = PremiumKeyManager()
    
    def generate_key(self, args):
        """Generate a new member key"""
        try:
            key_id, raw_key = self.key_manager.generate_member_key(
                member_id=args.member_id,
                member_email=args.email,
                validity_days=args.validity_days,
                max_usage=args.max_usage,
                permissions=args.permissions.split(',') if args.permissions else None
            )
            
            print(f"✅ Successfully generated premium member key!")
            print(f"Key ID: {key_id}")
            print(f"Member Key: {raw_key}")
            print(f"Member ID: {args.member_id}")
            print(f"Email: {args.email}")
            print(f"Valid for: {args.validity_days} days")
            
            if args.max_usage:
                print(f"Usage limit: {args.max_usage}")
            
            print("\n⚠️  IMPORTANT: Save this key securely - it cannot be retrieved again!")
            print("The member should set this as BINANCE_MCP_MEMBER_KEY environment variable")
            
        except Exception as e:
            print(f"❌ Error generating key: {e}")
            sys.exit(1)
    
    def validate_key(self, args):
        """Validate a member key"""
        try:
            member_key = self.key_manager.validate_key(args.key)
            
            if member_key:
                print(f"✅ Key is VALID")
                print(f"Key ID: {member_key.key_id}")
                print(f"Member ID: {member_key.member_id}")
                print(f"Email: {member_key.member_email}")
                print(f"Status: {member_key.status.value}")
                print(f"Created: {member_key.created_at}")
                print(f"Usage count: {member_key.usage_count}")
                
                if member_key.expires_at:
                    print(f"Expires: {member_key.expires_at}")
                
                if member_key.max_usage:
                    print(f"Usage limit: {member_key.max_usage}")
                
                print(f"Permissions: {', '.join(member_key.permissions)}")
            else:
                print("❌ Key is INVALID or EXPIRED")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error validating key: {e}")
            sys.exit(1)
    
    def list_keys(self, args):
        """List member keys"""
        try:
            keys = self.key_manager.list_member_keys(args.member_id)
            
            if not keys:
                print("No keys found")
                return
            
            print(f"Found {len(keys)} key(s):")
            print("-" * 80)
            
            for key in keys:
                status_emoji = {
                    KeyStatus.ACTIVE: "🟢",
                    KeyStatus.EXPIRED: "🟡", 
                    KeyStatus.REVOKED: "🔴",
                    KeyStatus.SUSPENDED: "🟠"
                }.get(key.status, "⚪")
                
                print(f"{status_emoji} {key.key_id}")
                print(f"  Member: {key.member_id} ({key.member_email})")
                print(f"  Status: {key.status.value}")
                print(f"  Created: {key.created_at}")
                print(f"  Usage: {key.usage_count}" + (f"/{key.max_usage}" if key.max_usage else ""))
                
                if key.expires_at:
                    print(f"  Expires: {key.expires_at}")
                
                if key.last_used_at:
                    print(f"  Last used: {key.last_used_at}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error listing keys: {e}")
            sys.exit(1)
    
    def revoke_key(self, args):
        """Revoke a member key"""
        try:
            success = self.key_manager.revoke_key(args.key_id)
            
            if success:
                print(f"✅ Successfully revoked key: {args.key_id}")
            else:
                print(f"❌ Key not found: {args.key_id}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error revoking key: {e}")
            sys.exit(1)
    
    def stats(self, args):
        """Show key statistics"""
        try:
            stats = self.key_manager.get_key_stats()
            
            print("📊 Premium Member Key Statistics")
            print("-" * 40)
            print(f"Total keys: {stats['total_keys']}")
            print(f"Active keys: {stats['active_keys']} 🟢")
            print(f"Revoked keys: {stats['revoked_keys']} 🔴")
            print(f"Expired keys: {stats['expired_keys']} 🟡")
            print(f"Total API usage: {stats['total_usage']:,}")
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            sys.exit(1)
    
    def cleanup(self, args):
        """Clean up expired keys"""
        try:
            count = self.key_manager.cleanup_expired_keys()
            print(f"✅ Cleaned up {count} expired key(s)")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Premium Futures MCP Key Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a key for a new member
  premium-key-manager generate --member-id "user123" --email "user@example.com"
  
  # Generate a key with 30-day validity and 1000 usage limit
  premium-key-manager generate --member-id "user456" --email "user@example.com" \\
    --validity-days 30 --max-usage 1000
  
  # Validate a member key
  premium-key-manager validate --key "pmk_abc123..."
  
  # List all keys for a member
  premium-key-manager list --member-id "user123"
  
  # Revoke a key
  premium-key-manager revoke --key-id "key_abc123"
  
  # Show statistics
  premium-key-manager stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a new member key')
    gen_parser.add_argument('--member-id', required=True, help='Unique member identifier')
    gen_parser.add_argument('--email', required=True, help='Member email address')
    gen_parser.add_argument('--validity-days', type=int, default=365, 
                           help='Key validity in days (default: 365)')
    gen_parser.add_argument('--max-usage', type=int, help='Maximum usage count (optional)')
    gen_parser.add_argument('--permissions', default='premium_trading,advanced_analytics',
                           help='Comma-separated permissions (default: premium_trading,advanced_analytics)')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate a member key')
    val_parser.add_argument('--key', required=True, help='Member key to validate')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List member keys')
    list_parser.add_argument('--member-id', help='Filter by member ID (optional)')
    
    # Revoke command
    rev_parser = subparsers.add_parser('revoke', help='Revoke a member key')
    rev_parser.add_argument('--key-id', required=True, help='Key ID to revoke')
    
    # Stats command
    subparsers.add_parser('stats', help='Show key statistics')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Clean up expired keys')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = KeyManagerCLI()
    
    # Route to appropriate handler
    {
        'generate': cli.generate_key,
        'validate': cli.validate_key,
        'list': cli.list_keys,
        'revoke': cli.revoke_key,
        'stats': cli.stats,
        'cleanup': cli.cleanup
    }[args.command](args)


if __name__ == '__main__':
    main()
