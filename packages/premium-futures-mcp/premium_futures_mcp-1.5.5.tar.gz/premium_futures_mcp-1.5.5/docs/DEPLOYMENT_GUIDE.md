# Premium Futures MCP - Deployment Guide

## 📋 Table of Contents
- [Deployment Architecture](#-deployment-architecture)
- [Docker Deployment](#-docker-deployment)
- [Systemd Deployment](#-systemd-deployment)
- [Member Key Management](#-member-key-management)
- [Security Considerations](#-security-considerations)

## 🚀 Deployment Architecture

### Overview
The Premium Futures MCP uses a **self-hosted model** where you run your own premium server instance. This eliminates the need to republish to PyPI for each new member key.

```
Your Business Model:
┌─────────────────────────────────────────────────────────────┐
│                     Your VPS/Server                        │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Premium MCP     │  │ Key Management  │  │ Member Keys │ │
│  │ Server          │  │ API/CLI         │  │ Database    │ │
│  │ (Port 8000)     │  │ (Port 8080)     │  │ (SQLite)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           ▲                      ▲                         │
└───────────┼──────────────────────┼─────────────────────────┘
            │                      │
            │                      │ Key Management
            │ Premium MCP Access   │ (You Only)
            │                      │
    ┌───────▼──────┐      ┌────────▼────────┐
    │   Member A   │      │      You        │
    │  (Paid Sub)  │      │   (Admin)       │
    │              │      │                 │
    │ ┌─────────┐  │      │ ┌─────────────┐ │
    │ │MCP      │  │      │ │Key Manager  │ │
    │ │Client + │  │      │ │CLI/Bot      │ │
    │ │Mem Key  │  │      │ └─────────────┘ │
    │ └─────────┘  │      └─────────────────┘
    └──────────────┘
```

## 📋 Step-by-Step Deployment

### 1. Deploy Premium Server on Your VPS

```bash
# On your VPS
git clone https://github.com/yourusername/premium_futures_mcp.git
cd premium_futures_mcp

# Install dependencies
pip install -e .

# Set environment variables
export BINANCE_API_KEY="your_api_key"
export BINANCE_SECRET_KEY="your_secret_key"
export PREMIUM_KEYS_DB="/opt/premium_mcp/keys.db"
export PREMIUM_BOT_ADMIN_TOKEN="your-secure-admin-token"

# Start premium MCP server
python -m premium_futures_mcp.server --host 0.0.0.0 --port 8000

# Start key management bot (separate terminal)
python -m premium_futures_mcp.key_bot --host 0.0.0.0 --port 8080
```

### 2. Generate Member Keys (No PyPI Updates Needed!)

You have multiple options for generating member keys for your premium customers:

#### Option A: Using the Python CLI

```bash
# Generate key for new paying customer
python -m premium_futures_mcp.key_manager generate \
  --member-id "customer_001" \
  --email "customer@example.com" \
  --validity-days 365

# Output:
# ✅ Successfully generated premium member key!
# Key ID: key_a1b2c3d4
# Member Key: pmk_1234567890abcdef1234567890abcdef
# Member ID: customer_001
# Email: customer@example.com
# Valid for: 365 days
```

#### Option B: Using the Simple Bash Script (create_customer_key.sh)

This script provides a simple interface for quick key generation:

```bash
# Usage: ./create_customer_key.sh customer_email customer_name
./create_customer_key.sh john@example.com john_doe

# Output:
# 🔑 Creating premium member key for: john@example.com
# ✅ Key generated! Send the 'member_key' value to your customer.
```

#### Option C: Using the Advanced Bash Script (generate_key.sh)

This script provides more options and flexibility:

```bash
# Basic usage
./generate_key.sh --id customer123 --email customer@example.com

# Advanced usage with custom validity and server URL
./generate_key.sh --id enterprise_customer --email enterprise@example.com \
  --days 30 --server http://your-server:8080

# Output:
# Generating premium member key...
# ✅ Key generated successfully!
# ========== MEMBER KEY ==========
# pmk_1234567890abcdef1234567890abcdef
# ===============================
```

**Script Comparison:**

| Feature | create_customer_key.sh | generate_key.sh |
|---------|------------------------|------------------|
| Interface | Positional arguments | Named parameters with flags |
| Admin token | Hardcoded in script | From environment or parameter |
| Server URL | Hardcoded | Configurable |
| Validity days | Fixed (365) | Configurable |
| Usage limits | Not supported | Supported |
| Help documentation | Basic | Comprehensive |
| Error handling | Basic | Advanced |

### 3. Member Usage (Client Side)

Your paying customers use the key like this:

```json
// ~/.config/mcp/settings.json
{
  "servers": {
    "premium-binance": {
      "command": "python",
      "args": ["-m", "mcp", "client", "stdio"],
      "env": {
        "MCP_SERVER_URL": "wss://your-vps.com:8000",
        "BINANCE_API_KEY": "their_binance_api_key",
        "BINANCE_SECRET_KEY": "their_binance_secret_key", 
        "BINANCE_MCP_MEMBER_KEY": "pmk_1234567890abcdef1234567890abcdef"
      }
    }
  }
}
```

## 🔄 Business Operations

### Daily Operations (No Code Changes!)

```bash
# Add new customer
./add_customer.sh "customer_002" "new@customer.com"

# Check active subscriptions
python -m premium_futures_mcp.key_manager stats

# Revoke expired/cancelled subscription
python -m premium_futures_mcp.key_manager revoke --key-id "key_xyz789"

# Monthly cleanup
python -m premium_futures_mcp.key_manager cleanup
```

### Automated Customer Onboarding

```python
# Your subscription system calls this
import requests

def create_premium_access(customer_email, subscription_days=365):
    response = requests.post("http://localhost:8080/generate-key", 
        headers={"Authorization": "Bearer your-admin-token"},
        json={
            "member_id": f"customer_{int(time.time())}",
            "member_email": customer_email,
            "validity_days": subscription_days,
            "permissions": ["premium_trading", "advanced_analytics"]
        }
    )
    
    key_data = response.json()
    
    # Send welcome email with member key
    send_welcome_email(customer_email, key_data['member_key'])
    
    return key_data['member_key']
```

## 🏢 Revenue Model

### Subscription Tiers
- **Basic**: Free PyPI package (Account Info + Market Data only)
- **Premium**: $29/month (Full premium server access)
- **Enterprise**: $99/month (Higher limits + priority support)

### Key Benefits
- ✅ **No PyPI republishing** for each customer
- ✅ **Real-time key management** without code changes
- ✅ **Scalable architecture** for thousands of customers
- ✅ **Secure key validation** with usage tracking
- ✅ **Revenue protection** with revocable access

## 🔒 Security Features

### Key Storage
- Keys stored as **SHA-256 hashes** (never plaintext)
- **SQLite database** with proper indexing
- **Environment-based** admin authentication
- **Usage tracking** and audit trail

### Access Control
- **Individual key validation** per request
- **Expiration date** enforcement
- **Usage limits** per subscription tier
- **Permission-based** feature access
- **Instant revocation** capability

## 📊 Monitoring & Analytics

```bash
# Real-time statistics
python -m premium_futures_mcp.key_manager stats

# Output:
# 📊 Premium Member Key Statistics
# ────────────────────────────────────────
# Total keys: 150
# Active keys: 142 🟢
# Revoked keys: 5 🔴
# Expired keys: 3 🟡
# Total API usage: 1,245,670
```

## 🔧 Maintenance

### Backup Key Database
```bash
# Daily backup
cp /opt/premium_mcp/keys.db /backup/keys_$(date +%Y%m%d).db

# Restore from backup
cp /backup/keys_20240701.db /opt/premium_mcp/keys.db
```

### Server Updates
```bash
# Update premium server (keys preserved)
git pull origin main
pip install -e . --upgrade
systemctl restart premium-mcp-server
```

## 📈 Scaling Considerations

### High Availability
- **Load balancer** for multiple server instances
- **Shared database** (PostgreSQL/MySQL for production)
- **Redis caching** for key validation
- **Monitoring** with Prometheus/Grafana

### Enterprise Features
- **API rate limiting** per customer
- **Usage analytics** dashboard
- **Customer portal** for key management
- **Webhook notifications** for subscription events
