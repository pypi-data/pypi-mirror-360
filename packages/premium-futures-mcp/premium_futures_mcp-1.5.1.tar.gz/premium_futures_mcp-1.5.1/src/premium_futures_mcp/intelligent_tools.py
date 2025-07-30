"""
Intelligent Market Analysis Tools for Premium Binance Futures MCP Server

These tools provide pre-analyzed market data and intelligent filtering
to avoid the bottleneck of calling individual APIs for each token.
"""

from mcp.types import Tool


def get_intelligent_market_tools():
    """Market intelligence tools with pre-filtered and analyzed data"""
    return [
        Tool(
            name="get_market_opportunities",
            description="""Get top trading opportunities based on comprehensive 9-factor scoring system:
            1. Open Interest changes (0-10 points)
            2. Volume spikes (0-8 points)  
            3. Funding rate extremes (0-6 points)
            4. Volatility squeeze (0-5 points)
            5. Whale activity (0-6 points)
            6. Price structure (0-4 points)
            7. Sentiment/narrative (0-4 points)
            8. Volume/MarketCap ratio (0-3 points)
            9. Long/Short sentiment (0-8 points)
            
            Total: 0-50 points with direction recommendations (LONG/SHORT/WATCH)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer", 
                        "description": "Number of opportunities to return (default: 10, max: 50)",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum opportunity score (0-50, default: 25)",
                        "minimum": 0,
                        "maximum": 50,
                        "default": 25
                    },
                    "direction": {
                        "type": "string",
                        "description": "Filter by trading direction",
                        "enum": ["LONG", "SHORT", "WATCH", "ALL"],
                        "default": "ALL"
                    },
                    "confidence": {
                        "type": "string", 
                        "description": "Filter by confidence level",
                        "enum": ["HIGH", "MEDIUM", "LOW", "VERY_LOW", "ALL"],
                        "default": "ALL"
                    },
                    "risk_level": {
                        "type": "string",
                        "description": "Filter by risk level",
                        "enum": ["LOW", "MEDIUM", "HIGH", "ALL"],
                        "default": "ALL"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_token_analysis",
            description="""Get detailed analysis for a specific token with complete scoring breakdown.
            Provides real-time analysis including:
            - 9-factor scoring breakdown
            - Risk assessment
            - Entry timeframe suggestions
            - Confidence factors
            - Market context""",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., BTCUSDT, ETHUSDT)"
                    },
                    "include_context": {
                        "type": "boolean",
                        "description": "Include additional market context and comparisons",
                        "default": True
                    }
                },
                "required": ["symbol"]
            }
        ),
        
        Tool(
            name="get_market_dashboard", 
            description="""Get comprehensive market overview dashboard with:
            - Market statistics and sentiment
            - Top opportunities by category
            - Funding rate extremes
            - Volume leaders
            - Volatility squeeze candidates
            - Risk distribution""",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_breakdown": {
                        "type": "boolean",
                        "description": "Include detailed scoring breakdown for top opportunities",
                        "default": False
                    },
                    "category_limit": {
                        "type": "integer",
                        "description": "Number of tokens per category (default: 5)",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 5
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_funding_extremes",
            description="""Get tokens with extreme funding rates indicating potential squeezes.
            Trading Logic: LONG_SQUEEZE → SHORT trade | SHORT_SQUEEZE → LONG trade
            
            Extreme funding rates indicate squeeze opportunities:
            - LONG_SQUEEZE: Over-leveraged longs + high funding → Trade SHORT
            - SHORT_SQUEEZE: Over-leveraged shorts + negative funding → Trade LONG
            - Strategy: Always trade OPPOSITE to the squeeze direction for profit""",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "number",
                        "description": "Funding rate threshold in percentage (default: 0.05%)",
                        "minimum": 0.01,
                        "maximum": 1.0,
                        "default": 0.05
                    },
                    "include_direction": {
                        "type": "string",
                        "description": "Include specific squeeze direction",
                        "enum": ["LONG_SQUEEZE", "SHORT_SQUEEZE", "BOTH"],
                        "default": "BOTH"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_volume_leaders",
            description="""Get tokens with unusual volume activity indicating potential breakouts.
            Volume often precedes price movement, making this a leading indicator.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "multiplier": {
                        "type": "number",
                        "description": "Volume multiplier threshold vs average (default: 2.0)",
                        "minimum": 1.5,
                        "maximum": 10.0,
                        "default": 2.0
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Volume comparison timeframe",
                        "enum": ["1h", "4h", "24h"],
                        "default": "24h"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_volatility_squeeze",
            description="""Get tokens showing volatility squeeze patterns.
            Low volatility often precedes explosive moves - compression before expansion.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "compression_level": {
                        "type": "string",
                        "description": "Level of volatility compression",
                        "enum": ["EXTREME", "HIGH", "MODERATE", "ALL"],
                        "default": "HIGH"
                    },
                    "min_volume": {
                        "type": "number",
                        "description": "Minimum 24h volume filter (default: 500000)",
                        "minimum": 100000,
                        "default": 500000
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_whale_activity",
            description="""Get tokens with significant whale activity based on order book analysis.
            Large orders and imbalances often indicate institutional interest.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_whale_score": {
                        "type": "integer",
                        "description": "Minimum whale activity score (0-6, default: 3)",
                        "minimum": 1,
                        "maximum": 6,
                        "default": 3
                    },
                    "whale_direction": {
                        "type": "string",
                        "description": "Filter by whale bias direction",
                        "enum": ["LONG", "SHORT", "ALL"],
                        "default": "ALL"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_narrative_plays",
            description="""Get tokens benefiting from current market narratives.
            Narrative-driven tokens often see sustained momentum.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "narrative": {
                        "type": "string",
                        "description": "Filter by specific narrative category",
                        "enum": ["AI", "RWA", "Layer-1", "Layer-2", "DeFi", "Gaming", "Infrastructure", "Metaverse", "NFT", "Payment", "PoW", "Storage", "Meme", "Index", "Privacy", "Bitcoin Eco", "CEX", "ALL"],
                        "default": "ALL"
                    },
                    "min_sentiment_score": {
                        "type": "integer",
                        "description": "Minimum sentiment score (0-4, default: 1)",
                        "minimum": 0,
                        "maximum": 4,
                        "default": 1
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="get_quick_scan",
            description="""Get a quick market scan with only the highest conviction opportunities.
            Perfect for rapid market assessment when time is limited.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "urgency": {
                        "type": "string",
                        "description": "Scan urgency level",
                        "enum": ["IMMEDIATE", "URGENT", "NORMAL"],
                        "default": "NORMAL"
                    }
                },
                "required": []
            }
        )
    ]


def get_all_tools():
    """Get all intelligent market tools only - use server.py to combine with other tools"""
    return get_intelligent_market_tools()
