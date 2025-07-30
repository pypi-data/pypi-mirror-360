# Complete Beginner's Guide: Binance Futures MCP Server for VSCode on Windows

This guide will walk you through setting up and using the Binance Futures MCP (Model Context Protocol) server with GitHub Copilot in VSCode on Windows. **No prior experience required!**

## 📋 What You'll Need

- Windows 10/11 computer
- VSCode (Visual Studio Code)
- GitHub Copilot subscription
- Binance Futures account with API access
- About 30-45 minutes

## 🎯 What This Tool Does

This MCP server gives GitHub Copilot the ability to:
- Get your Binance Futures account balance and positions
- Fetch real-time market data (prices, volume, top gainers/losers)
- Place and manage futures trading orders
- Analyze market sentiment and trading statistics
- All directly within VSCode!

## 📦 Step 1: Install Python

1. **Download Python:**
   - Go to [python.org/downloads](https://python.org/downloads/)
   - Click "Download Python 3.11.x" (or latest version)

2. **Install Python:**
   - Run the downloaded installer
   - **IMPORTANT:** Check "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation:**
   - Press `Win + R`, type `cmd`, press Enter
   - Type: `python --version`
   - You should see something like "Python 3.11.x"

## 🔧 Step 2: Download and Setup the MCP Server

1. **Download the Server:**
   - Download this entire folder to your computer
   - Place it somewhere easy to find like `C:\binance-mcp\`

2. **Open Command Prompt:**
   - Press `Win + R`, type `cmd`, press Enter
   - Navigate to your folder: `cd C:\binance-mcp\` (adjust path as needed)

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Wait for all packages to install.

## 🔑 Step 3: Get Your Binance API Keys

**⚠️ SECURITY WARNING: Your API keys are like passwords to your trading account. Keep them secret!**

1. **Login to Binance:**
   - Go to [binance.com](https://binance.com)
   - Log into your account

2. **Create API Key:**
   - Go to Account → API Management
   - Click "Create API" 
   - Choose "System Generated"
   - Complete 2FA verification
   - **IMPORTANT:** For trading permissions:
     - ✅ Enable Reading
     - ✅ Enable Futures Trading
     - ❌ Leave "Enable Withdrawals" DISABLED for security

3. **Save Your Keys:**
   - Copy both the "API Key" and "Secret Key"
   - Store them temporarily in Notepad (we'll use them next)

## ⚙️ Step 4: Configure the Server

1. **Create Config File:**
   - In your `C:\binance-mcp\` folder, create a file named `config.py`
   - Copy this content into it:

```python
# Binance API Configuration
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Optional: Set to True for testnet (paper trading)
USE_TESTNET = False

# Cache settings (default values work fine)
CACHE_DURATION = 60  # seconds
```

2. **Add Your Keys:**
   - Replace `"your_api_key_here"` with your actual API key
   - Replace `"your_secret_key_here"` with your actual secret key
   - Save the file

3. **Test Your Setup:**
   ```bash
   python -m premium_futures_mcp.server
   ```
   If you see "Server starting..." without errors, you're good to go!
   Press `Ctrl+C` to stop the server.

## 📂 Step 5: Setup VSCode and MCP

1. **Install VSCode Extensions:**
   - Open VSCode
   - Go to Extensions (Ctrl+Shift+X)
   - Install "GitHub Copilot" and "GitHub Copilot Chat"

2. **Create MCP Configuration:**
   - Press `Ctrl+Shift+P` to open command palette
   - Type "Preferences: Open User Settings (JSON)"
   - Add this configuration:

```json
{
  "github.copilot.chat.mcp.servers": {
    "binance-futures": {
      "command": "python",
      "args": ["-m", "premium_futures_mcp.server"],
      "cwd": "C:\\binance-mcp"
    }
  }
}
```

**Important:** Change `"C:\\binance-mcp"` to your actual folder path (use double backslashes).

3. **Restart VSCode** to apply the configuration.

## 🚀 Step 6: First Test

1. **Open Copilot Chat:**
   - Press `Ctrl+Shift+P`
   - Type "GitHub Copilot: Open Chat"

2. **Test Basic Commands:**
   ```
   What's my Binance futures account balance?
   ```

   ```
   Show me the top 5 gainers in the futures market today
   ```

   ```
   What's the current market overview?
   ```

If these work, congratulations! Your setup is complete! 🎉

## 💡 Example Use Cases

### Getting Market Information
```
Show me top 10 gainers and losers with minimum $1M volume
```

```
What's the current price and 24h change for BTCUSDT?
```

```
Give me a market overview with top movers
```

### Account Management
```
What positions do I currently have open?
```

```
Show me my account balance and available margin
```

```
What are my recent trades for ETHUSDT?
```

### Trading (Be Careful!)
```
Place a small long position on BTCUSDT with stop loss and take profit
```

```
What open orders do I have for ADAUSDT?
```

## 🔧 Troubleshooting Common Issues

### "Permission denied" or "API key invalid"
- Double-check your API keys in `config.py`
- Ensure Futures trading is enabled on your API key
- Try regenerating your API keys

### "Module not found" errors
- Make sure you installed requirements: `pip install -r requirements.txt`
- Check that you're in the correct directory

### "Connection timeout" or network errors
- Check your internet connection
- Some corporate networks block trading APIs
- Try using a VPN if needed

### VSCode doesn't recognize the MCP server
- Verify the path in your VSCode settings is correct
- Restart VSCode completely
- Check that the server starts manually: `python -m premium_futures_mcp.server`

## ⚠️ Important Safety Tips

1. **Start Small:** Begin with tiny position sizes to test everything works
2. **Use Stop Losses:** Always set stop losses to limit potential losses
3. **Test First:** Consider using Binance Testnet first (set `USE_TESTNET = True`)
4. **Keep Keys Secret:** Never share your API keys with anyone
5. **Monitor Positions:** Don't rely solely on automation - always monitor your trades

## 🎓 Next Steps

Once you're comfortable with basic usage:
- Explore more advanced trading strategies
- Set up automated alerts
- Use the sentiment analysis tools
- Integrate with your existing trading workflow

## 📞 Getting Help

If you run into issues:
1. Check the error messages carefully
2. Review this guide step by step
3. Make sure all requirements are met
4. Test each component individually

## 🏁 Conclusion

You now have a powerful trading assistant integrated directly into VSCode! GitHub Copilot can help you:
- Monitor markets in real-time
- Execute trades with natural language
- Analyze your portfolio performance
- Make informed trading decisions

**Remember:** This tool gives you great power, but with great power comes great responsibility. Always trade responsibly and never risk more than you can afford to lose.

Happy trading! 📈
