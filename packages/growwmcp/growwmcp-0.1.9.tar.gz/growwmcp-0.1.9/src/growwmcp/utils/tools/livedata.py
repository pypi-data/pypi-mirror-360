import os
from typing import Optional, Dict, List, Annotated, Literal, Union, Tuple
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from ..helper import groww_login

groww = groww_login()


mcp = FastMCP(
    name="Groww Live Data MCP Server",
    instructions=f"A Groww MCP Server for fetching live market data including quotes, LTP, and OHLC data",
)

# =============================================================================
# LIVE DATA MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def get_quote(
    trading_symbol: Annotated[
        str,
        Field(
            description="Trading Symbol of the instrument (e.g., 'NIFTY', 'RELIANCE')"
        ),
    ],
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Fetch a real-time quote for an individual instrument.

    Use this tool when the user asks about:
    - "Get quote for RELIANCE"
    - "Show me real-time data for NIFTY"
    - "What's the current quote for TCS?"
    - "Get market depth for this stock"
    - "Show me bid/ask prices"
    - "Get detailed quote information"
    - "What's the current market data?"
    - "Show volume and price details"
    """
    response = groww.get_quote(
        exchange=exchange, segment=segment, trading_symbol=trading_symbol
    )
    return response


@mcp.tool()
def get_ltp(
    exchange_trading_symbols: Annotated[
        List[str],
        Field(
            description="List of trading symbols with exchange (e.g., ['NSE_NIFTY', 'NSE_RELIANCE'])"
        ),
    ],
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Fetch the last traded price for single or multiple instruments.
    Supports up to 50 instruments per call.

    Use this tool when the user asks about:
    - "What's the LTP of RELIANCE?"
    - "Get last traded price for NIFTY"
    - "Show me current prices for multiple stocks"
    - "Get LTP for TCS and INFY"
    - "What are the latest prices?"
    - "Check current trading prices"
    - "Get last price for these instruments"
    - "Show me live prices"
    """
    response = groww.get_ltp(
        segment=segment, exchange_trading_symbols=exchange_trading_symbols
    )
    return response


