#!/usr/bin/env python3
"""
Fallback data provider when Redis is not available
"""

from datetime import datetime
from typing import List, Dict, Any

def get_fallback_opportunities() -> List[Dict[str, Any]]:
    """Return sample market opportunities when Redis is not available"""
    
    return [
        {
            "symbol": "BTCUSDT",
            "total_score": 35,
            "direction": "LONG",
            "confidence": "HIGH",
            "risk_level": "MEDIUM",
            "volume_24h": 1500000000,
            "timestamp": datetime.now().isoformat(),
            "score_breakdown": {
                "open_interest": 8,
                "volume_spike": 6,
                "funding_rate": 2,
                "volatility_squeeze": 4,
                "whale_activity": 5,
                "price_structure": 3,
                "sentiment": 3,
                "volume_marketcap": 2,
                "long_short_sentiment": 2
            },
            "category_scores": {
                "Bitcoin Eco": 8,
                "Layer-1": 6
            },
            "narrative_type": "Bitcoin Eco"
        },
        {
            "symbol": "ETHUSDT",
            "total_score": 32,
            "direction": "SHORT",
            "confidence": "MEDIUM",
            "risk_level": "HIGH",
            "volume_24h": 800000000,
            "timestamp": datetime.now().isoformat(),
            "score_breakdown": {
                "open_interest": 7,
                "volume_spike": 5,
                "funding_rate": 6,
                "volatility_squeeze": 2,
                "whale_activity": 4,
                "price_structure": 2,
                "sentiment": 2,
                "volume_marketcap": 2,
                "long_short_sentiment": 2
            },
            "category_scores": {
                "Layer-1": 9,
                "DeFi": 5
            },
            "narrative_type": "Layer-1"
        },
        {
            "symbol": "SOLUSDT",
            "total_score": 28,
            "direction": "LONG",
            "confidence": "MEDIUM",
            "risk_level": "LOW",
            "volume_24h": 200000000,
            "timestamp": datetime.now().isoformat(),
            "score_breakdown": {
                "open_interest": 6,
                "volume_spike": 4,
                "funding_rate": 1,
                "volatility_squeeze": 5,
                "whale_activity": 3,
                "price_structure": 3,
                "sentiment": 3,
                "volume_marketcap": 2,
                "long_short_sentiment": 1
            },
            "category_scores": {
                "Layer-1": 7,
                "DeFi": 4
            },
            "narrative_type": "Layer-1"
        },
        {
            "symbol": "ADAUSDT",
            "total_score": 26,
            "direction": "WATCH",
            "confidence": "LOW",
            "risk_level": "MEDIUM",
            "volume_24h": 150000000,
            "timestamp": datetime.now().isoformat(),
            "score_breakdown": {
                "open_interest": 5,
                "volume_spike": 3,
                "funding_rate": 4,
                "volatility_squeeze": 4,
                "whale_activity": 2,
                "price_structure": 2,
                "sentiment": 2,
                "volume_marketcap": 2,
                "long_short_sentiment": 2
            },
            "category_scores": {
                "Layer-1": 6,
                "DeFi": 3
            },
            "narrative_type": "Layer-1"
        },
        {
            "symbol": "LINKUSDT",
            "total_score": 24,
            "direction": "LONG",
            "confidence": "LOW",
            "risk_level": "LOW",
            "volume_24h": 100000000,
            "timestamp": datetime.now().isoformat(),
            "score_breakdown": {
                "open_interest": 4,
                "volume_spike": 3,
                "funding_rate": 1,
                "volatility_squeeze": 3,
                "whale_activity": 4,
                "price_structure": 3,
                "sentiment": 3,
                "volume_marketcap": 2,
                "long_short_sentiment": 1
            },
            "category_scores": {
                "Infrastructure": 8,
                "DeFi": 4
            },
            "narrative_type": "Infrastructure"
        }
    ]
