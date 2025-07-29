#!/usr/bin/env python3
"""
Test script to analyze volume spike and funding rate scoring
"""
import asyncio
import sys
import json
sys.path.append('src')

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

async def test_token_scoring():
    """Test scoring breakdown for specific tokens"""
    
    # Test tokens that appeared in the opportunities
    test_tokens = [
        'VICUSDT',     # Top opportunity
        'STOUSDT',     # Second opportunity 
        '1000000BOBUSDT',  # Third opportunity with funding extreme
        'BTCUSDT',     # Reference token
        'ETHUSDT'      # Another reference
    ]
    
    async with PublicBinanceClient() as client:
        intelligence = MarketIntelligenceService(client)
        
        print("🔍 SCORING BREAKDOWN ANALYSIS\n")
        print("=" * 80)
        
        for symbol in test_tokens:
            print(f"\n📊 ANALYZING {symbol}")
            print("-" * 50)
            
            try:
                # Get market data first
                ticker_data = await client.get_ticker(symbol)
                
                # Get detailed score breakdown
                score_data = await intelligence.calculate_token_score(symbol, ticker_data)
                
                if 'error' in score_data:
                    print(f"❌ Error: {score_data['error']}")
                    continue
                
                breakdown = score_data.get('score_breakdown', {})
                total_score = score_data.get('total_score', 0)
                
                print(f"📈 Total Score: {total_score}/64")
                print(f"🎯 Direction: {score_data.get('direction', 'N/A')}")
                print(f"🔥 Confidence: {score_data.get('confidence', 'N/A')}")
                print(f"💡 Recommendation: {score_data.get('recommendation', 'N/A')}")
                
                print("\n🔬 Score Breakdown:")
                print(f"  • Open Interest:     {breakdown.get('open_interest', 0)}/10")
                print(f"  • Volume Spike:      {breakdown.get('volume_spike', 0)}/8")
                print(f"  • Funding Rate:      {breakdown.get('funding_rate', 0)}/6") 
                print(f"  • Volatility:        {breakdown.get('volatility_squeeze', 0)}/5")
                print(f"  • Whale Activity:    {breakdown.get('whale_activity', 0)}/6")
                print(f"  • Price Structure:   {breakdown.get('price_structure', 0)}/4")
                print(f"  • Sentiment:         {breakdown.get('sentiment', 0)}/4")
                print(f"  • Volume/MCap:       {breakdown.get('volume_mcap_ratio', 0)}/3")
                print(f"  • Long/Short:        {breakdown.get('longshort_sentiment', 0)}/8")
                
                # Test volume spike calculation manually
                await test_volume_spike_details(client, symbol)
                
                # Test funding rate calculation manually
                await test_funding_rate_details(client, symbol)
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                continue

async def test_volume_spike_details(client: PublicBinanceClient, symbol: str):
    """Test volume spike scoring in detail"""
    try:
        print(f"\n🔊 VOLUME SPIKE ANALYSIS for {symbol}:")
        
        # Get current ticker data
        ticker = await client.get_ticker(symbol)
        current_volume = float(ticker.get('volume', 0))
        
        # Get hourly klines for volume comparison
        klines = await client.get_klines(symbol, "1h", 25)
        
        if len(klines) < 24:
            print("   ⚠️  Insufficient hourly data")
            return
        
        # Calculate volume metrics
        hourly_volumes = [float(kline[5]) for kline in klines[:-1]]  # Exclude current hour
        avg_volume = sum(hourly_volumes) / len(hourly_volumes) if hourly_volumes else 1
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        print(f"   📊 Current 24h Volume: {current_volume:,.0f}")
        print(f"   📊 Average Volume (last 24h): {avg_volume:,.0f}")
        print(f"   📊 Volume Ratio: {volume_ratio:.2f}x")
        
        # Show scoring logic
        if volume_ratio > 10:
            score = 8
        elif volume_ratio > 5:
            score = 7
        elif volume_ratio > 3:
            score = 6
        elif volume_ratio > 2:
            score = 4
        elif volume_ratio > 1.5:
            score = 2
        else:
            score = 0
            
        print(f"   🎯 Volume Spike Score: {score}/8")
        
        # Show recent volume trend
        recent_volumes = hourly_volumes[-5:]  # Last 5 hours
        print(f"   📈 Recent 5h volumes: {[f'{v:,.0f}' for v in recent_volumes]}")
        
    except Exception as e:
        print(f"   ❌ Volume analysis error: {e}")

async def test_funding_rate_details(client: PublicBinanceClient, symbol: str):
    """Test funding rate scoring in detail"""
    try:
        print(f"\n💰 FUNDING RATE ANALYSIS for {symbol}:")
        
        # Get mark price data (includes funding rate)
        mark_price_data = await client.get_mark_price(symbol)
        funding_rate = float(mark_price_data['lastFundingRate'])
        
        print(f"   💸 Current Funding Rate: {funding_rate:.6f} ({funding_rate*100:.4f}%)")
        
        # Show scoring logic
        direction = "NEUTRAL"
        score = 0
        
        if funding_rate > 0.002:  # > 0.2%
            score = 6
            direction = "SHORT"
            print(f"   ⚡ EXTREME positive funding! Over-leveraged longs")
        elif funding_rate > 0.001:  # > 0.1%
            score = 5
            direction = "SHORT"
            print(f"   🔥 High positive funding - potential short squeeze")
        elif funding_rate > 0.0005:  # > 0.05%
            score = 3
            direction = "SHORT"
            print(f"   ⚠️  Moderate positive funding")
        elif funding_rate < -0.002:  # < -0.2%
            score = 6
            direction = "LONG"
            print(f"   ⚡ EXTREME negative funding! Over-leveraged shorts")
        elif funding_rate < -0.001:  # < -0.1%
            score = 5
            direction = "LONG"
            print(f"   🔥 High negative funding - potential long squeeze")
        elif funding_rate < -0.0005:  # < -0.05%
            score = 3
            direction = "LONG"
            print(f"   ⚠️  Moderate negative funding")
        else:
            print(f"   ✅ Normal funding rate")
        
        print(f"   🎯 Funding Rate Score: {score}/6")
        print(f"   🧭 Suggested Direction: {direction}")
        
        # Get funding rate history if available
        try:
            funding_history = await client.get_funding_rate_history(symbol, limit=8)
            if funding_history:
                print(f"   📊 Recent funding history:")
                for i, entry in enumerate(funding_history[-5:]):  # Last 5 entries
                    rate = float(entry['fundingRate'])
                    time = entry['fundingTime']
                    print(f"      {i+1}. {rate:.6f} ({rate*100:.4f}%) - {time}")
        except:
            print(f"   ⚠️  Funding history not available")
        
    except Exception as e:
        print(f"   ❌ Funding analysis error: {e}")

if __name__ == "__main__":
    asyncio.run(test_token_scoring())