@mcp.tool()
def get_ohlc(
    exchange_trading_symbols: Annotated[
        List[str],
        Field(
            description="List of trading symbols with exchange (e.g., ['NSE_NIFTY', 'NSE_RELIANCE'])"
        ),
    ],
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get the OHLC (Open, High, Low, Close) details for single or multiple instruments.
    Supports up to 50 instruments per call.

    Use this tool when the user asks about:
    - "Get OHLC data for RELIANCE"
    - "Show me open high low close for NIFTY"
    - "What are today's price ranges?"
    - "Get OHLC for multiple stocks"
    - "Show me daily price summary"
    - "What's the day's trading range?"
    - "Get open close prices"
    - "Show price movements for today"
    """
    response = groww.get_ohlc(
        segment=segment, exchange_trading_symbols=exchange_trading_symbols
    )
    return response


@mcp.tool()
def get_multiple_quotes(
    instruments: Annotated[
        List[Dict], Field(description="List of instrument details to get quotes for")
    ],
) -> dict:
    """
    Get real-time quotes for multiple instruments in a single call.

    Each instrument in the list should contain:
    - exchange: 'NSE' or 'BSE'
    - segment: 'CASH' or 'FNO'
    - trading_symbol: Trading symbol (e.g., 'RELIANCE', 'NIFTY')

    Use this tool when the user asks about:
    - "Get quotes for multiple stocks"
    - "Show me detailed data for these instruments"
    - "Get market depth for multiple symbols"
    - "Compare quotes across instruments"
    - "Show detailed market data for basket of stocks"
    """
    quotes = {}
    for instrument in instruments:
        try:
            exchange = instrument.get("exchange", "NSE")
            segment = instrument.get("segment", "CASH")
            trading_symbol = instrument.get("trading_symbol")

            if trading_symbol:
                quote = groww.get_quote(
                    exchange=exchange, segment=segment, trading_symbol=trading_symbol
                )
                quotes[f"{exchange}_{trading_symbol}"] = quote
        except Exception as e:
            quotes[
                f"{instrument.get('exchange', 'NSE')}_{instrument.get('trading_symbol', 'UNKNOWN')}"
            ] = {"error": str(e)}

    return quotes


@mcp.tool()
def get_market_summary(
    symbols: Annotated[
        List[str],
        Field(
            description="List of exchange_trading_symbols (e.g., ['NSE_NIFTY', 'NSE_RELIANCE'])"
        ),
    ],
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get a comprehensive market summary including LTP and OHLC data for multiple instruments.

    Use this tool when the user asks about:
    - "Give me market summary for these stocks"
    - "Show me complete data for multiple instruments"
    - "Get both LTP and OHLC for these symbols"
    - "Market overview for my watchlist"
    - "Complete market data summary"
    - "Show me comprehensive price data"
    """
    try:
        # Convert list to tuple for the API call
        symbols_tuple = tuple(symbols)

        # Get LTP data
        ltp_data = groww.get_ltp(
            segment=segment, exchange_trading_symbols=symbols_tuple
        )

        # Get OHLC data
        ohlc_data = groww.get_ohlc(
            segment=segment, exchange_trading_symbols=symbols_tuple
        )

        # Combine the data
        summary = {}
        for symbol in symbols:
            summary[symbol] = {
                "ltp": ltp_data.get(symbol, "N/A"),
                "ohlc": ohlc_data.get(symbol, {}),
                "symbol": symbol,
                "segment": segment,
            }

        return {
            "market_summary": summary,
            "total_instruments": len(symbols),
            "segment": segment,
        }

    except Exception as e:
        return {"error": str(e), "symbols": symbols, "segment": segment}


@mcp.tool()
def get_price_comparison(
    symbols: Annotated[
        List[str],
        Field(
            description="List of exchange_trading_symbols to compare (e.g., ['NSE_RELIANCE', 'NSE_TCS'])"
        ),
    ],
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Compare current prices and day changes across multiple instruments.

    Use this tool when the user asks about:
    - "Compare prices of these stocks"
    - "Which stock is performing better today?"
    - "Show me price comparison"
    - "Compare day changes across instruments"
    - "Which one has higher returns today?"
    - "Show relative performance"
    """
    try:
        comparison_data = {}

        # Get detailed quotes for comparison
        for symbol in symbols:
            try:
                # Extract exchange and trading_symbol from the format "NSE_SYMBOL"
                if "_" in symbol:
                    exchange, trading_symbol = symbol.split("_", 1)
                else:
                    exchange = "NSE"
                    trading_symbol = symbol

                quote = groww.get_quote(
                    exchange=exchange, segment=segment, trading_symbol=trading_symbol
                )

                comparison_data[symbol] = {
                    "last_price": quote.get("last_price", 0),
                    "day_change": quote.get("day_change", 0),
                    "day_change_perc": quote.get("day_change_perc", 0),
                    "volume": quote.get("volume", 0),
                    "ohlc": quote.get("ohlc", {}),
                    "market_cap": quote.get("market_cap", 0),
                }

            except Exception as e:
                comparison_data[symbol] = {"error": str(e)}

        # Find best and worst performers
        valid_data = {k: v for k, v in comparison_data.items() if "error" not in v}

        best_performer = None
        worst_performer = None

        if valid_data:
            best_performer = max(
                valid_data.items(), key=lambda x: x[1].get("day_change_perc", 0)
            )
            worst_performer = min(
                valid_data.items(), key=lambda x: x[1].get("day_change_perc", 0)
            )

        return {
            "comparison_data": comparison_data,
            "best_performer": best_performer,
            "worst_performer": worst_performer,
            "total_symbols": len(symbols),
            "segment": segment,
        }

    except Exception as e:
        return {"error": str(e), "symbols": symbols, "segment": segment}


@mcp.tool()
def get_market_depth_analysis(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get detailed market depth analysis including bid-ask spread and order book data.

    Use this tool when the user asks about:
    - "Show me market depth for this stock"
    - "What's the bid-ask spread?"
    - "Get order book data"
    - "Show me buy and sell orders"
    - "Market depth analysis"
    - "Order book information"
    """
    try:
        quote = groww.get_quote(
            exchange=exchange, segment=segment, trading_symbol=trading_symbol
        )

        # Extract market depth information
        depth = quote.get("depth", {})
        bid_price = quote.get("bid_price", 0)
        offer_price = quote.get("offer_price", 0)
        bid_quantity = quote.get("bid_quantity", 0)
        offer_quantity = quote.get("offer_quantity", 0)

        # Calculate spread
        spread = offer_price - bid_price if (offer_price and bid_price) else 0
        spread_percentage = (spread / bid_price * 100) if bid_price > 0 else 0

        analysis = {
            "symbol": f"{exchange}_{trading_symbol}",
            "bid_ask_spread": {
                "bid_price": bid_price,
                "ask_price": offer_price,
                "spread": spread,
                "spread_percentage": round(spread_percentage, 4),
            },
            "quantities": {
                "bid_quantity": bid_quantity,
                "ask_quantity": offer_quantity,
                "total_buy_quantity": quote.get("total_buy_quantity", 0),
                "total_sell_quantity": quote.get("total_sell_quantity", 0),
            },
            "order_book": depth,
            "market_indicators": {
                "last_price": quote.get("last_price", 0),
                "volume": quote.get("volume", 0),
                "last_trade_quantity": quote.get("last_trade_quantity", 0),
                "last_trade_time": quote.get("last_trade_time", 0),
            },
        }

        return analysis

    except Exception as e:
        return {
            "error": str(e),
            "symbol": f"{exchange}_{trading_symbol}",
            "segment": segment,
        }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)
