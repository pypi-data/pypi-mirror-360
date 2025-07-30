#!/usr/bin/env python3
"""
Test script to verify dynamic sentiment scoring
"""
import asyncio
import sys
sys.path.append('src')

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

async def test_dynamic_sentiment():
    """Test dynamic sentiment scoring for different categories"""
    
    # Test tokens from different categories
    test_tokens = [
        ('APEUSDT', 'NFT'),         # Should get high score (NFT performing well)
        ('UNIUSDT', 'DeFi'),        # Should get good score (DeFi performing well)  
        ('AIUSDT', 'AI'),           # Should get lower score (AI underperforming)
        ('DOGEUSDT', 'Meme'),       # Should get moderate score
        ('ETHUSDT', 'Layer-1'),     # Should get moderate score
    ]
    
    async with PublicBinanceClient() as client:
        intelligence = MarketIntelligenceService(client)
        
        # Get ticker data for dynamic calculation
        all_tickers = await client.get_all_tickers()
        
        # Calculate dynamic scores
        print("🧠 DYNAMIC SENTIMENT SCORING TEST")
        print("=" * 60)
        
        print("\n📊 Calculating dynamic category scores...")
        dynamic_scores = await intelligence._calculate_dynamic_category_scores(all_tickers)
        
        print(f"\n🎯 Category Performance Rankings:")
        sorted_categories = sorted(dynamic_scores.items(), key=lambda x: x[1], reverse=True)
        for i, (category, score) in enumerate(sorted_categories[:15], 1):
            metrics = intelligence.category_metrics_cache.get(category, {})
            active_tokens = metrics.get('active_tokens', 0)
            avg_change = metrics.get('avg_price_change', 0)
            total_volume = metrics.get('total_volume', 0)
            print(f"   {i:2d}. {category:12s}: {score:.2f}/4 ({active_tokens:2d} tokens, {avg_change:+6.2f}%, {total_volume:,.0f} vol)")
        
        print(f"\n🔍 Individual Token Sentiment Analysis:")
        print("-" * 60)
        
        for symbol, expected_category in test_tokens:
            try:
                # Test the sentiment scoring
                sentiment_score, actual_category = await intelligence._calculate_sentiment_score(symbol)
                category_dynamic_score = dynamic_scores.get(actual_category, 1.0)
                
                print(f"\n📈 {symbol}")
                print(f"   Expected Category: {expected_category}")
                print(f"   Actual Category:   {actual_category}")
                print(f"   Category Score:    {category_dynamic_score:.2f}/4 (dynamic)")
                print(f"   Token Score:       {sentiment_score}/4")
                
                # Compare with old hardcoded score
                old_hardcoded = intelligence.narrative_scores.get(actual_category, 1)
                print(f"   Old Hardcoded:     {old_hardcoded}/4")
                
                if category_dynamic_score != old_hardcoded:
                    difference = category_dynamic_score - old_hardcoded
                    direction = "📈 UPGRADE" if difference > 0 else "📉 DOWNGRADE"
                    print(f"   📊 Change:         {direction} ({difference:+.2f} points)")
                else:
                    print(f"   📊 Change:         No change")
                    
            except Exception as e:
                print(f"❌ Error testing {symbol}: {e}")
        
        print(f"\n💡 INSIGHTS:")
        print("   • Dynamic scoring reflects real market performance")
        print("   • Categories with strong performance get higher sentiment scores")
        print("   • This removes bias from hardcoded category rankings")
        print("   • Sentiment scores now update based on actual market data")

if __name__ == "__main__":
    asyncio.run(test_dynamic_sentiment())
