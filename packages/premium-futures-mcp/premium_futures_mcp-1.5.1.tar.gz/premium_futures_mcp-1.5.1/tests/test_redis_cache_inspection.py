#!/usr/bin/env python3
"""
Redis Cache Inspection Script
Connects to Redis and inspects cached market data to verify structure and narrative analytics.
"""

import redis
import json
import sys
from typing import Dict, Any

def connect_to_redis() -> redis.Redis:
    """Connect to Redis server"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        # Test connection
        r.ping()
        print("✅ Connected to Redis successfully")
        return r
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        print("Make sure Redis is running (docker-compose up -d redis)")
        sys.exit(1)

def inspect_cache_keys(r: redis.Redis) -> None:
    """Inspect available cache keys"""
    print("\n🔍 Inspecting Redis cache keys...")
    
    # Get all keys
    all_keys = r.keys("*")
    print(f"Total keys in cache: {len(all_keys)}")
    
    # Group keys by type
    token_keys = [k for k in all_keys if k.startswith("token:")]
    category_keys = [k for k in all_keys if k.startswith("category:")]
    market_keys = [k for k in all_keys if k.startswith("market:")]
    other_keys = [k for k in all_keys if not any(k.startswith(prefix) for prefix in ["token:", "category:", "market:"])]
    
    print(f"Token keys: {len(token_keys)}")
    print(f"Category keys: {len(category_keys)}")
    print(f"Market keys: {len(market_keys)}")
    print(f"Other keys: {len(other_keys)}")
    
    if token_keys:
        print(f"\nSample token keys: {token_keys[:5]}")
    if category_keys:
        print(f"Sample category keys: {category_keys[:5]}")
    if market_keys:
        print(f"Sample market keys: {market_keys[:5]}")
    if other_keys:
        print(f"Other keys: {other_keys}")

def inspect_token_data(r: redis.Redis, symbol: str = "CHZUSDT") -> None:
    """Inspect cached data for a specific token"""
    print(f"\n🔍 Inspecting cached data for {symbol}...")
    
    token_key = f"token:{symbol}"
    
    if not r.exists(token_key):
        print(f"❌ No cached data found for {symbol}")
        return
    
    try:
        # Get cached data
        cached_data = r.get(token_key)
        if cached_data:
            data = json.loads(cached_data)
            print(f"✅ Found cached data for {symbol}")
            print(f"Data structure:")
            print(json.dumps(data, indent=2))
            
            # Check for key fields
            required_fields = [
                'symbol', 'score', 'direction', 'volume_24h', 'price_change_24h',
                'open_interest', 'funding_rate', 'narrative_type'
            ]
            
            print(f"\n📊 Field validation:")
            for field in required_fields:
                if field in data:
                    print(f"✅ {field}: {data[field]}")
                else:
                    print(f"❌ Missing field: {field}")
                    
        else:
            print(f"❌ Empty data for {symbol}")
            
    except Exception as e:
        print(f"❌ Error parsing data for {symbol}: {e}")

def inspect_category_analytics(r: redis.Redis) -> None:
    """Inspect category analytics in cache"""
    print(f"\n🔍 Inspecting category analytics...")
    
    analytics_key = "category_analytics"
    
    if not r.exists(analytics_key):
        print(f"❌ No category analytics found in cache")
        return
    
    try:
        # Get analytics data
        analytics_data = r.get(analytics_key)
        if analytics_data:
            data = json.loads(analytics_data)
            print(f"✅ Found category analytics")
            print(f"Number of categories: {len(data)}")
            
            # Show sample categories
            categories = list(data.keys())[:5]
            for category in categories:
                cat_data = data[category]
                print(f"\n📈 Category: {category}")
                print(f"  - Avg Score: {cat_data.get('avg_score', 'N/A'):.2f}")
                print(f"  - Token Count: {cat_data.get('token_count', 'N/A')}")
                print(f"  - Total Volume: {cat_data.get('total_volume', 'N/A'):,.0f}")
                print(f"  - Avg OI: {cat_data.get('avg_open_interest', 'N/A'):,.0f}")
                
        else:
            print(f"❌ Empty category analytics data")
            
    except Exception as e:
        print(f"❌ Error parsing category analytics: {e}")

def find_tokens_with_narrative(r: redis.Redis, limit: int = 10) -> None:
    """Find tokens that have narrative_type field"""
    print(f"\n🔍 Finding tokens with narrative_type field...")
    
    # Get all token keys
    token_keys = r.keys("token:*")
    
    tokens_with_narrative = []
    tokens_without_narrative = []
    
    for key in token_keys[:limit]:  # Limit for performance
        try:
            data = json.loads(r.get(key))
            symbol = key.replace("token:", "")
            
            if 'narrative_type' in data and data['narrative_type']:
                tokens_with_narrative.append({
                    'symbol': symbol,
                    'narrative_type': data['narrative_type'],
                    'score': data.get('score', 'N/A')
                })
            else:
                tokens_without_narrative.append(symbol)
                
        except Exception as e:
            print(f"❌ Error processing {key}: {e}")
    
    print(f"✅ Tokens with narrative_type: {len(tokens_with_narrative)}")
    print(f"❌ Tokens without narrative_type: {len(tokens_without_narrative)}")
    
    if tokens_with_narrative:
        print(f"\nSample tokens with narrative:")
        for token in tokens_with_narrative[:5]:
            print(f"  - {token['symbol']}: {token['narrative_type']} (score: {token['score']})")
    
    if tokens_without_narrative:
        print(f"\nTokens without narrative: {tokens_without_narrative[:5]}")

def main():
    """Main inspection function"""
    print("🚀 Starting Redis Cache Inspection")
    print("=" * 50)
    
    # Connect to Redis
    r = connect_to_redis()
    
    # Inspect cache structure
    inspect_cache_keys(r)
    
    # Inspect specific token (CHZUSDT)
    inspect_token_data(r, "CHZUSDT")
    
    # Try other popular tokens if CHZUSDT not found
    popular_tokens = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT"]
    for token in popular_tokens:
        if r.exists(f"token:{token}"):
            inspect_token_data(r, token)
            break
    
    # Inspect category analytics
    inspect_category_analytics(r)
    
    # Find tokens with narrative data
    find_tokens_with_narrative(r, limit=20)
    
    print("\n✅ Redis cache inspection completed!")

if __name__ == "__main__":
    main()
