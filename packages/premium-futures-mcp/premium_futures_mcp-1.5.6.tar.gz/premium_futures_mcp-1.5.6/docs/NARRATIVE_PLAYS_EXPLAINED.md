# 🎭 Narrative Plays System - Complete Guide

## 📊 How `get_narrative_plays` Tool Works

The `get_narrative_plays` tool identifies tokens that benefit from current market narratives by analyzing **sentiment scores** and **narrative categories**.

## 🎯 Sentiment Scoring System (0-4 Points)

### 🔥 **TIER 1: AI Narrative (4/4 points)**
- **Tokens**: FET, AGIX, OCEAN, TAO, RNDR, WLD, ARKM
- **Why**: AI is the hottest narrative in crypto with massive institutional and retail interest
- **Example**: `FETUSDT` gets 4/4 sentiment points automatically

### ⚡ **TIER 2: Layer2 & DeFi (3/4 points)**
- **Layer2**: ARB, OP, MATIC, LRC, IMX, STRK
- **DeFi**: UNI, AAVE, COMP, MKR, CRV, BAL
- **Why**: Strong fundamental narratives with proven utility
- **Example**: `ARBUSDT` and `UNIUSDT` get 3/4 sentiment points

### 🎪 **TIER 3: Meme & Bluechip (2/4 points)**
- **Meme**: DOGE, SHIB, PEPE, FLOKI, BONK, WIF
- **Bluechip**: BTC, ETH
- **Why**: Reliable narratives but not currently trending
- **Example**: `DOGEUSDT` and `BTCUSDT` get 2/4 sentiment points

### ⚪ **TIER 4: General Tokens (1/4 points)**
- **All other tokens** not in above categories
- **Why**: No specific narrative strength
- **Example**: `LINKUSDT` gets 1/4 sentiment points

## 🔍 What Makes a Token Good for Narrative Plays?

### 1. **High Sentiment Score (≥2)**
The tool filters for tokens with sentiment scores of 2 or higher by default.

### 2. **Supporting Technical Indicators**
Narrative plays work best when combined with:
- **Volume Spikes** (6+ points): Confirms breakout momentum
- **Whale Activity** (4+ points): Institutional interest aligning with narrative
- **Funding Extremes** (4+ points): Squeeze potential during narrative pumps
- **Technical Breakouts** (3+ points): Price breaking key resistance levels

### 3. **Market Timing Factors**
- **Cycle Alignment**: Is this narrative currently hot?
- **Recent Catalysts**: News, partnerships, or developments
- **Social Sentiment**: Twitter buzz, Reddit discussions
- **Institutional Activity**: Adoption, partnerships, investments

## 🚀 Tool Usage Examples

### Basic Usage:
```json
{
  "name": "get_narrative_plays",
  "arguments": {
    "narrative": "ALL",
    "min_sentiment_score": 2
  }
}
```

### Filter for AI Tokens Only:
```json
{
  "name": "get_narrative_plays", 
  "arguments": {
    "narrative": "AI",
    "min_sentiment_score": 3
  }
}
```

### High Conviction Plays:
```json
{
  "name": "get_narrative_plays",
  "arguments": {
    "narrative": "ALL", 
    "min_sentiment_score": 3
  }
}
```

## 📈 Typical Narrative Play Profile

A strong narrative play might look like:
- **Total Score**: 35-50/60 points
- **Sentiment Score**: 3-4/4 points 
- **Volume Score**: 4-6/8 points (unusual activity)
- **Direction**: LONG (riding narrative momentum)
- **Confidence**: MEDIUM-HIGH
- **Narrative Type**: AI, Layer2, or DeFi

## 💡 Key Success Factors

### ✅ **DO:**
- Look for narratives with recent catalysts
- Combine with technical breakouts
- Watch for institutional accumulation
- Time entries during narrative peaks
- Set realistic profit targets

### ❌ **DON'T:**
- Chase narratives at extreme highs
- Ignore underlying fundamentals
- Trade against major trends
- Use excessive leverage
- FOMO into late-cycle narratives

## 🎯 Strategy Tips

1. **Early Identification**: Use the tool to spot narrative momentum before it peaks
2. **Multi-Factor Confirmation**: Look for 3+ supporting indicators beyond sentiment
3. **Risk Management**: Narrative plays can be volatile - size positions accordingly
4. **Cycle Awareness**: Different narratives dominate different market cycles
5. **News Monitoring**: Stay updated on narrative-driving developments

## 📊 Real-World Example

**FETUSDT during AI narrative pump:**
- Sentiment Score: 4/4 (AI narrative)
- Volume Score: 7/8 (unusual buying activity)
- Whale Score: 5/6 (institutional accumulation)
- Total Score: 42/60
- Direction: LONG
- Confidence: HIGH
- **Result**: Strong narrative play candidate

The `get_narrative_plays` tool would identify this as a top opportunity, combining the hot AI narrative with supporting technical indicators.
