# Premium Futures MCP - Folder Organization

This document explains the organized folder structure of the Premium Futures MCP project.

## 📁 Project Structure

```
premium_futures_mcp/
├── 📂 src/                         # Source code
│   └── premium_futures_mcp/        # Main package
├── 📂 docs/                        # Documentation
│   ├── BINANCE_CATEGORIES.md       # Token categories
│   ├── COMPREHENSIVE_NARRATIVE_SYSTEM.md
│   ├── DEPLOYMENT_GUIDE.md         # Deployment instructions
│   ├── DOCKER_SETUP_GUIDE.md       # Docker setup
│   ├── FIX_SUMMARY.md              # Bug fix summaries
│   ├── INSTALLATION.md             # Installation guide
│   ├── NARRATIVE_PLAYS_EXPLAINED.md
│   └── WINDOWS_SETUP_GUIDE.md      # Windows setup
├── 📂 tests/                       # Test files
│   ├── test_*.py                   # All test scripts
│   └── debug_*.py                  # Debug scripts
├── 📂 scripts/                     # Utility scripts
│   └── publish.py                  # Publishing script
├── 📂 docker/                      # Docker configuration
│   └── docker-compose.yml          # Docker Compose file
├── 📂 examples/                    # Example configurations
│   └── config_example.py           # Example config
├── 📂 data/                        # Runtime data
├── 📂 logs/                        # Log files
├── 📂 dist/                        # Build artifacts
├── 🔗 docker-compose.yml           # Symlink to docker/docker-compose.yml
├── 📄 Dockerfile                   # Docker build file
├── 📄 README.md                    # Main documentation
├── 📄 setup.py                     # Package setup
├── 📄 pyproject.toml               # Modern Python packaging
├── 📄 requirements.txt             # Dependencies
└── 📄 .gitignore                   # Git ignore rules
```

## 🚀 Quick Start Commands

### Development
```bash
# Install for development
pip install -e .

# Run tests
python -m pytest tests/

# Run specific test
python tests/test_market_intelligence.py
```

### Docker Operations
```bash
# Start all services
docker-compose up -d

# View logs
docker logs premium-market-monitor

# Restart services
docker-compose restart
```

### Scripts
```bash
# Publish to PyPI
python scripts/publish.py
```

## 📚 Documentation

- **Installation**: See `docs/INSTALLATION.md`
- **Docker Setup**: See `docs/DOCKER_SETUP_GUIDE.md`
- **Deployment**: See `docs/DEPLOYMENT_GUIDE.md`
- **Windows Setup**: See `docs/WINDOWS_SETUP_GUIDE.md`

## 🧪 Testing

All test files are in the `tests/` directory:
- `test_market_intelligence.py` - Market intelligence tests
- `test_scoring_breakdown.py` - Scoring system tests
- `test_dynamic_sentiment.py` - Sentiment analysis tests
- And many more...

## 🐳 Docker

Docker configuration is in the `docker/` directory:
- `docker-compose.yml` - Service definitions
- Symlinked to root for easy access

## 📝 Examples

Configuration examples are in the `examples/` directory:
- `config_example.py` - Example configuration file

This organization makes the project much cleaner and easier to navigate!
