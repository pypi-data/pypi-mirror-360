"""
Market Intelligence Service for Premium Binance Futures MCP Server

This module provides intelligent market analysis and token scoring based on:
1. Open Interest Changes
2. Volume Spikes  
3. Funding Rate Extremes
4. Volatility Squeeze
5. Whale Activity
6. Price Structure
7. Sentiment/Narrative
8. Volume/MarketCap Ratio
9. Long/Short Sentiment

Scoring system: 0-50 points total, with direction recommendations (LONG/SHORT/WATCH)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from .public_client import PublicBinanceClient


class MarketIntelligenceService:
    """24/7 market monitoring with intelligent scoring system"""
    
    def __init__(self, public_client: PublicBinanceClient = None, redis_client=None):
        self.client = public_client
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Active symbols cache (like TickerCache)
        self.active_symbols: set = set()
        self.exchange_info_updated: Optional[datetime] = None
        
        # Comprehensive token categories based on Binance underlyingSubType
        # Official Binance categories with narrative scoring weights
        self.token_categories = {
            'AI': ['1000X', 'ACT', 'AGIX', 'AGT', 'AI', 'AI16Z', 'AIOT', 'AIXBT', 'AKT', 'ALCH', 'ARC', 'ATH', 'AVAAI', 'AWE', 'BDXN', 'BID', 'CGPT', 'COOKIE', 'FET', 'FHE', 'FLUX', 'GOAT', 'GRASS', 'GRIFFAIN', 'GRT', 'IO', 'IP', 'LA', 'LPT', 'NFP', 'NIL', 'NMR', 'OCEAN', 'PHA', 'PHB', 'PORT3', 'PROMPT', 'RLC', 'SHELL', 'SKYAI', 'SWARMS', 'SXT', 'TAO', 'THETA', 'TURBO', 'VANA', 'VIDT', 'VIRTUAL', 'VVV', 'WLD', 'ZEREBRO'],
            'Layer-1': ['ADA', 'ALGO', 'AMB', 'APT', 'ARK', 'ASTR', 'ATOM', 'BB', 'BERA', 'BNB', 'CELO', 'DOT', 'DYDX', 'EGLD', 'ETH', 'FLOW', 'FTM', 'HBAR', 'HIVE', 'ICX', 'INIT', 'IOST', 'KAS', 'KLAY', 'KSM', 'LUNA2', 'MINA', 'MOVE', 'MOVR', 'NEAR', 'NEO', 'NTRN', 'OMNI', 'ONG', 'PARTI', 'QTUM', 'REI', 'ROSE', 'S', 'SAGA', 'SCR', 'SCRT', 'SEI', 'SKATE', 'SOL', 'STRK', 'SUI', 'SXP', 'TON', 'TRX', 'VET', 'VIC', 'VTHO', 'WAVES', 'XEM', 'XTZ', 'ZETA'],
            'Layer-2': ['A', 'ARB', 'CELR', 'CTSI', 'GLMR', 'LSK', 'MANTA', 'MERL', 'METIS', 'OMG', 'ONE', 'OP', 'POL', 'POWR', 'PUFFER', 'SKL', 'SOPH', 'STRAX', 'TAIKO', 'XLM', 'ZK', 'ZKJ'],
            'DeFi': ['1000LUNC', '1INCH', 'AAVE', 'ACX', 'AERO', 'AEVO', 'ALPACA', 'ALPHA', 'ANKR', 'AUCTION', 'B2', 'BABY', 'BAL', 'BAKE', 'BANANA', 'BAND', 'BEL', 'BNT', 'BOND', 'BR', 'BSW', 'BTCST', 'C98', 'CAKE', 'CETUS', 'CHESS', 'COMP', 'COW', 'CRV', 'CVX', 'DEEP', 'DEXE', 'DF', 'DODOX', 'DOLO', 'DRIFT', 'ENA', 'ETHFI', 'F', 'FIS', 'FLM', 'FORTH', 'FUN', 'FXS', 'GMX', 'HAEDAL', 'HFT', 'HOME', 'HYPE', 'HYPER', 'IDEX', 'JOE', 'JST', 'JTO', 'JUP', 'KAIA', 'KAVA', 'KERNEL', 'KMNO', 'KNC', 'LDO', 'LEVER', 'LINA', 'LISTA', 'LQTY', 'LRC', 'MILK', 'MKR', 'MLN', 'MORPHO', 'MYX', 'OBOL', 'OGN', 'ORCA', 'PENDLE', 'PERP', 'PUMPBTC', 'PUNDIX', 'QUICK', 'RAD', 'RAY', 'RDNT', 'REEF', 'REN', 'RESOLV', 'REZ', 'RPL', 'RUNE', 'SNT', 'SOLV', 'SPELL', 'SPK', 'SQD', 'STEEM', 'STG', 'STO', 'STPT', 'SUN', 'SUSHI', 'SWELL', 'SYN', 'SYRUP', 'THE', 'TOKEN', 'UMA', 'UNFI', 'UNI', 'USTC', 'VELODROME', 'WOO', 'XVS', 'YFI', 'ZRX'],
            'Meme': ['1000000BOB', '1000000MOG', '1000BONK', '1000CAT', '1000CHEEMS', '1000FLOKI', '1000PEPE', '1000RATS', '1000SATS', '1000SHIB', '1000WHY', '1MBABYDOGE', 'B', 'BAN', 'BANANAS31', 'BANK', 'BOME', 'BRETT', 'BROCCOLI714', 'BROCCOLIF3B', 'CHILLGUY', 'DEGEN', 'DOGE', 'DOGS', 'FARTCOIN', 'HIPPO', 'JELLYJELLY', 'KOMA', 'MELANIA', 'MEME', 'MEW', 'MOODENG', 'MUBARAK', 'MYRO', 'NEIRO', 'NEIROETH', 'NEWT', 'ORDI', 'PENGU', 'PEOPLE', 'PIPPIN', 'PNUT', 'PONKE', 'POPCAT', 'PUMP', 'SIREN', 'SLERF', 'SPX', 'TRUMP', 'TST', 'TUT', 'VINE', 'WIF'],
            'Gaming': ['ACE', 'AGLD', 'BEAMX', 'BIGTIME', 'CATI', 'ENJ', 'FORM', 'GALA', 'GUN', 'HMSTR', 'LOKA', 'MAVIA', 'MEMEFI', 'NOT', 'NXPC', 'PIXEL', 'PORTAL', 'RONIN', 'SONIC', 'VOXEL', 'WAXP', 'XAI', 'YGG'],
            'Infrastructure': ['AERGO', 'ALT', 'API3', 'ARKM', 'ARPA', 'ATA', 'AXL', 'BAT', 'BICO', 'BMT', 'CTK', 'CVC', 'CYBER', 'DENT', 'DIA', 'DYM', 'EIGEN', 'ENS', 'FIDA', 'G', 'GAS', 'GLM', 'GPS', 'GTC', 'HEI', 'HOOK', 'ID', 'IOTX', 'JASMY', 'KAITO', 'KEY', 'LAYER', 'LINK', 'LOOM', 'MASK', 'MAV', 'MDT', 'MTL', 'NULS', 'ORBS', 'OXT', 'POLYX', 'PYTH', 'QNT', 'RED', 'RENDER', 'SAFE', 'SFP', 'SIGN', 'SOON', 'SSV', 'T', 'TIA', 'TRB', 'TWT', 'UXLINK', 'W', 'WCT', 'ZRO'],
            'RWA': ['AVAX', 'CHR', 'DUSK', 'EPT', 'HIFI', 'ICP', 'INJ', 'LUMIA', 'OM', 'ONDO', 'PAXG', 'PLUME', 'RSR', 'SNX', 'TRU', 'USUAL'],
            'Metaverse': ['ALICE', 'AXS', 'COMBO', 'D', 'EDU', 'GHST', 'HIGH', 'ILV', 'MAGIC', 'MANA', 'MBOX', 'MOCA', 'SAND', 'SLP', 'TLM', 'VANRY'],
            'NFT': ['ANIME', 'APE', 'BLUR', 'BNX', 'CHZ', 'DAR', 'DEGO', 'DOOD', 'EPIC', 'FIO', 'GMT', 'IMX', 'ME', 'PROM'],
            'Payment': ['1000XEC', 'ACH', 'BCH', 'COTI', 'DGB', 'HUMA', 'LTC', 'STMX', 'XRP'],
            'PoW': ['BSV', 'BTC', 'CFX', 'CKB', 'DASH', 'ETC', 'ETHW', 'IOTA', 'KDA', 'NKN', 'ONT', 'RVN', 'SYS', 'XCN', 'XMR', 'XVG', 'ZEC', 'ZEN', 'ZIL'],
            'Storage': ['AR', 'BLZ', 'FIL', 'HOT', 'RARE', 'RIF', 'SC', 'STORJ', 'STX', 'SUPER', 'TNSR', 'WAL'],
            'Index': ['BTCDOM', 'DEFI'],
            'Privacy': ['LIT'],
            'Bitcoin Eco': ['BADGER'],
            'CEX': ['FTT']
        }
        
        # Narrative scoring weights (points awarded for each category)
        self.narrative_scores = {
            'AI': 4,           # Hottest narrative
            'RWA': 4,          # Real World Assets - very hot
            'Layer-1': 3,      # Strong fundamental narrative
            'Layer-2': 3,      # Scaling solutions
            'DeFi': 3,         # Proven utility
            'Gaming': 3,       # Growing sector
            'Infrastructure': 2, # Solid but not trending
            'Metaverse': 2,    # Moderate interest
            'NFT': 2,          # Established but cooling
            'Payment': 2,      # Utility focused
            'PoW': 2,          # Bitcoin/traditional crypto
            'Storage': 2,      # Niche but useful
            'Meme': 1,         # Volatile, low conviction
            'Index': 1,        # Passive instruments
            'Privacy': 1,      # Regulatory concerns
            'Bitcoin Eco': 1,  # Limited scope
            'CEX': 1           # Single token category
        }
    
        # Dynamic narrative scores (calculated from real market data)
        self.dynamic_narrative_scores = {}
        self.category_metrics_cache = {}
        self.category_metrics_updated = None
    
    async def calculate_token_score(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Calculate comprehensive token score based on 8 key indicators"""
        
        # First check if symbol is actively trading (not delisted)
        await self.update_active_symbols()
        if not self.is_symbol_active(symbol):
            return {
                "symbol": symbol,
                "total_score": 0,
                "error": "Symbol not actively trading (delisted/suspended)",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        score_breakdown = {}
        total_score = 0
        direction = "NEUTRAL"
        confidence_factors = []
        
        try:
            # 1. Open Interest Change Score (0-10)
            oi_score = await self._calculate_oi_score(symbol, market_data)
            score_breakdown["open_interest"] = oi_score
            total_score += oi_score
            if oi_score >= 8:
                confidence_factors.append("Strong OI momentum")
            
            # 2. Volume Spike Score (0-8) 
            volume_score = await self._calculate_volume_score(symbol, market_data)
            score_breakdown["volume_spike"] = volume_score
            total_score += volume_score
            if volume_score >= 6:
                confidence_factors.append("Significant volume spike")
            
            # 3. Funding Rate Extremes (0-6)
            funding_score, funding_direction = await self._calculate_funding_score(symbol)
            score_breakdown["funding_rate"] = funding_score
            total_score += funding_score
            if funding_score >= 4:
                confidence_factors.append(f"Extreme funding suggests {funding_direction}")
            
            # 4. Volatility Squeeze (0-5)
            volatility_score = await self._calculate_volatility_score(symbol)
            score_breakdown["volatility_squeeze"] = volatility_score
            total_score += volatility_score
            if volatility_score >= 3:
                confidence_factors.append("Low volatility squeeze detected")
            
            # 5. Whale Activity (0-6)
            whale_score, whale_direction = await self._calculate_whale_score(symbol)
            score_breakdown["whale_activity"] = whale_score
            total_score += whale_score
            if whale_score >= 4:
                confidence_factors.append(f"Whale activity favors {whale_direction}")
            
            # 6. Price Structure (0-4)
            structure_score, structure_signal = await self._calculate_structure_score(symbol)
            score_breakdown["price_structure"] = structure_score
            total_score += structure_score
            if structure_score >= 3:
                confidence_factors.append(f"Price near {structure_signal}")
            
            # 7. Sentiment/Narrative (0-4)
            sentiment_score, narrative = await self._calculate_sentiment_score(symbol)
            score_breakdown["sentiment"] = sentiment_score
            total_score += sentiment_score
            if sentiment_score >= 3:
                confidence_factors.append(f"Strong {narrative} narrative")
            
            # 8. Volume/MarketCap Ratio (0-3)
            vmc_score = await self._calculate_vmc_score(symbol, market_data)
            score_breakdown["volume_mcap_ratio"] = vmc_score
            total_score += vmc_score
            
            # 9. Long/Short Sentiment (0-4)
            longshort_score, ls_direction = await self._calculate_longshort_sentiment_score(symbol)
            score_breakdown["longshort_sentiment"] = longshort_score
            total_score += longshort_score
            if longshort_score >= 3:
                confidence_factors.append(f"Strong {ls_direction} sentiment from top traders")
            
            # Determine trading direction based on strongest signals
            direction = self._determine_direction(funding_direction, whale_direction, 
                                                funding_score, whale_score, 
                                                float(market_data.get('priceChangePercent', 0)))
            
            # Calculate confidence level
            confidence = self._calculate_confidence(total_score, len(confidence_factors))
            
            # Get category scores for all narratives (dynamic scoring)
            category_scores = {}
            if self.dynamic_narrative_scores:
                # Include all category scores for this token
                category_scores = self.dynamic_narrative_scores.copy()
            else:
                # Fallback to simplified scores if dynamic scores not available
                category_scores = {
                    'AI': 3, 'RWA': 3, 'Layer-1': 2, 'Layer-2': 2, 'DeFi': 2,
                    'Gaming': 2, 'Infrastructure': 2, 'Metaverse': 2, 'NFT': 2,
                    'Payment': 2, 'PoW': 2, 'Storage': 2, 'Meme': 1,
                    'Index': 1, 'Privacy': 1, 'Bitcoin Eco': 1, 'CEX': 1, 'General': 1
                }
            
            return {
                "symbol": symbol,
                "total_score": total_score,
                "max_score": 50,
                "direction": direction,
                "confidence": confidence,
                "confidence_factors": confidence_factors,
                "score_breakdown": score_breakdown,
                "narrative_type": narrative,  # Add narrative type for filtering
                "category_scores": category_scores,  # Add dynamic category scores for narrative analytics
                "recommendation": self._get_recommendation(total_score, direction),
                "risk_level": self._assess_risk_level(symbol, score_breakdown),
                "entry_timeframe": self._suggest_timeframe(total_score, volatility_score),
                "price_change_24h": float(market_data.get('priceChangePercent', 0)),
                "volume_24h": float(market_data.get('volume', 0)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating score for {symbol}: {e}")
            return {
                "symbol": symbol,
                "total_score": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _calculate_oi_score(self, symbol: str, market_data: Dict) -> int:
        """Calculate Open Interest change score (0-10) using Binance OI Statistics"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for OI score calculation for {symbol}")
                return 0
            
            # Get current OI
            current_oi_response = await self.client.get_open_interest(symbol)
            current_oi = float(current_oi_response['openInterest'])
            
            # Get historical OI statistics (last 30 periods of 5m = 2.5 hours of data)
            oi_stats = await self.client.get_open_interest_stats(symbol, period="5m", limit=30)
            
            if len(oi_stats) < 10:  # Need at least 10 data points for meaningful analysis
                self.logger.debug(f"Insufficient OI history for {symbol}: {len(oi_stats)} points")
                # Give baseline score based on current OI magnitude
                if current_oi > 1000000:  # High OI
                    return 3
                elif current_oi > 100000:  # Medium OI
                    return 2
                elif current_oi > 10000:   # Low OI
                    return 1
                else:
                    return 0
            
            # Calculate various OI change metrics
            historical_oi = [float(entry['sumOpenInterest']) for entry in oi_stats]
            
            # 1. Recent change (current vs 1 hour ago)
            hour_ago_oi = historical_oi[-12] if len(historical_oi) >= 12 else historical_oi[0]
            hour_change_pct = ((current_oi - hour_ago_oi) / hour_ago_oi) * 100 if hour_ago_oi > 0 else 0
            
            # 2. Short-term trend (last 30min average vs previous 30min average)
            recent_6_avg = sum(historical_oi[-6:]) / 6 if len(historical_oi) >= 6 else current_oi
            previous_6_avg = sum(historical_oi[-12:-6]) / 6 if len(historical_oi) >= 12 else hour_ago_oi
            trend_change_pct = ((recent_6_avg - previous_6_avg) / previous_6_avg) * 100 if previous_6_avg > 0 else 0
            
            # 3. Volatility of OI (how much OI is fluctuating)
            if len(historical_oi) >= 20:
                recent_20 = historical_oi[-20:]
                oi_avg = sum(recent_20) / len(recent_20)
                oi_std = (sum((x - oi_avg) ** 2 for x in recent_20) / len(recent_20)) ** 0.5
                oi_volatility = (oi_std / oi_avg) * 100 if oi_avg > 0 else 0
            else:
                oi_volatility = 0
            
            # Score based on multiple factors
            score = 0
            
            # Hour change scoring (0-4 points) - More realistic thresholds
            if abs(hour_change_pct) > 5:
                score += 4  # Very significant change
            elif abs(hour_change_pct) > 3:
                score += 3  # Significant change
            elif abs(hour_change_pct) > 1.5:
                score += 2  # Moderate change
            elif abs(hour_change_pct) > 0.5:
                score += 1  # Small but notable change
            
            # Trend scoring (0-3 points) - More realistic thresholds
            if abs(trend_change_pct) > 3:
                score += 3  # Strong trend
            elif abs(trend_change_pct) > 2:
                score += 2  # Moderate trend
            elif abs(trend_change_pct) > 0.5:
                score += 1  # Weak trend
            
            # Volatility scoring (0-3 points) - high volatility indicates active interest
            if oi_volatility > 5:
                score += 3  # Very active
            elif oi_volatility > 3:
                score += 2  # Active
            elif oi_volatility > 1:
                score += 1  # Somewhat active
            
            # Cap at maximum score
            score = min(score, 10)
            
            self.logger.debug(f"OI Score for {symbol}: {score}/10 (1h: {hour_change_pct:.2f}%, trend: {trend_change_pct:.2f}%, vol: {oi_volatility:.2f}%)")
            
            return score
            
        except Exception as e:
            error_msg = str(e)
            # Check if it's a delisted token error
            if "4108" in error_msg or "delivering or delivered or settling or closed" in error_msg:
                # Token is delisted/suspended - this should not happen if pre-filtering works
                self.logger.warning(f"Delisted token {symbol} passed through to OI scoring - should be filtered earlier")
                return 0
            else:
                # Other errors should be logged
                self.logger.error(f"Error calculating OI score for {symbol}: {e}")
                return 0
    
    async def _calculate_volume_score(self, symbol: str, market_data: Dict) -> int:
        """Calculate volume spike score (0-8)"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for volume score calculation for {symbol}")
                return 0
                
            current_volume = float(market_data.get('volume', 0))
            
            # Get hourly volume data for comparison
            klines = await self.client.get_klines(symbol, "1h", 25)  # Last 24 hours + current
            
            if len(klines) < 24:
                return 0
            
            # Calculate average volume (excluding current hour)
            hourly_volumes = [float(kline[5]) for kline in klines[:-1]]
            avg_volume = sum(hourly_volumes) / len(hourly_volumes) if hourly_volumes else 1
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Score based on volume spike magnitude
            if volume_ratio > 10:
                return 8  # Extreme volume spike
            elif volume_ratio > 5:
                return 7
            elif volume_ratio > 3:
                return 6
            elif volume_ratio > 2:
                return 4
            elif volume_ratio > 1.5:
                return 2
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Error calculating volume score for {symbol}: {e}")
            return 0
    
    async def _calculate_funding_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate funding rate extremes score (0-6) and direction"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for funding score calculation for {symbol}")
                return 0, "NEUTRAL"
                
            funding_response = await self.client.get_mark_price(symbol)
            funding_rate = float(funding_response['lastFundingRate'])
            
            direction = "NEUTRAL"
            score = 0
            
            # Extreme funding rates indicate potential squeezes
            if funding_rate > 0.002:  # > 0.2% (very extreme)
                score = 6
                direction = "SHORT"  # Over-leveraged longs, high squeeze potential
            elif funding_rate > 0.001:  # > 0.1%
                score = 5
                direction = "SHORT"
            elif funding_rate > 0.0005:  # > 0.05%
                score = 3
                direction = "SHORT"
            elif funding_rate < -0.002:  # < -0.2% (very extreme)
                score = 6
                direction = "LONG"  # Over-leveraged shorts, high squeeze potential
            elif funding_rate < -0.001:  # < -0.1%
                score = 5
                direction = "LONG"
            elif funding_rate < -0.0005:  # < -0.05%
                score = 3
                direction = "LONG"
            
            return score, direction
            
        except Exception as e:
            error_msg = str(e)
            if "4108" in error_msg or "delivering or delivered or settling or closed" in error_msg:
                # Token is delisted/suspended - this should not happen if pre-filtering works
                self.logger.warning(f"Delisted token {symbol} passed through to funding scoring - should be filtered earlier")
                return 0, "NEUTRAL"
            else:
                self.logger.error(f"Error calculating funding score for {symbol}: {e}")
                return 0, "NEUTRAL"
    
    async def _calculate_volatility_score(self, symbol: str) -> int:
        """Calculate volatility squeeze score (0-5)"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for volatility score calculation for {symbol}")
                return 0
                
            # Get recent klines for ATR calculation
            klines = await self.client.get_klines(symbol, "1h", 20)
            
            if len(klines) < 14:
                return 0
            
            # Calculate True Range for each period
            true_ranges = []
            for i in range(1, len(klines)):
                high = float(klines[i][2])
                low = float(klines[i][3])
                prev_close = float(klines[i-1][4])
                
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)
            
            # Calculate current vs average ATR
            current_atr = sum(true_ranges[-5:]) / 5  # Last 5 hours ATR
            avg_atr = sum(true_ranges[-14:]) / 14  # 14 hours ATR average
            
            atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1
            
            # Lower volatility (tighter range) gets higher score - indicates compression
            # Made thresholds more lenient to capture more opportunities
            if atr_ratio < 0.5:
                return 5  # Extreme compression
            elif atr_ratio < 0.7:
                return 4
            elif atr_ratio < 0.85:
                return 3
            elif atr_ratio < 1.0:
                return 2
            elif atr_ratio < 1.2:
                return 1
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Error calculating volatility score for {symbol}: {e}")
            return 0
    
    async def _calculate_whale_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate whale activity score (0-6) and direction"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for whale score calculation for {symbol}")
                return 0, "NEUTRAL"
                
            # Get order book depth to analyze whale activity
            order_book = await self.client.get_order_book(symbol, 500)
            
            # Analyze top 20 levels for whale walls
            bids = order_book['bids'][:20]
            asks = order_book['asks'][:20]
            
            # Calculate bid/ask volume and identify large orders
            total_bid_volume = sum(float(bid[1]) for bid in bids)
            total_ask_volume = sum(float(ask[1]) for ask in asks)
            
            # Find unusually large orders (whale walls)
            bid_volumes = [float(bid[1]) for bid in bids]
            ask_volumes = [float(ask[1]) for ask in asks]
            
            avg_bid_size = total_bid_volume / len(bids) if bids else 0
            avg_ask_size = total_ask_volume / len(asks) if asks else 0
            
            # Look for orders 5x larger than average
            large_bids = [vol for vol in bid_volumes if vol > avg_bid_size * 5]
            large_asks = [vol for vol in ask_volumes if vol > avg_ask_size * 5]
            
            # Calculate imbalance
            if total_bid_volume + total_ask_volume == 0:
                return 0, "NEUTRAL"
            
            imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume)
            
            # Score based on whale activity indicators
            score = 0
            direction = "NEUTRAL"
            
            # Large order walls indicate whale interest
            if len(large_bids) > len(large_asks) and imbalance > 0.3:
                score = 6 if imbalance > 0.6 else 4
                direction = "LONG"
            elif len(large_asks) > len(large_bids) and imbalance < -0.3:
                score = 6 if imbalance < -0.6 else 4
                direction = "SHORT"
            elif abs(imbalance) > 0.5:
                score = 3
                direction = "LONG" if imbalance > 0 else "SHORT"
            elif abs(imbalance) > 0.3:
                score = 2
                direction = "LONG" if imbalance > 0 else "SHORT"
            
            return score, direction
                
        except Exception as e:
            self.logger.error(f"Error calculating whale score for {symbol}: {e}")
            return 0, "NEUTRAL"
    
    async def _calculate_structure_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate price structure score (0-4) and structure signal"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for structure score calculation for {symbol}")
                return 0, "NEUTRAL"
                
            # Get recent price action for structure analysis
            klines = await self.client.get_klines(symbol, "15m", 40)  # 10 hours of 15m data
            
            if len(klines) < 20:
                return 0, "insufficient_data"
            
            # Extract price data
            highs = [float(kline[2]) for kline in klines]
            lows = [float(kline[3]) for kline in klines]
            closes = [float(kline[4]) for kline in klines]
            
            current_price = closes[-1]
            
            # Find key levels (recent highs/lows)
            recent_high = max(highs[-20:])  # 5 hour high
            recent_low = min(lows[-20:])   # 5 hour low
            daily_high = max(highs)
            daily_low = min(lows)
            
            # Calculate position in range
            if recent_high != recent_low:
                range_position = (current_price - recent_low) / (recent_high - recent_low)
            else:
                range_position = 0.5
            
            # Score based on position relative to key levels
            score = 0
            signal = ""
            
            # Breakout levels (higher score)
            if current_price >= recent_high * 0.999:  # Near/above recent high
                score = 4
                signal = "resistance_breakout"
            elif current_price <= recent_low * 1.001:  # Near/below recent low
                score = 4
                signal = "support_breakdown"
            elif range_position > 0.9:  # Near resistance
                score = 3
                signal = "approaching_resistance"
            elif range_position < 0.1:  # Near support
                score = 3
                signal = "approaching_support"
            elif 0.4 <= range_position <= 0.6:  # Middle of range
                score = 1
                signal = "range_middle"
            else:
                score = 0
                signal = "no_clear_structure"
            
            return score, signal
                
        except Exception as e:
            self.logger.error(f"Error calculating structure score for {symbol}: {e}")
            return 0, "error"
    
    async def _calculate_sentiment_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate sentiment/narrative score (0-4) based on dynamic category metrics"""
        base_symbol = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '')
        
        # Remove common prefixes from Binance that don't affect base symbol
        if base_symbol.startswith('1000'):
            base_symbol = base_symbol[4:]  # Remove 1000 prefix
        if base_symbol.startswith('1000000'):
            base_symbol = base_symbol[7:]  # Remove 1000000 prefix
        if base_symbol.startswith('1MB'):
            base_symbol = base_symbol[3:]  # Remove 1MB prefix for baby tokens
        
        # Check each category for the base symbol
        for category, tokens in self.token_categories.items():
            if base_symbol in tokens:
                # Use dynamic score if available, otherwise fallback to simplified default
                if self.dynamic_narrative_scores and category in self.dynamic_narrative_scores:
                    score = self.dynamic_narrative_scores[category]
                    return int(round(score)), category
                else:
                    # Simplified fallback scoring while dynamic scores are being calculated
                    fallback_scores = {
                        'AI': 3, 'RWA': 3, 'Layer-1': 2, 'Layer-2': 2, 'DeFi': 2,
                        'Gaming': 2, 'Infrastructure': 2, 'Metaverse': 2, 'NFT': 2,
                        'Payment': 2, 'PoW': 2, 'Storage': 2, 'Meme': 1,
                        'Index': 1, 'Privacy': 1, 'Bitcoin Eco': 1, 'CEX': 1
                    }
                    score = fallback_scores.get(category, 1)
                    return score, category
        
        # Default for tokens not in any specific category
        return 1, "General"
    
    async def _calculate_vmc_score(self, symbol: str, market_data: Dict) -> int:
        """Calculate Volume/MarketCap ratio score (0-3)"""
        try:
            volume_24h = float(market_data.get('volume', 0))
            quote_volume = float(market_data.get('quoteVolume', 0))
            
            # Use volume thresholds as proxy for activity level
            if volume_24h > 10000000:  # Very high activity
                return 3
            elif volume_24h > 5000000:  # High activity
                return 2
            elif volume_24h > 1000000:  # Moderate activity
                return 1
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Error calculating VMC score for {symbol}: {e}")
            return 0
    
    async def _calculate_longshort_sentiment_score(self, symbol: str) -> Tuple[int, str]:
        """Calculate Long/Short sentiment score (0-4) based on top trader positions"""
        try:
            if not self.client:
                self.logger.warning(f"No client available for Long/Short sentiment calculation for {symbol}")
                return 0, "NEUTRAL"
            
            # Get top trader long/short account ratio
            account_ratio_data = await self.client.get_top_long_short_account_ratio(symbol, period="5m", limit=12)
            
            if not account_ratio_data or len(account_ratio_data) < 6:
                return 0, "NEUTRAL"
            
            # Calculate current and historical ratios
            current_ratio = float(account_ratio_data[-1]['longShortRatio'])
            ratios = [float(entry['longShortRatio']) for entry in account_ratio_data]
            avg_ratio = sum(ratios) / len(ratios)
            
            # Calculate ratio change and extremity
            ratio_change = current_ratio - avg_ratio
            
            # Determine sentiment direction and strength
            if current_ratio > 1.0:  # More longs than shorts
                base_direction = "LONG"
                extremity = current_ratio - 1.0  # How far above 1.0
            else:  # More shorts than longs
                base_direction = "SHORT"
                extremity = 1.0 - current_ratio  # How far below 1.0
            
            # Calculate score based on extremity and trend
            score = 0
            
            # Score based on ratio extremity
            if extremity >= 0.4:  # Very extreme (e.g., 1.4+ or 0.6-)
                score += 2
            elif extremity >= 0.2:  # Moderate extreme (e.g., 1.2+ or 0.8-)
                score += 1
            
            # Score based on recent trend strength
            if len(ratios) >= 6:
                recent_trend = ratios[-3:] 
                earlier_trend = ratios[-6:-3]
                recent_avg = sum(recent_trend) / len(recent_trend)
                earlier_avg = sum(earlier_trend) / len(earlier_trend)
                trend_change = recent_avg - earlier_avg
                
                if abs(trend_change) >= 0.05:  # Strong trend change
                    score += 1
                    if abs(trend_change) >= 0.1:  # Very strong trend
                        score += 1
            
            # Bonus for contrarian signals (often more reliable)
            if base_direction == "SHORT" and current_ratio < 0.7:  # Heavy short bias
                score += 1  # Contrarian long opportunity
                direction = "CONTRARIAN_LONG"
            elif base_direction == "LONG" and current_ratio > 1.3:  # Heavy long bias  
                score += 1  # Contrarian short opportunity
                direction = "CONTRARIAN_SHORT"
            else:
                direction = base_direction
            
            # Cap score at 4
            score = min(score, 4)
            
            return score, direction
            
        except Exception as e:
            self.logger.error(f"Error calculating Long/Short sentiment score for {symbol}: {e}")
            return 0, "NEUTRAL"
    
    def _determine_direction(self, funding_direction: str, whale_direction: str, 
                           funding_score: int, whale_score: int, price_change: float) -> str:
        """Determine overall trading direction based on strongest signals with risk adjustment"""
        
        # NEW: Risk-adjusted approach instead of simple override
        signals = {
            'funding': {'direction': funding_direction, 'score': funding_score, 'weight': 0.4},
            'whale': {'direction': whale_direction, 'score': whale_score, 'weight': 0.3},
            'momentum': {'direction': 'LONG' if price_change > 5 else 'SHORT' if price_change < -5 else 'NEUTRAL', 
                        'score': min(abs(price_change) / 2, 5), 'weight': 0.3}
        }
        
        # Calculate weighted direction scores
        direction_scores = {'LONG': 0, 'SHORT': 0, 'NEUTRAL': 0, 'WATCH': 0}
        
        for signal_name, signal_data in signals.items():
            direction = signal_data['direction']
            score = signal_data['score']
            weight = signal_data['weight']
            
            if direction in direction_scores:
                direction_scores[direction] += score * weight
        
        # Find strongest direction
        strongest_direction = max(direction_scores.items(), key=lambda x: x[1])
        
        # Special handling for extreme funding (high priority but not absolute override)
        if funding_score >= 5:
            # If funding is extreme, add warning but don't necessarily override
            if strongest_direction[1] < 4:  # If other signals are weak
                return funding_direction + "_PRIORITY"  # Add priority flag
            else:
                return "CONFLICTED_" + strongest_direction[0]  # Mark as conflicted
        
        # For non-extreme funding, use weighted approach
        if strongest_direction[1] >= 2:
            return strongest_direction[0]
        else:
            return "WATCH"
    
    def _calculate_confidence(self, total_score: int, factor_count: int) -> str:
        """Calculate confidence level based on score and confirming factors"""
        # Updated thresholds for 50-point system (25-50 range for qualified opportunities)
        if total_score >= 40 and factor_count >= 4:
            return "HIGH"
        elif total_score >= 30 and factor_count >= 3:
            return "MEDIUM"
        elif total_score >= 25 and factor_count >= 2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _get_recommendation(self, score: int, direction: str) -> str:
        """Get trading recommendation based on score and direction with risk awareness"""
        
        # Handle special direction cases from improved _determine_direction
        if "_PRIORITY" in direction:
            base_direction = direction.replace("_PRIORITY", "")
            if score >= 30:
                return f"URGENT {base_direction} (Funding Squeeze Risk)"
            else:
                return f"CAUTION {base_direction} (Mixed Signals)"
        
        if "CONFLICTED_" in direction:
            base_direction = direction.replace("CONFLICTED_", "")
            return f"CONFLICTED SIGNALS - Consider {base_direction} with hedge"
        
        # Standard recommendations with risk adjustment
        if score >= 43:
            return f"STRONG {direction}" if direction not in ["NEUTRAL", "WATCH"] else "STRONG WATCH"
        elif score >= 35:
            return f"MODERATE {direction}" if direction not in ["NEUTRAL", "WATCH"] else "WATCH"
        elif score >= 30:
            return f"WEAK {direction}" if direction not in ["NEUTRAL", "WATCH"] else "MONITOR"
        elif score >= 25:
            return "WAIT FOR CONFIRMATION"
        else:
            return "AVOID"
    
    def _assess_risk_level(self, symbol: str, score_breakdown: Dict) -> str:
        """Assess risk level based on score components with funding rate awareness"""
        funding_score = score_breakdown.get('funding_rate', 0)
        volatility_score = score_breakdown.get('volatility_squeeze', 0)
        whale_score = score_breakdown.get('whale_activity', 0)
        
        # High risk conditions
        risk_factors = []
        
        if funding_score >= 5:
            risk_factors.append("Extreme funding (squeeze risk)")
        elif funding_score >= 3:
            risk_factors.append("High funding")
            
        if volatility_score >= 4:
            risk_factors.append("Volatility compression")
            
        if whale_score >= 5:
            risk_factors.append("Heavy whale activity")
        
        # Determine risk level
        if len(risk_factors) >= 2 or funding_score >= 5:
            return "HIGH"
        elif len(risk_factors) >= 1 or funding_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _suggest_timeframe(self, total_score: int, volatility_score: int) -> str:
        """Suggest entry timeframe based on analysis"""
        if total_score >= 45 and volatility_score >= 4:
            return "IMMEDIATE"  # High conviction + compression
        elif total_score >= 35:
            return "1-4 HOURS"  # Good setup
        elif total_score >= 25:
            return "4-12 HOURS"  # Wait for confirmation
        else:
            return "WAIT"
    
    async def scan_all_tokens(self) -> List[Dict[str, Any]]:
        """Scan all futures tokens and return scored opportunities"""
        try:
            if not self.client:
                self.logger.error("No client available for market scan")
                return []
                
            self.logger.info("Starting comprehensive market scan...")
            start_time = datetime.utcnow()
            
            # Get all 24hr ticker data in one efficient call
            all_tickers = await self.client.get_all_tickers()
            
            if not all_tickers:
                self.logger.error("No ticker data received")
                return []
            
            # Calculate dynamic category scores based on current market data
            self.logger.info("Calculating dynamic category sentiment scores...")
            await self._calculate_dynamic_category_scores(all_tickers)
            
            scored_tokens = []
            processed_count = 0
            skipped_count = 0
            
            # Filter and process tokens with improved filtering
            excluded_pairs = {
                'USDCUSDT',    # Stablecoin pair
                'TUSDUSDT',    # Stablecoin pair  
                'BUSDUSDT',    # Stablecoin pair
                'DAIUSDT',     # Stablecoin pair
                'FDUSDUSDT',   # Stablecoin pair
                'USDPUSDT',    # Stablecoin pair
                'SUSDUSDT',    # Stablecoin pair
                'EURUSDT',     # Forex pair
                'GBPUSDT',     # Forex pair
                'AUDUSDT',     # Forex pair
                # Add more excluded pairs as needed
            }
            
            usdt_tickers = [ticker for ticker in all_tickers 
                           if ticker['symbol'].endswith('USDT') 
                           and ticker['symbol'] not in excluded_pairs
                           and float(ticker['volume']) > 100000]  # Minimum volume filter
            
            # Get active trading symbols from exchange info to filter out delisted tokens
            try:
                exchange_info = await self.client.get_exchange_info()
                active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] 
                                if symbol['status'] == 'TRADING'}
                
                # Filter to only active trading symbols
                usdt_tickers = [ticker for ticker in usdt_tickers 
                              if ticker['symbol'] in active_symbols]
                
                self.logger.info(f"Filtered to {len(usdt_tickers)} active trading symbols with sufficient volume")
                
            except Exception as e:
                self.logger.warning(f"Could not get exchange info for filtering: {e}")
                self.logger.info(f"Processing {len(usdt_tickers)} tokens with sufficient volume...")
            
            # Process each token with scoring
            for ticker in usdt_tickers:
                symbol = ticker['symbol']
                
                try:
                    score_data = await self.calculate_token_score(symbol, ticker)
                    
                    # Filter tokens with minimum score threshold (20+) before storing to Redis
                    # This reduces Redis memory usage and improves tool performance
                    if score_data.get('total_score', 0) >= 20:  # Only store quality opportunities (threshold: 20)
                        scored_tokens.append(score_data)
                    else:
                        skipped_count += 1
                        
                    processed_count += 1
                    
                    # Log progress every 50 tokens
                    if processed_count % 50 == 0:
                        quality_count = len(scored_tokens)
                        self.logger.info(f"Processed {processed_count}/{len(usdt_tickers)} tokens... "
                                       f"Found {quality_count} quality opportunities (score ≥20)")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "4108" in error_msg or "delivering or delivered or settling or closed" in error_msg:
                        # Delisted token - just skip silently
                        skipped_count += 1
                    else:
                        # Other errors should be logged
                        self.logger.error(f"Error scoring {symbol}: {e}")
                    continue
            
            # Sort by total score
            scored_tokens.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Cache only quality results (score ≥ 20)
            await self._cache_market_opportunities(scored_tokens)
            
            scan_duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Enhanced logging with quality metrics
            self.logger.info(f"Market scan completed in {scan_duration:.2f}s. "
                           f"Quality opportunities (≥20): {len(scored_tokens)} from {processed_count} analyzed "
                           f"({skipped_count} below threshold or errors)")
            
            # Log quality distribution
            if scored_tokens:
                high_quality = len([t for t in scored_tokens if t['total_score'] >= 30])
                medium_quality = len([t for t in scored_tokens if 25 <= t['total_score'] < 30])
                low_quality = len([t for t in scored_tokens if 20 <= t['total_score'] < 25])
                
                self.logger.info(f"Quality distribution: High (≥30): {high_quality}, "
                               f"Medium (25-29): {medium_quality}, Low (20-24): {low_quality}")
            
            return scored_tokens
            
        except Exception as e:
            self.logger.error(f"Error in market scan: {e}")
            return []
    
    async def get_cached_opportunities(self) -> List[Dict[str, Any]]:
        """Get cached market opportunities - ONLY uses cache, never makes API calls"""
        if not self.redis:
            self.logger.warning("No Redis available - returning empty list")
            return []
        
        try:
            self.logger.debug("Retrieving cached opportunities from Redis...")
            
            # Increased timeout to prevent premature fallback (changed from 3s to 30s)
            import asyncio
            try:
                cached_data = await asyncio.wait_for(self.redis.get("market_opportunities"), timeout=30.0)
            except asyncio.TimeoutError:
                self.logger.warning("Redis timeout - returning empty list")
                return []
            
            if cached_data:
                self.logger.debug(f"Raw cached data length: {len(cached_data)} characters")
                data = json.loads(cached_data)
                opportunities = data.get("opportunities", [])
                self.logger.info(f"Retrieved {len(opportunities)} cached opportunities from Redis")
                
                # Log summary for debugging
                if opportunities:
                    high_confidence = len([o for o in opportunities if o.get('confidence') == 'HIGH'])
                    avg_score = sum(o.get('total_score', 0) for o in opportunities) / len(opportunities)
                    self.logger.debug(f"Cache summary: {high_confidence} HIGH confidence, avg score: {avg_score:.1f}")
                
                return opportunities
            else:
                self.logger.warning("No cached opportunities found in Redis")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error retrieving cached opportunities: {e}")
            return []
    
    async def _cache_market_opportunities(self, opportunities: List[Dict]):
        """Cache market opportunities with metadata"""
        if not self.redis:
            return
        
        try:
            cache_data = {
                "opportunities": opportunities,
                "timestamp": datetime.utcnow().isoformat(),
                "total_analyzed": len(opportunities),
                "cache_version": "1.0"
            }
            
            # Cache for 10 minutes (longer than scan interval + scan duration)
            await self.redis.setex("market_opportunities", 600, json.dumps(cache_data))
            
            # Also cache summary statistics
            summary = self._create_market_summary(opportunities)
            await self.redis.setex("market_summary", 600, json.dumps(summary))
            
        except Exception as e:
            self.logger.error(f"Error caching opportunities: {e}")
    
    def _create_market_summary(self, opportunities: List[Dict]) -> Dict:
        """Create market summary from opportunities"""
        if not opportunities:
            return {"error": "No opportunities available"}
        
        return {
            "total_opportunities": len(opportunities),
            "high_confidence": len([o for o in opportunities if o.get('confidence') == 'HIGH']),
            "long_signals": len([o for o in opportunities if o.get('direction') == 'LONG']),
            "short_signals": len([o for o in opportunities if o.get('direction') == 'SHORT']),
            "watch_signals": len([o for o in opportunities if o.get('direction') == 'WATCH']),
            "avg_score": sum(o.get('total_score', 0) for o in opportunities) / len(opportunities),
            "top_5": opportunities[:5],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_cached_oi(self, symbol: str) -> Optional[float]:
        """Get cached OI value for comparison"""
        if not self.redis:
            return None
        try:
            cached = await self.redis.get(f"oi:{symbol}")
            return float(cached) if cached else None
        except:
            return None
    
    async def _cache_oi(self, symbol: str, oi_value: float):
        """Cache OI value for future comparison"""
        if self.redis:
            try:
                # Cache for 3 hours
                await self.redis.setex(f"oi:{symbol}", 10800, str(oi_value))
            except:
                pass
    
    async def update_active_symbols(self):
        """Update list of active trading symbols (like TickerCache)"""
        try:
            if not self.client:
                self.logger.warning("No client available for updating active symbols")
                return
                
            # Check if update is needed (every 30 minutes)
            if (self.exchange_info_updated and 
                datetime.utcnow() - self.exchange_info_updated < timedelta(minutes=30)):
                return

            self.logger.info("Updating active symbols from exchange info...")
            
            exchange_info = await self.client.get_exchange_info()
            active_symbols = set()
            
            symbols_data = exchange_info.get('symbols', [])
            
            for symbol_info in symbols_data:
                symbol = symbol_info.get('symbol', '')
                status = symbol_info.get('status', '')
                
                # Only include symbols that are actively trading
                # Exclude: SETTLING (delisted), CLOSE, AUCTION_MATCH, etc.
                if status == 'TRADING':
                    active_symbols.add(symbol)
            
            self.active_symbols = active_symbols
            self.exchange_info_updated = datetime.utcnow()
            
            self.logger.info(f"Active symbols updated: {len(active_symbols)} trading symbols")
            
            # Log some examples of excluded symbols for debugging
            all_symbols = {s.get('symbol', '') for s in symbols_data}
            excluded_symbols = all_symbols - active_symbols
            if excluded_symbols:
                excluded_sample = list(excluded_symbols)[:5]
                self.logger.info(f"Excluded symbols (sample): {excluded_sample}")
                
        except Exception as e:
            self.logger.error(f"Failed to update active symbols: {e}")
            # Keep existing active_symbols if update fails
    
    def is_symbol_active(self, symbol: str) -> bool:
        """Check if symbol is actively trading (not delisted)"""
        # If no active symbols list, assume it's active (fallback)
        if not self.active_symbols:
            return True
        return symbol in self.active_symbols
    
    async def _calculate_dynamic_category_scores(self, all_tickers: List[Dict]) -> Dict[str, float]:
        """Calculate dynamic sentiment scores for each category based on real market data"""
        try:
            # Initialize category metrics
            category_metrics = {}
            for category in self.token_categories.keys():
                category_metrics[category] = {
                    'total_volume': 0,
                    'total_tokens': 0,
                    'active_tokens': 0,
                    'total_price_change': 0,
                    'positive_tokens': 0,
                    'avg_volume': 0,
                    'avg_price_change': 0,
                    'volume_score': 0,
                    'performance_score': 0,
                    'activity_score': 0,
                    'final_score': 0
                }
            
            # Process all tickers and categorize them
            for ticker in all_tickers:
                symbol = ticker['symbol']
                if not symbol.endswith('USDT'):
                    continue
                    
                # Get base symbol and find category
                base_symbol = symbol.replace('USDT', '')
                if base_symbol.startswith('1000'):
                    base_symbol = base_symbol[4:]
                if base_symbol.startswith('1000000'):
                    base_symbol = base_symbol[7:]
                if base_symbol.startswith('1MB'):
                    base_symbol = base_symbol[3:]
                
                # Find which category this token belongs to
                token_category = None
                for category, tokens in self.token_categories.items():
                    if base_symbol in tokens:
                        token_category = category
                        break
                
                if not token_category:
                    token_category = 'General'  # Default category
                    if 'General' not in category_metrics:
                        category_metrics['General'] = {
                            'total_volume': 0, 'total_tokens': 0, 'active_tokens': 0,
                            'total_price_change': 0, 'positive_tokens': 0,
                            'avg_volume': 0, 'avg_price_change': 0,
                            'volume_score': 0, 'performance_score': 0, 'activity_score': 0, 'final_score': 0
                        }
                
                # Extract metrics
                volume = float(ticker.get('volume', 0))
                price_change = float(ticker.get('priceChangePercent', 0))
                
                # Only include tokens with meaningful volume
                if volume >= 100000:  # Minimum volume threshold
                    metrics = category_metrics[token_category]
                    metrics['total_volume'] += volume
                    metrics['active_tokens'] += 1
                    metrics['total_price_change'] += price_change
                    if price_change > 0:
                        metrics['positive_tokens'] += 1
                
                metrics['total_tokens'] += 1
            
            # Calculate averages and scores for each category
            all_volumes = []
            all_performance = []
            
            for category, metrics in category_metrics.items():
                if metrics['active_tokens'] > 0:
                    metrics['avg_volume'] = metrics['total_volume'] / metrics['active_tokens']
                    metrics['avg_price_change'] = metrics['total_price_change'] / metrics['active_tokens']
                    metrics['positive_ratio'] = metrics['positive_tokens'] / metrics['active_tokens']
                    
                    all_volumes.append(metrics['avg_volume'])
                    all_performance.append(metrics['avg_price_change'])
            
            # Normalize scores across categories (0-4 scale)
            if all_volumes and all_performance:
                max_volume = max(all_volumes) if all_volumes else 1
                min_volume = min(all_volumes) if all_volumes else 0
                max_performance = max(all_performance) if all_performance else 1
                min_performance = min(all_performance) if all_performance else -1
                
                volume_range = max_volume - min_volume if max_volume != min_volume else 1
                performance_range = max_performance - min_performance if max_performance != min_performance else 1
                
                for category, metrics in category_metrics.items():
                    if metrics['active_tokens'] > 0:
                        # Volume score (0-2 points): Higher average volume = higher score
                        volume_normalized = (metrics['avg_volume'] - min_volume) / volume_range
                        metrics['volume_score'] = volume_normalized * 2
                        
                        # Performance score (0-2 points): Better price performance = higher score
                        performance_normalized = (metrics['avg_price_change'] - min_performance) / performance_range
                        metrics['performance_score'] = performance_normalized * 2
                        
                        # Activity score (0-1 point): Based on number of active tokens and positive ratio
                        activity_factor = min(metrics['active_tokens'] / 10, 1.0)  # Bonus for having many active tokens
                        positive_factor = metrics['positive_ratio']  # Bonus for having positive tokens
                        metrics['activity_score'] = (activity_factor * 0.5) + (positive_factor * 0.5)
                        
                        # Final score (0-4): Weighted combination
                        metrics['final_score'] = (
                            metrics['volume_score'] * 0.4 +      # 40% volume weight
                            metrics['performance_score'] * 0.4 + # 40% performance weight  
                            metrics['activity_score'] * 0.2      # 20% activity weight
                        )
                        
                        # Ensure score is between 0 and 4
                        metrics['final_score'] = max(0, min(4, metrics['final_score']))
                    else:
                        metrics['final_score'] = 1  # Default score for categories with no active tokens
            
            # Extract final scores for each category
            dynamic_scores = {}
            for category, metrics in category_metrics.items():
                dynamic_scores[category] = round(metrics['final_score'], 2)
            
            # Cache the results
            self.dynamic_narrative_scores = dynamic_scores
            self.category_metrics_cache = category_metrics
            self.category_metrics_updated = datetime.utcnow()
            
            # Log the dynamic scores for transparency
            self.logger.info("📊 Dynamic Category Sentiment Scores:")
            sorted_categories = sorted(dynamic_scores.items(), key=lambda x: x[1], reverse=True)
            for category, score in sorted_categories[:10]:  # Top 10
                metrics = category_metrics.get(category, {})
                active_tokens = metrics.get('active_tokens', 0)
                avg_change = metrics.get('avg_price_change', 0)
                self.logger.info(f"   {category}: {score:.2f}/4 ({active_tokens} tokens, {avg_change:+.2f}% avg)")
            
            return dynamic_scores
            
        except Exception as e:
            self.logger.error(f"Error calculating dynamic category scores: {e}")
            # Fallback to simplified hardcoded scores if calculation fails
            return {
                'AI': 3, 'RWA': 3, 'Layer-1': 2.5, 'Layer-2': 2.5, 'DeFi': 2.5,
                'Gaming': 2, 'Infrastructure': 2, 'Metaverse': 2, 'NFT': 2,
                'Payment': 2, 'PoW': 2, 'Storage': 2, 'Meme': 1.5,
                'Index': 1, 'Privacy': 1, 'Bitcoin Eco': 1, 'CEX': 1, 'General': 1
            }
    
    async def get_category_insights(self) -> Dict[str, Any]:
        """Get insights about category performance for market analysis"""
        if not self.category_metrics_cache:
            return {"error": "Category metrics not available"}
        
        insights = {
            "top_performing_categories": [],
            "most_active_categories": [],
            "category_breakdown": self.category_metrics_cache,
            "last_updated": self.category_metrics_updated.isoformat() if self.category_metrics_updated else None
        }
        
        # Get top performing categories by score
        sorted_by_score = sorted(
            [(cat, metrics) for cat, metrics in self.category_metrics_cache.items()],
            key=lambda x: x[1]['final_score'],
            reverse=True
        )
        
        insights["top_performing_categories"] = [
            {
                "category": cat,
                "score": metrics['final_score'],
                "avg_price_change": metrics['avg_price_change'],
                "active_tokens": metrics['active_tokens'],
                "total_volume": metrics['total_volume']
            }
            for cat, metrics in sorted_by_score[:10]
            if metrics['active_tokens'] > 0
        ]
        
        # Get most active categories by volume
        sorted_by_volume = sorted(
            [(cat, metrics) for cat, metrics in self.category_metrics_cache.items()],
            key=lambda x: x[1]['total_volume'],
            reverse=True
        )
        
        insights["most_active_categories"] = [
            {
                "category": cat,
                "total_volume": metrics['total_volume'],
                "active_tokens": metrics['active_tokens'],
                "avg_volume": metrics['avg_volume']
            }
            for cat, metrics in sorted_by_volume[:10]
            if metrics['active_tokens'] > 0
        ]
        
        return insights
