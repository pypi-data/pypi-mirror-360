from growwapi import GrowwAPI
from dotenv import load_dotenv
from fastmcp import FastMCP
from ..helper import get_symbol_match

mcp = FastMCP(
    name="Groww MCP Server",
    instructions=f"A Groww MCP Server for order action and portfoilio analysis",
)


@mcp.tool()
def search_stock_symbol_by_company_name(company_name: str) -> list[dict]:
    '''
    🔍 Search for stock trading symbols by company name.

    This tool helps you find the correct trading symbol for a company when you 
    only know the company name. Essential for accurate order placement.

    Use this tool when you need to:
    - "Find symbol for Reliance Industries"
    - "What's the trading symbol for TCS?"
    - "Search for Infosys stock symbol"
    - "Get ticker for a company"
    - "Look up stock symbol"

    Args:
        company_name: Name of the company to search for (e.g., "Reliance", "Tata Consultancy")

    Returns:
        list[dict]: List of potentially matching ticker symbols and company details.
    '''
    return get_symbol_match(company_name)
