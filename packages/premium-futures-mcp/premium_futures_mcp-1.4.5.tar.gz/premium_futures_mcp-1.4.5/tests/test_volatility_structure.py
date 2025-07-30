#!/usr/bin/env python3
"""
Detailed analysis of Volatility Squeeze and Price Structure scoring
"""
import asyncio
import sys
sys.path.append('src')

from premium_futures_mcp.public_client import PublicBinanceClient
from premium_futures_mcp.market_intelligence import MarketIntelligenceService

async def test_volatility_and_structure():
    """Test volatility squeeze and price structure scoring in detail"""
    
    test_tokens = [
        'BTCUSDT',
        'ETHUSDT', 
        'VICUSDT',    # Currently high scoring
        'STOUSDT',    # Currently high scoring
        '1000000BOBUSDT'  # Currently high scoring
    ]
    
    async with PublicBinanceClient() as client:
        intelligence = MarketIntelligenceService(client)
        
        print("🔍 VOLATILITY SQUEEZE & PRICE STRUCTURE ANALYSIS")
        print("=" * 80)
        
        for symbol in test_tokens:
            print(f"\n📊 ANALYZING {symbol}")
            print("-" * 60)
            
            try:
                # Test Volatility Squeeze Analysis
                print("🌪️  VOLATILITY SQUEEZE ANALYSIS:")
                await analyze_volatility_squeeze(client, symbol)
                
                print("\n📈 PRICE STRUCTURE ANALYSIS:")
                await analyze_price_structure(client, symbol)
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")

