# Installation Guide for Premium Futures MCP

## Architecture Overview

This system consists of:
- **Docker Services**: Market Monitor + Redis Cache + Key Server
- **Local MCP**: Installed on your PC, connects to Docker services

## Quick Setup

### 1. Start Docker Services (Required)
```bash
# Clone and start the services
git clone https://github.com/alexcandrabersiva/premium_futures_mcp
cd premium_futures_mcp
docker-compose up -d
```

This starts:
- Redis cache on `localhost:6379`
- Market monitor (scans and scores tokens)
- Key server on `localhost:8080`

### 2. Install MCP Package Locally
```bash
# Install the MCP package on your local machine
pip install -e .
```

### 3. Use in Your MCP Client
The MCP tools will automatically connect to Redis cache running in Docker.

## Dependencies

### Automatically Installed (Local MCP Client)
- `mcp>=1.0.0` - MCP protocol implementation
- `httpx>=0.25.0` - HTTP client for API calls
- `aiohttp>=3.8.0` - Async HTTP client for Binance API
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variable management
- `aioredis>=2.0.0` - Redis client for accessing cached data

### Docker-Only Dependencies (Not needed locally)
- `fastapi` and `uvicorn` - Only needed for the premium key server running in Docker
- `numpy` and `pandas` - Only needed for advanced analytics in Docker services

**Important**: Previous versions (1.2.3 and earlier) incorrectly included `fastapi`/`uvicorn` 
as local dependencies, which could cause "TimeoutError" conflicts. Version 1.2.4+ fixes this.

### System Requirements
- Docker and Docker Compose
- Python 3.10+
- Network access to `localhost:6379` (Redis) and `localhost:8080` (Key Server)

## How It Works

1. **Docker Market Monitor** scans all Binance futures tokens every 5 minutes
2. **Applies 9-factor scoring** (Open Interest, Volume, Funding, etc.)
3. **Caches results** in Redis with opportunities scored 25-50/50
4. **Local MCP tools** fetch pre-analyzed data from Redis cache
5. **No API keys needed** - uses public Binance endpoints only

## Troubleshooting

**Error: "No module named 'aioredis'"**
- Solution: Ensure you installed with `pip install -e .`

**Error: "Cannot connect to Redis"**
- Solution: Ensure Docker services are running: `docker-compose up -d`
- Check: `docker ps` should show 3 running containers

**Error: "No market opportunities found"**
- Solution: Wait 5-10 minutes for initial market scan to complete
- Check: `docker logs premium-market-monitor` for scan progress

**Error: "ModuleNotFoundError: No module named 'premium_futures_mcp'"**
- Solution: Install from project root: `pip install -e .`
