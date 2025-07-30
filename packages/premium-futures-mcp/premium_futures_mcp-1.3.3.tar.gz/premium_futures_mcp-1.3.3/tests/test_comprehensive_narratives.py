#!/usr/bin/env python3
"""
Test script for the comprehensive Binance-based narrative categorization system
"""
import asyncio
import sys
sys.path.append('src')

from premium_futures_mcp.market_intelligence import MarketIntelligenceService
from premium_futures_mcp.public_client import PublicBinanceClient


async def test_comprehensive_narratives():
    print("🎭 TESTING COMPREHENSIVE BINANCE NARRATIVE SYSTEM")
    print("=" * 60)
    
    # Test without client first (just categories)
    intelligence = MarketIntelligenceService(None)
    
    # Test samples from each category
    test_symbols = [
        # AI narrative (should get 4 points)
        ('FETUSDT', 'AI', 4),
        ('TAOUESDT', 'AI', 4), 
        ('AGIXUSDT', 'AI', 4),
        
        # RWA narrative (should get 4 points)
        ('ONDOUSDT', 'RWA', 4),
        ('INJUSDT', 'RWA', 4),
        
        # Layer-1 (should get 3 points)
        ('SOLUSDT', 'Layer-1', 3),
        ('ADAUSDT', 'Layer-1', 3),
        ('DOTSDT', 'Layer-1', 3),
        
        # Layer-2 (should get 3 points)
        ('ARBUSDT', 'Layer-2', 3),
        ('OPUSDT', 'Layer-2', 3),
        
        # DeFi (should get 3 points)
        ('UNIUSDT', 'DeFi', 3),
        ('AAVEUSDT', 'DeFi', 3),
        
        # Gaming (should get 3 points)
        ('GALAUSDT', 'Gaming', 3),
        ('AXSUSDT', 'Gaming', 3),
        
        # Infrastructure (should get 2 points)
        ('LINKUSDT', 'Infrastructure', 2),
        ('RENDERUSDT', 'Infrastructure', 2),
        
        # Meme (should get 1 point)
        ('DOGEUSDT', 'Meme', 1),
        ('1000PEPEUSDT', 'Meme', 1),
        
        # PoW (should get 2 points)
        ('BTCUSDT', 'PoW', 2),
        
        # Unknown token (should get 1 point)
        ('UNKNOWNUSDT', 'General', 1),
    ]
    
    print("📊 TESTING NARRATIVE CATEGORIZATION:")
    print("-" * 60)
    print(f"{'Symbol':<15} {'Expected':<12} {'Actual':<12} {'Score':<5} {'Status'}")
    print("-" * 60)
    
    correct = 0
    total = 0
    
    for symbol, expected_category, expected_score in test_symbols:
        try:
            score, category = await intelligence._calculate_sentiment_score(symbol)
            status = "✅" if category == expected_category and score == expected_score else "❌"
            if status == "✅":
                correct += 1
            
            print(f"{symbol:<15} {expected_category:<12} {category:<12} {score:<5} {status}")
            total += 1
            
        except Exception as e:
            print(f"{symbol:<15} {expected_category:<12} ERROR        0     ❌ ({e})")
            total += 1
    
    print("-" * 60)
    print(f"Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
    
    print("\n📈 CATEGORY BREAKDOWN:")
    print("-" * 40)
    
    # Show category counts
    for category, tokens in intelligence.token_categories.items():
        score = intelligence.narrative_scores.get(category, 1)
        print(f"{category:<15} | {len(tokens):>3} tokens | {score}/4 points")
    
    print(f"\nTotal categories: {len(intelligence.token_categories)}")
    total_tokens = sum(len(tokens) for tokens in intelligence.token_categories.values())
    print(f"Total tokens categorized: {total_tokens}")
    
    print("\n🎯 HIGH-VALUE NARRATIVES (3-4 points):")
    high_value_categories = {k: v for k, v in intelligence.narrative_scores.items() if v >= 3}
    for category, score in sorted(high_value_categories.items(), key=lambda x: x[1], reverse=True):
        token_count = len(intelligence.token_categories.get(category, []))
        print(f"  {category:<15} ({score}/4) - {token_count} tokens")
    
    print(f"\n🎉 Comprehensive narrative system ready!")
    print(f"✅ {len(intelligence.token_categories)} categories")
    print(f"✅ {total_tokens} tokens categorized")
    print(f"✅ Scoring system: 1-4 points based on narrative strength")


if __name__ == "__main__":
    asyncio.run(test_comprehensive_narratives())