async def analyze_volatility_squeeze(client: PublicBinanceClient, symbol: str):
    """Detailed volatility squeeze analysis"""
    try:
        print(f"   📡 Endpoint: GET /fapi/v1/klines")
        print(f"   🔧 Parameters: symbol={symbol}, interval=1h, limit=20")
        
        # Get recent klines for ATR calculation (same as in the code)
        klines = await client.get_klines(symbol, "1h", 20)
        
        if len(klines) < 14:
            print("   ⚠️  Insufficient data (need 14+ klines)")
            return
        
        print(f"   📊 Data Points: {len(klines)} hourly candles")
        
        # Calculate True Range for each period (same logic as code)
        true_ranges = []
        for i in range(1, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            prev_close = float(klines[i-1][4])
            
            tr = max(
                high - low,                    # Current high-low
                abs(high - prev_close),        # Current high vs previous close
                abs(low - prev_close)          # Current low vs previous close
            )
            true_ranges.append(tr)
        
        print(f"   📐 True Range Calculation:")
        print(f"      • Method: max(high-low, |high-prev_close|, |low-prev_close|)")
        print(f"      • Periods calculated: {len(true_ranges)}")
        
        # Calculate ATR ratios (same as code)
        current_atr = sum(true_ranges[-5:]) / 5    # Last 5 hours ATR
        avg_atr = sum(true_ranges[-14:]) / 14      # 14 hours ATR average
        atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1
        
        print(f"   📊 ATR Analysis:")
        print(f"      • Current ATR (5h avg): {current_atr:.6f}")
        print(f"      • Average ATR (14h avg): {avg_atr:.6f}")
        print(f"      • ATR Ratio: {atr_ratio:.3f}")
        
        # Show scoring logic (same thresholds as code)
        print(f"   🎯 Volatility Squeeze Scoring Logic:")
        print(f"      • < 0.5:  5 points (Extreme compression)")
        print(f"      • < 0.7:  4 points (High compression)")
        print(f"      • < 0.85: 3 points (Moderate compression)")
        print(f"      • < 1.0:  2 points (Low compression)")
        print(f"      • < 1.2:  1 point  (Minimal compression)")
        print(f"      • ≥ 1.2:  0 points (No compression)")
        
        # Calculate actual score
        if atr_ratio < 0.5:
            score = 5
            level = "EXTREME compression"
        elif atr_ratio < 0.7:
            score = 4
            level = "HIGH compression"
        elif atr_ratio < 0.85:
            score = 3
            level = "MODERATE compression"
        elif atr_ratio < 1.0:
            score = 2
            level = "LOW compression"
        elif atr_ratio < 1.2:
            score = 1
            level = "MINIMAL compression"
        else:
            score = 0
            level = "NO compression"
        
        print(f"   🏆 RESULT: {score}/5 points - {level}")
        print(f"   💡 Interpretation: Lower ATR ratio = tighter price ranges = higher squeeze potential")
        
        # Show recent price action
        recent_ranges = true_ranges[-5:]
        print(f"   📈 Recent True Ranges: {[f'{tr:.6f}' for tr in recent_ranges]}")
        
    except Exception as e:
        print(f"   ❌ Error in volatility analysis: {e}")

async def analyze_price_structure(client: PublicBinanceClient, symbol: str):
    """Detailed price structure analysis"""
    try:
        print(f"   📡 Endpoint: GET /fapi/v1/klines")
        print(f"   🔧 Parameters: symbol={symbol}, interval=15m, limit=40")
        
        # Get recent price action for structure analysis (same as code)
        klines = await client.get_klines(symbol, "15m", 40)  # 10 hours of 15m data
        
        if len(klines) < 20:
            print("   ⚠️  Insufficient data (need 20+ klines)")
            return
        
        print(f"   📊 Data Points: {len(klines)} 15-minute candles (10 hours)")
        
        # Extract price data (same as code)
        highs = [float(kline[2]) for kline in klines]
        lows = [float(kline[3]) for kline in klines]
        closes = [float(kline[4]) for kline in klines]
        
        current_price = closes[-1]
        
        # Find key levels (same logic as code)
        recent_high = max(highs[-20:])    # 5 hour high (20 * 15min = 5h)
        recent_low = min(lows[-20:])      # 5 hour low
        daily_high = max(highs)           # 10 hour high
        daily_low = min(lows)             # 10 hour low
        
        print(f"   🏔️  Key Price Levels:")
        print(f"      • Current Price:    {current_price:.6f}")
        print(f"      • Recent High (5h): {recent_high:.6f}")
        print(f"      • Recent Low (5h):  {recent_low:.6f}")
        print(f"      • Daily High (10h): {daily_high:.6f}")
        print(f"      • Daily Low (10h):  {daily_low:.6f}")
        
        # Calculate position in range (same as code)
        if recent_high != recent_low:
            range_position = (current_price - recent_low) / (recent_high - recent_low)
        else:
            range_position = 0.5
        
        print(f"   📍 Range Position: {range_position:.3f} (0=bottom, 1=top)")
        
        # Show scoring logic (same thresholds as code)
        print(f"   🎯 Price Structure Scoring Logic:")
        print(f"      • ≥ 99.9% of recent high: 4 points (Resistance breakout)")
        print(f"      • ≤ 100.1% of recent low: 4 points (Support breakdown)")
        print(f"      • > 90% range position:   3 points (Approaching resistance)")
        print(f"      • < 10% range position:   3 points (Approaching support)")
        print(f"      • 40-60% range position:  1 point  (Range middle)")
        print(f"      • Other positions:        0 points (No clear structure)")
        
        # Calculate actual score (same logic as code)
        score = 0
        signal = ""
        
        resistance_threshold = recent_high * 0.999
        support_threshold = recent_low * 1.001
        
        if current_price >= resistance_threshold:
            score = 4
            signal = "resistance_breakout"
            level = "RESISTANCE BREAKOUT"
        elif current_price <= support_threshold:
            score = 4
            signal = "support_breakdown"  
            level = "SUPPORT BREAKDOWN"
        elif range_position > 0.9:
            score = 3
            signal = "approaching_resistance"
            level = "APPROACHING RESISTANCE"
        elif range_position < 0.1:
            score = 3
            signal = "approaching_support"
            level = "APPROACHING SUPPORT"
        elif 0.4 <= range_position <= 0.6:
            score = 1
            signal = "range_middle"
            level = "RANGE MIDDLE"
        else:
            score = 0
            signal = "no_clear_structure"
            level = "NO CLEAR STRUCTURE"
        
        print(f"   🏆 RESULT: {score}/4 points - {level}")
        print(f"   📊 Signal: {signal}")
        
        # Show distance to key levels
        resistance_distance = ((recent_high - current_price) / current_price) * 100
        support_distance = ((current_price - recent_low) / current_price) * 100
        
        print(f"   📏 Distance Analysis:")
        print(f"      • To Resistance: {resistance_distance:+.2f}%")
        print(f"      • To Support:    {support_distance:+.2f}%")
        
        print(f"   💡 Interpretation: Higher scores indicate proximity to key breakout/breakdown levels")
        
    except Exception as e:
        print(f"   ❌ Error in structure analysis: {e}")

if __name__ == "__main__":
    asyncio.run(test_volatility_and_structure())
