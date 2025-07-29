### GROWWMCP

GrowwMCP is a powerful tool that integrates your personal Groww account with an intelligent, chat-based interface. It allows you to perform deep market analysis, manage your portfolio holdings, and execute complex trading strategies using simple conversational commands. This turns your trading platform into an interactive financial assistant.

### **How to Set Up GrowwMCP with Claude Desktop**

This guide will help you connect your GrowwMCP to Claude Desktop, allowing you to analyse your portfolio, placing orders, analyse market and lot more using simple chat commands.

---

#### **Step 1: Install Prerequisite Software**

To get started, please install the following applications on your computer.

1.  **Python 3.10:** [! Required, it is mandatory to use python 3.10, the package isn't supported by python version <= 3.9]
    *   Install Python by following the official guide at this URL:
    *   [https://www.python.org/downloads/release/python-31018/](https://www.python.org/downloads/release/python-31018/)

2.  **uv (A Python Package Installer):**
    *   Use the official documentation at the following link to install `uv`:
    *   [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

> **Important For Mac Users:** Mac users should install Python and uv using the command below. (If you do not have administrative privileges, please contact your IT Administrator). Do not try `pip install uv` to avoid unexpected behavior


```zsh
brew install uv
brew install python@3.10
```

3. **Install the Claude Desktop Application**
    *   Obtain the installer for your specific operating system from https://claude.ai/download and execute it. (Administrator permissions are necessary).
    [On macOS, this will download as a .dmg file. Double-click it to launch the installer.]

> **Important:** It is recommended to use administrator/root privileges when installing the above tools. This will help ensure that Claude can locate and utilize them correctly.

---


#### **Step 2: Get Your Groww API Credentials**

To connect Claude to your Groww account, you need special keys. You must first have access to the Groww API.

1.  Visit the Groww API documentation to get your **API Key**, **API Secret**, and set up your **TOTP secret**.
    *   [https://groww.in/trade-api/docs/python-sdk#2nd-approach-totp-flow](https://groww.in/trade-api/docs/python-sdk#2nd-approach-totp-flow)
2.  Keep these keys safe and ready for the next step.

---

#### **Step 3: Configure Claude Desktop**

Now, you will tell Claude Desktop how to run the Groww tool.

1.  Open your Claude Desktop configuration file.
    *   For help finding this file, see the official guide here (you do not need to install Node.js): [https://modelcontextprotocol.io/quickstart/user](https://modelcontextprotocol.io/quickstart/user)

2.  In the configuration file, find the `mcpServers` section and add the following code inside it:

    ```json
    {
        "mcpServers": {
            "growwmcp": {
                "command": "uv",
                "args": [
                "run",
                "--python",
                "3.10",
                 "--reinstall",
                "--with",
                "growwmcp",
                "python",
                "-m",
                "growwmcp",
                "--stdio"
                ],
                "env": {
                    "GROWW_API_KEY": "<your api key here>",
                    "GROWW_API_SECRET": "<your api secret here>"
                }
            }
        }
    }
    ```

3.  Replace `<your api key here>` and `<your api secret here>` with the actual keys you got from Groww in Step 2.

4.  Save and close the configuration file.

---

#### **Attach system prompt**

You can help Claude understand how to use the Groww tool more effectively by adding a system prompt.

1.  In the Claude Desktop chat interface, click the **`+`** button.
2.  Find the `growwmcp` section and click **"Add"** next to `prompt_template_prompt`.

![Image showing how to add the system prompt in Claude Desktop](assets/claude_sys_prompt.png)

This will give Claude better instructions, leading to more accurate results. You are all set.

---

#### **Step 4: Verify the Setup**

1.  Restart your Claude Desktop application.
2.  Check the "Search & Tools" section in Claude. You should see **growwmcp** listed as an available tool.
    *   *Note: It may take 10-30 seconds for the tool to appear the first time while it sets up.*

    ![Image showing 'growwmcp' in the Claude Desktop tool list](assets/claude_groww_mcp.png)

---

#### **Step 5: Start Using the Groww Tool**

Once confirmed, you can start chatting with Claude to manage your portfolio. Try commands like but not limited to:

*   `Place a stoploss order for 5 units of X stock at Y price`
*   `Find next Thursday's NIFTY 25000 PE contract`
*   `What is my current portfolio value?`
*   `Build a wide iron condor for july 1 on NIFTY, plot the payoff graph for that`
*   `I am bullish on X stock for the upcoming month. Find the next monthly expiry for X options. I want to buy a call option. Please select the strike price that is closest to, but just above, the current market price of X. Prepare an order to buy 1 lot of this specific option.` 
*   `When Nifty opens with a gap of over 1%, what does the first 15-minute candle typically look like — in terms of range and direction? (Mean, Median, 95th percentile data to be presented)`

---

### **Security/Vulnerability**

> This package is supposed be run by a mcp supported tool (i.e. claude desktop) so ensure you trust claude desktop with your data, and keep your `<your api key here>` and `<your api secret here>` safe.
> **Disclaimer:** The strategies and analysis presented by the AI assistant are generated by AI. They do not represent any financial advice or official recommendations from Groww. 


### **Tool Documentation**

| Category | Tool Name & Icon | Description | Primary Use Case / Triggers | Confirmation Required? |
| :--- | :--- | :--- | :--- | :--- |
| **Portfolio Management** | `portfolio_get_my_portfolio_holdings` 📊 | Retrieves a user's complete stock holdings, including valuations and P&L. | "Show my portfolio," "What stocks do I own?" | No |
| | `portfolio_get_my_trading_positions` 📈 | Fetches current intraday (MIS) and derivative (F&O) trading positions. | "Show my positions," "My active trades." | No |
| | `portfolio_get_specific_stock_position` 🎯 | Provides detailed position information for a single trading symbol. | "Show my RELIANCE position," "Check my NIFTY futures." | No |
| **Order Management** | `orders_place_order_with_confirmation` ⚠️ | Places a new stock or F&O order after a strict, mandatory user confirmation. | "Buy X shares," "Place a limit order." | **Yes** (`CONFIRM_ORDER`) |
| | `orders_smart_order_placement` | Intelligently places equity or F&O orders by auto-detecting the type. | "Buy 2 lots of NIFTY call," "Sell Bank Nifty futures." | **Yes** (via confirmation) |
| | `orders_modify_order_with_confirmation` ⚠️ | Modifies a pending order's parameters after mandatory user confirmation. | "Change the quantity," "Update my limit price." | **Yes** (`CONFIRM_MODIFY`) |
| | `orders_cancel_order_with_confirmation` ⚠️ | Cancels a pending order after mandatory user confirmation. | "Cancel my pending order," "Stop my order." | **Yes** (`CONFIRM_CANCEL`) |
| | `orders_get_order_status` | Retrieves the current status (e.g., pending, executed) of a specific order. | "What's the status of my order?" | No |
| | `orders_get_order_history` | Fetches a list of all past orders for a specific market segment. | "Show my order history," "List all my trades." | No |
| | `orders_get_trade_list_for_order` | Lists all trade executions (fills) for a single order. | "Show all executions for my order." | No |
| | `orders_get_order_details` | Provides comprehensive information for a single specified order. | "Show me complete order details." | No |
| **Instrument & Symbol** | `utils_search_stock_symbol_by_company_name` 🔍 | Finds a stock's trading symbol using the company name. | "Find symbol for Reliance," "What's the ticker for TCS?" | No |
| | `instruments_get_instrument_by_*` | Gets detailed instrument data using a Groww symbol, exchange symbol, or token. | "Get details of NSE-RELIANCE," "Look up stock details." | No |
| | `instruments_search_instruments_by_name` | Searches for instruments using a partial name or keyword. | "Find stocks containing 'Reliance'." | No |
| | `instruments_get_available_option_expiries` | Lists all available expiry dates for a given option's underlying symbol. | "What are the NIFTY option expiries?" | No |
| | `instruments_get_available_option_strikes` | Lists all available strike prices for a given option and expiry. | "Show me strike prices for RELIANCE calls." | No |
| | `instruments_build_option_symbol` | Constructs and validates a correct F&O option symbol. | "Build symbol for NIFTY 24000 CE." | No |
| | `instruments_build_future_symbol` | Constructs and validates a correct F&O future symbol. | "Build future symbol for NIFTY expiring soon." | No |
| | `instruments_smart_fno_order_assistant` | Guides users to place correct F&O orders by asking clarifying questions. | "I want to buy a NIFTY call option." | No |
| | `instruments_place_fno_order` | A dedicated tool to place a validated F&O order. | "Place order for NIFTY call option." | **Yes** (via confirmation) |
| **Margin & Funds** | `margins_get_available_margin_details` | Shows the user's total available margin (buying power). | "What's my available margin?" | No |
| | `margins_get_order_margin_details` | Calculates the margin required for a single or basket of orders. | "How much margin do I need for this trade?" | No |
| | `margins_check_margin_sufficiency` | Checks if the user has enough margin to place a proposed order. | "Can I afford this trade?" | No |
| | `margins_calculate_max_quantity_affordable` | Calculates the maximum quantity of a stock a user can buy with their margin. | "How many shares of X can I buy?" | No |
| **Live Market Data** | `livedata_get_quote` | Fetches a full real-time quote (market depth, bid/ask) for one instrument. | "Get quote for RELIANCE." | No |
| | `livedata_get_ltp` | Fetches only the Last Traded Price (LTP) for up to 50 instruments. | "What's the LTP of RELIANCE and TCS?" | No |
| | `livedata_get_ohlc` | Fetches the Open, High, Low, Close (OHLC) data for up to 50 instruments. | "Get today's OHLC for NIFTY." | No |
| **Historical Data** | `historicaldata_get_historical_candle_data` | Fetches historical candle data for a custom time range and interval. | "Get 5-minute candles for NIFTY last week." | No |
| | `historicaldata_get_daily_historical_data` | Fetches daily historical data for a specified number of past days. | "Get last 30 days of data for RELIANCE." | No |
| **Real-time Data Feeds**| `feed_get_market_depth` | Subscribes to live market depth (Level 2) data for an instrument. | "Show me the live order book for stock X." | No |
| | `feed_get_order_updates` | Subscribes to real-time updates for the user's own order executions. | "Track my order executions in real-time." | No |
| | `feed_get_position_updates` | Subscribes to real-time updates for the user's F&O position changes. | "Get live updates on my derivatives positions." | No |
| **Pattern Detection Data**| `pattern_get_historical_candlestick_patterns` | Gives list of detected patterns from candles of historical data | "Do you see any patterns in this week candles?" | No
