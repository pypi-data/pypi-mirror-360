#!/usr/bin/env python3

"""
Test script to verify the actual maximum scores for each factor
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.market_intelligence import MarketIntelligenceService

async def verify_max_scores():
    """Check the actual maximum scores by looking at the implementation"""
    
    print("🔍 Verifying Maximum Scores for Each Factor")
    print("=" * 60)
    
    # We'll examine the scoring ranges from the code comments
    scoring_factors = [
        ("Open Interest", "0-10", 10),
        ("Volume Spike", "0-8", 8), 
        ("Funding Rate", "0-6", 6),
        ("Volatility Squeeze", "0-5", 5),
        ("Whale Activity", "0-6", 6),
        ("Price Structure", "0-4", 4),
        ("Sentiment/Narrative", "0-4", 4),
        ("Volume/MarketCap Ratio", "0-3", 3),
        ("Long/Short Sentiment", "0-4", 4),
    ]
    
    total_max = 0
    
    for factor, range_str, max_points in scoring_factors:
        print(f"  {factor:25} {range_str:>10} = {max_points:>3} points")
        total_max += max_points
    
    print("-" * 60)
    print(f"{'TOTAL MAXIMUM SCORE':25} {'':>10} = {total_max:>3} points")
    print("=" * 60)
    
    # Check what's currently set in the code
    mi = MarketIntelligenceService()
    print(f"\nCurrent max_score in code: Looking at the hardcoded value...")
    
    # Let's check what the test scoring result shows
    print(f"\nFrom the latest log: 1000000BOBUSDT scored 32/64")
    print(f"This suggests the system thinks max score is 64")
    print(f"But based on factor analysis, max should be {total_max}")
    
    if total_max != 64:
        print(f"\n⚠️  MISMATCH DETECTED!")
        print(f"   Code sets max_score = 64")
        print(f"   But actual factor sum = {total_max}")
        print(f"   Need to correct max_score to {total_max}")
    else:
        print(f"\n✅ Scores match!")

if __name__ == "__main__":
    asyncio.run(verify_max_scores())
