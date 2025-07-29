import os
from typing import Optional, Dict, List, Annotated, Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from ..helper import groww_login

groww = groww_login()


mcp = FastMCP(
    name="Groww Margin MCP Server",
    instructions=f"A Groww MCP Server for margin calculations and available margin details",
)

# =============================================================================
# MARGIN MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def get_available_margin_details() -> dict:
    """
    Get available margin details for the user account.

    Use this tool when the user asks about:
    - "What's my available margin?"
    - "Show me my margin details"
    - "How much margin do I have?"
    - "Check my available balance"
    - "What's my buying power?"
    - "Show margin breakdown"
    - "Display cash and collateral details"
    """
    response = groww.get_available_margin_details()
    return response


@mcp.tool()
def get_order_margin_details(
    orders: Annotated[
        List[Dict], Field(description="List of order details to calculate margin for")
    ],
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Calculate required margin for a single order or basket of orders.

    Each order in the orders list should contain:
    - trading_symbol: Trading symbol (e.g., 'RELIANCE', 'TCS')
    - transaction_type: 'BUY' or 'SELL'
    - quantity: Number of shares
    - price: Price for limit orders (optional)
    - order_type: 'MARKET' or 'LIMIT'
    - product: 'CNC' or 'MIS'
    - exchange: 'NSE' or 'BSE'

    Use this tool when the user asks about:
    - "How much margin do I need for this order?"
    - "Calculate margin requirement for buying X shares"
    - "What's the margin needed for this trade?"
    - "Check margin for multiple orders"
    - "Show margin calculation for basket orders"
    - "How much money do I need to place this order?"
    """
    response = groww.get_order_margin_details(segment=segment, orders=orders)
    return response


@mcp.tool()
def calculate_single_order_margin(
    trading_symbol: Annotated[
        str,
        Field(description="Trading Symbol of the instrument (e.g., 'RELIANCE', 'TCS')"),
    ],
    quantity: Annotated[int, Field(description="Number of shares to trade")],
    transaction_type: Annotated[
        Literal["BUY", "SELL"], Field(description="Transaction type")
    ] = "BUY",
    price: Annotated[
        Optional[float], Field(description="Price for limit orders")
    ] = None,
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="Order type")
    ] = "MARKET",
    product: Annotated[
        Literal["CNC", "MIS"], Field(description="Product type")
    ] = "CNC",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Calculate margin requirement for a single order with individual parameters.

    Use this tool when the user asks about:
    - "How much margin for buying 10 shares of RELIANCE?"
    - "Calculate margin for selling TCS stock"
    - "What's the margin requirement for this specific trade?"
    - "Check margin needed for one order"
    """
    order_details = [
        {
            "trading_symbol": trading_symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "exchange": exchange,
        }
    ]

    if price is not None:
        order_details[0]["price"] = price

    response = groww.get_order_margin_details(segment=segment, orders=order_details)
    return response


@mcp.tool()
def check_margin_sufficiency(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    quantity: Annotated[int, Field(description="Number of shares to trade")],
    transaction_type: Annotated[
        Literal["BUY", "SELL"], Field(description="Transaction type")
    ] = "BUY",
    price: Annotated[
        Optional[float], Field(description="Price for limit orders")
    ] = None,
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="Order type")
    ] = "MARKET",
    product: Annotated[
        Literal["CNC", "MIS"], Field(description="Product type")
    ] = "CNC",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Check if available margin is sufficient for a proposed order.

    Use this tool when the user asks about:
    - "Can I afford this trade?"
    - "Do I have enough margin for this order?"
    - "Check if I can buy these shares"
    - "Is my balance sufficient for this trade?"
    - "Will this order get rejected due to insufficient margin?"
    """
    # Get available margin
    available_margin = groww.get_available_margin_details()

    # Calculate required margin for the order
    order_details = [
        {
            "trading_symbol": trading_symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type,
            "product": product,
            "exchange": exchange,
        }
    ]

    if price is not None:
        order_details[0]["price"] = price

    required_margin = groww.get_order_margin_details(
        segment=segment, orders=order_details
    )

    # Determine available balance based on segment and product
    if segment == "CASH":
        if product == "CNC":
            available_balance = available_margin.get("equity_margin_details", {}).get(
                "cnc_balance_available", 0
            )
        else:  # MIS
            available_balance = available_margin.get("equity_margin_details", {}).get(
                "mis_balance_available", 0
            )
    else:  # FNO
        if transaction_type == "BUY":
            if "option" in trading_symbol.lower():
                available_balance = available_margin.get("fno_margin_details", {}).get(
                    "option_buy_balance_available", 0
                )
            else:
                available_balance = available_margin.get("fno_margin_details", {}).get(
                    "future_balance_available", 0
                )
        else:  # SELL
            available_balance = available_margin.get("fno_margin_details", {}).get(
                "option_sell_balance_available", 0
            )

    total_required = required_margin.get("total_requirement", 0)
    is_sufficient = available_balance >= total_required

    return {
        "is_sufficient": is_sufficient,
        "available_balance": available_balance,
        "required_margin": total_required,
        "shortfall": max(0, total_required - available_balance),
        "available_margin_details": available_margin,
        "order_margin_details": required_margin,
    }


@mcp.tool()
def get_margin_breakdown_by_segment() -> dict:
    """
    Get a detailed breakdown of margin usage by different segments (Cash vs FnO).

    Use this tool when the user asks about:
    - "Show me margin breakdown by segment"
    - "How is my margin distributed?"
    - "What's my cash vs FnO margin usage?"
    - "Display segment-wise margin details"
    - "Break down my margin allocation"
    """
    margin_details = groww.get_available_margin_details()

    breakdown = {
        "total_margin_summary": {
            "clear_cash": margin_details.get("clear_cash", 0),
            "net_margin_used": margin_details.get("net_margin_used", 0),
            "collateral_available": margin_details.get("collateral_available", 0),
            "collateral_used": margin_details.get("collateral_used", 0),
            "adhoc_margin": margin_details.get("adhoc_margin", 0),
            "brokerage_and_charges": margin_details.get("brokerage_and_charges", 0),
        },
        "equity_segment": margin_details.get("equity_margin_details", {}),
        "fno_segment": margin_details.get("fno_margin_details", {}),
        "raw_response": margin_details,
    }

    return breakdown


@mcp.tool()
def calculate_max_quantity_affordable(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    price: Annotated[float, Field(description="Price per share")],
    transaction_type: Annotated[
        Literal["BUY", "SELL"], Field(description="Transaction type")
    ] = "BUY",
    product: Annotated[
        Literal["CNC", "MIS"], Field(description="Product type")
    ] = "CNC",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Calculate the maximum quantity that can be purchased with available margin.

    Use this tool when the user asks about:
    - "How many shares can I buy with my available margin?"
    - "What's the maximum quantity I can afford?"
    - "How many shares of X can I purchase?"
    - "Calculate max affordable quantity"
    - "What's my buying capacity for this stock?"
    """
    # Get available margin
    available_margin = groww.get_available_margin_details()

    # Determine available balance based on segment and product
    if segment == "CASH":
        if product == "CNC":
            available_balance = available_margin.get("equity_margin_details", {}).get(
                "cnc_balance_available", 0
            )
        else:  # MIS
            available_balance = available_margin.get("equity_margin_details", {}).get(
                "mis_balance_available", 0
            )
    else:  # FNO
        if transaction_type == "BUY":
            available_balance = available_margin.get("fno_margin_details", {}).get(
                "option_buy_balance_available", 0
            )
        else:  # SELL
            available_balance = available_margin.get("fno_margin_details", {}).get(
                "option_sell_balance_available", 0
            )

    # Calculate approximate max quantity (rough estimate based on price)
    # This is a conservative estimate; actual margin requirements may vary
    estimated_max_quantity = int(available_balance / price) if price > 0 else 0

    # Try to get more accurate calculation by testing with estimated quantity
    max_affordable_quantity = 0
    if estimated_max_quantity > 0:
        try:
            # Test with estimated quantity
            test_order = [
                {
                    "trading_symbol": trading_symbol,
                    "transaction_type": transaction_type,
                    "quantity": estimated_max_quantity,
                    "price": price,
                    "order_type": "LIMIT",
                    "product": product,
                    "exchange": exchange,
                }
            ]

            margin_required = groww.get_order_margin_details(
                segment=segment, orders=test_order
            )

            total_required = margin_required.get("total_requirement", 0)

            if total_required <= available_balance:
                max_affordable_quantity = estimated_max_quantity
            else:
                # Binary search for exact quantity (simplified approach)
                max_affordable_quantity = int(
                    (available_balance / total_required) * estimated_max_quantity
                )

        except Exception as e:
            # Fallback to simple calculation
            max_affordable_quantity = estimated_max_quantity

    return {
        "max_affordable_quantity": max_affordable_quantity,
        "available_balance": available_balance,
        "price_per_share": price,
        "estimated_total_cost": max_affordable_quantity * price,
        "trading_symbol": trading_symbol,
        "product": product,
        "segment": segment,
    }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)
