"""
24/7 Background Market Monitor for Premium Binance Futures MCP Server

This service continuously monitors the market and pre-calculates opportunities
to provide instant responses to user queries instead of real-time API calls.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional
import redis.asyncio as redis
from .market_intelligence import MarketIntelligenceService
from .public_client import PublicBinanceClient


class MarketMonitor:
    """24/7 background market monitoring service"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.intelligence_service: Optional[MarketIntelligenceService] = None
        self.redis_client: Optional[redis.Redis] = None
        self.public_client: Optional[PublicBinanceClient] = None
        self.update_interval = 200  # 3 minutes and 20 seconds
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    async def initialize(self):
        """Initialize all services"""
        try:
            # Initialize Redis client
            self.redis_client = await self._get_redis_client()
            
            # Initialize Public Binance client (no API keys needed)
            self.public_client = PublicBinanceClient(testnet=self.testnet)
            
            # Initialize market intelligence service
            self.intelligence_service = MarketIntelligenceService(
                self.public_client, 
                self.redis_client
            )
            
            self.logger.info("Market monitor services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize market monitor: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous market monitoring"""
        if not await self.initialize():
            self.logger.error("Failed to initialize, exiting...")
            return
            
        self.running = True
        self.logger.info("Starting 24/7 market monitoring service...")
        
        # Use the public client context manager for the entire monitoring session
        async with self.public_client:
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while self.running:
                try:
                    start_time = datetime.utcnow()
                    self.logger.info(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting market scan...")
                    
                    # Perform comprehensive market scan
                    opportunities = await self.intelligence_service.scan_all_tokens()
                    
                    scan_duration = (datetime.utcnow() - start_time).total_seconds()
                    
                    if opportunities:
                        # Log scan results
                        self.logger.info(f"Market scan completed in {scan_duration:.2f}s")
                        self.logger.info(f"Found {len(opportunities)} opportunities")
                        
                        # Log top opportunities
                        await self._log_top_opportunities(opportunities)
                        
                        # Check for significant market changes
                        await self._check_market_alerts(opportunities)
                        
                        consecutive_errors = 0  # Reset error counter on success
                        
                    else:
                        self.logger.warning("No opportunities found in market scan")
                    
                    # Calculate next scan time
                    next_scan_time = datetime.utcnow().strftime('%H:%M:%S')
                    self.logger.info(f"Next scan in {self.update_interval}s at ~{next_scan_time}")
                    
                    # Wait for next scan
                    for _ in range(self.update_interval):
                        if not self.running:
                            break
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    consecutive_errors += 1
                    self.logger.error(f"Market monitor error ({consecutive_errors}/{max_consecutive_errors}): {e}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        self.logger.critical("Too many consecutive errors, stopping monitor")
                        break
                    
                    # Exponential backoff for errors
                    error_delay = min(60, 10 * consecutive_errors)
                    self.logger.info(f"Waiting {error_delay}s before retry...")
                    await asyncio.sleep(error_delay)
        
        await self.cleanup()
        self.logger.info("Market monitor stopped")
    
    async def _log_top_opportunities(self, opportunities):
        """Log top opportunities for monitoring"""
        if not opportunities:
            return
            
        # Filter high confidence opportunities
        high_confidence = [opp for opp in opportunities if opp.get('confidence') == 'HIGH']
        medium_confidence = [opp for opp in opportunities if opp.get('confidence') == 'MEDIUM']
        
        self.logger.info(f"Opportunity Summary:")
        self.logger.info(f"  High Confidence: {len(high_confidence)}")
        self.logger.info(f"  Medium Confidence: {len(medium_confidence)}")
        self.logger.info(f"  Total Analyzed: {len(opportunities)}")
        
        # Log top 5 opportunities
        top_5 = opportunities[:5]
        self.logger.info("Top 5 Opportunities:")
        for i, opp in enumerate(top_5, 1):
            symbol = opp['symbol']
            score = opp['total_score']
            max_score = opp.get('max_score', 50)  # Default to 50 for the 9-factor system
            direction = opp['direction']
            confidence = opp['confidence']
            recommendation = opp['recommendation']
            
            self.logger.info(f"  {i}. {symbol}: {score}/{max_score} ({confidence}) - {direction} - {recommendation}")
    
    async def _check_market_alerts(self, opportunities):
        """Check for significant market changes and log alerts"""
        try:
            # Check for extreme opportunities (score > 50)
            extreme_opportunities = [opp for opp in opportunities if opp['total_score'] > 50]
            
            if extreme_opportunities:
                self.logger.warning(f"🚨 EXTREME OPPORTUNITIES DETECTED ({len(extreme_opportunities)}):")
                for opp in extreme_opportunities:
                    max_score = opp.get('max_score', 50)
                    self.logger.warning(f"   🔥 {opp['symbol']}: {opp['total_score']}/{max_score} - {opp['recommendation']}")
            
            # Check for funding rate extremes
            funding_extremes = [
                opp for opp in opportunities 
                if opp.get('score_breakdown', {}).get('funding_rate', 0) >= 5
            ]
            
            if funding_extremes:
                self.logger.info(f"💸 Funding Rate Extremes: {len(funding_extremes)} tokens")
                for opp in funding_extremes[:3]:  # Top 3
                    self.logger.info(f"   ⚡ {opp['symbol']}: {opp['direction']} (squeeze potential)")
            
            # Check for volatility squeezes
            vol_squeezes = [
                opp for opp in opportunities 
                if opp.get('score_breakdown', {}).get('volatility_squeeze', 0) >= 4
            ]
            
            if vol_squeezes:
                self.logger.info(f"🌀 Volatility Squeezes: {len(vol_squeezes)} tokens ready for breakout")
            
        except Exception as e:
            self.logger.error(f"Error checking market alerts: {e}")
    
    async def _get_redis_client(self) -> Optional[redis.Redis]:
        """Get Redis client for caching"""
        try:
            # Try Docker network first, then localhost fallback (with password)
            redis_urls = [
                "redis://:ilikeMyself1100@premium-redis:6379",  # Docker network with password
                "redis://:ilikeMyself1100@localhost:6379"       # Local fallback with password
            ]
            
            for redis_url in redis_urls:
                try:
                    redis_client = await redis.from_url(
                        redis_url, 
                        decode_responses=True,
                        socket_timeout=5,
                        socket_connect_timeout=5
                    )
                    
                    # Test connection
                    await redis_client.ping()
                    self.logger.info(f"Redis connection established: {redis_url}")
                    return redis_client
                    
                except Exception as e:
                    self.logger.debug(f"Failed to connect to {redis_url}: {e}")
                    continue
            
            # If all connections fail
            raise Exception("All Redis connection attempts failed")
            
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}. Running without cache.")
            return None
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.public_client:
                await self.public_client.close()
                
            self.logger.info("Resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class MarketMonitorManager:
    """Manager for market monitor service with restart capabilities"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.monitor = None
        self.logger = logging.getLogger(__name__)
        
    async def start_with_restart(self, max_restarts: int = 5):
        """Start monitor with automatic restart on failure"""
        restart_count = 0
        
        while restart_count < max_restarts:
            try:
                self.logger.info(f"Starting market monitor (attempt {restart_count + 1}/{max_restarts})")
                
                self.monitor = MarketMonitor(self.testnet)
                await self.monitor.start_monitoring()
                
                # If we reach here, monitoring stopped normally
                break
                
            except Exception as e:
                restart_count += 1
                self.logger.error(f"Market monitor crashed: {e}")
                
                if restart_count < max_restarts:
                    restart_delay = min(300, 60 * restart_count)  # Max 5 minutes
                    self.logger.info(f"Restarting in {restart_delay}s...")
                    await asyncio.sleep(restart_delay)
                else:
                    self.logger.critical("Max restarts reached, giving up")
                    break


# CLI entry point for background service
async def main():
    """Main entry point for market monitor"""
    import os
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/market_monitor.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Check if testnet mode
    testnet = os.getenv("BINANCE_TESTNET", "false").lower() == "true"
    
    logger.info("Premium Binance Futures Market Monitor starting...")
    logger.info(f"Mode: {'Testnet' if testnet else 'Mainnet'}")
    logger.info("ℹ️  No API keys required - using public market data only")
    
    # Start monitor with restart capability
    manager = MarketMonitorManager(testnet=testnet)
    
    try:
        await manager.start_with_restart(max_restarts=10)
    except KeyboardInterrupt:
        logger.info("Market monitor stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
