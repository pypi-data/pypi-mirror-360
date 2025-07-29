from growwapi import GrowwAPI
from dotenv import load_dotenv
import os
from fastmcp.prompts.prompt import Message
from typing import Annotated, Literal
from pydantic import Field
from fastmcp import FastMCP
import pandas as pd
import requests
from ..helper import get_symbol_match
from ..helper import groww_login

groww = groww_login()

mcp = FastMCP(
    name="Groww MCP Server",
    instructions=f"A Groww MCP Server for order action and portfoilio analysis",
)


@mcp.tool()
def get_my_portfolio_holdings(
    timeout: Annotated[int, Field(description="Timeout for the API call")] = 5
) -> dict:
    """
    📊 Get your complete portfolio holdings with current valuations.

    This tool provides comprehensive information about all stocks you currently own,
    including quantity, average price, current market value, and P&L.

    Use this tool when you need:
    - "Show my portfolio"
    - "What stocks do I own?"
    - "My current holdings"
    - "Portfolio summary"
    - "Holdings with profit/loss"

    Returns:
        dict: Complete portfolio holdings with current market valuations.
    """
    return groww.get_holdings_for_user(timeout=timeout)


@mcp.tool()
def get_my_trading_positions() -> dict:
    """
    📈 Get your current trading positions (intraday & derivatives).

    This tool shows all your active trading positions including:
    - Intraday positions (MIS)
    - Derivatives positions (FnO)
    - Open P&L and realized P&L
    - Position quantities and values

    Use this tool when you need:
    - "Show my positions"
    - "What are my active trades?"
    - "My current positions"
    - "Trading P&L"
    - "Intraday positions"

    Returns:
        dict: All active trading positions with P&L details.
    """
    return groww.get_positions_for_user()


@mcp.tool()
def get_specific_stock_position(
    trading_symbol: Annotated[
        str, Field(description="Trading symbol of the stock (e.g., 'RELIANCE', 'TCS')")
    ],
    segment: Annotated[
        Literal["CASH", "FNO"],
        Field(description="Market segment - CASH for equity, FNO for derivatives"),
    ] = "CASH",
) -> dict:
    """
    🎯 Get position details for a specific stock or derivative.

    This tool provides detailed position information for a particular trading symbol,
    including quantity held, average price, current value, and P&L breakdown.

    Use this tool when you need:
    - "Show my RELIANCE position"
    - "What's my position in TCS?"
    - "Check my NIFTY futures position"
    - "Position details for specific stock"

    Returns:
        dict: Detailed position information for the specified trading symbol.
    """
    return groww.get_position_for_trading_symbol(trading_symbol, segment)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode on port 8892"
    )
    parser.add_argument("--stdio", action="store_true", help="Run with stdio transport")
    args = parser.parse_args()
    if args.stdio:
        mcp.run(transport="stdio")
    elif args.test:
        mcp.run(transport="sse", host="0.0.0.0", port=8892)
    else:
        mcp.run(transport="sse", host="0.0.0.0", port=8891)
