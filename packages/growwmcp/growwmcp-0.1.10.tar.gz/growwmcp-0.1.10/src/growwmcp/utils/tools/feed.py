import os
from typing import Optional, Dict, List, Annotated, Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI, GrowwFeed
from dotenv import load_dotenv
from ..helper import groww_login

groww = groww_login()
feed = GrowwFeed(groww)


mcp = FastMCP(
    name="Groww Feed MCP Server",
    instructions=f"A Groww MCP Server for feed data including market depth, order updates, and position updates",
)

# =============================================================================
# FEED DATA TOOLS
# =============================================================================


@mcp.tool()
def get_market_depth(
    instruments_list: Annotated[
        List[Dict],
        Field(
            description="List of instruments with exchange, segment, and exchange_token. Example: [{'exchange': 'NSE', 'segment': 'CASH', 'exchange_token': '2885'}]"
        ),
    ],
    subscribe_mode: Annotated[
        Literal["sync", "async"],
        Field(
            description="Mode of operation - 'sync' for immediate data retrieval, 'async' for callback-based updates"
        ),
    ] = "sync",
) -> dict:
    """
    Subscribe to and get market depth data for equity and derivatives instruments.
    Market depth shows aggregated buy and sell orders at different price levels.

    Use this tool when the user asks about:
    - "Show me the market depth for stock X"
    - "Get order book for instrument Y"
    - "What are the buy/sell orders for this stock?"
    - "Show me the bid-ask spread"
    - "Get level 2 market data"
    """
    try:
        if subscribe_mode == "sync":
            # Subscribe to market depth
            feed.subscribe_market_depth(instruments_list)

            # Get the market depth data
            market_depth_data = feed.get_market_depth()

            # Unsubscribe after getting data
            feed.unsubscribe_market_depth(instruments_list)

            return {
                "status": "success",
                "data": market_depth_data,
                "message": "Market depth data retrieved successfully",
            }
        else:
            # For async mode, just subscribe and return subscription status
            def on_data_received(meta):
                # print(f"Market depth data received for {meta.exchange}:{meta.segment}")
                return feed.get_market_depth()

            feed.subscribe_market_depth(
                instruments_list, on_data_received=on_data_received
            )

            return {
                "status": "subscribed",
                "message": "Subscribed to market depth updates. Use feed.consume() to start receiving data.",
                "instruments": instruments_list,
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to get market depth: {str(e)}"}


@mcp.tool()
def get_order_updates(
    segment: Annotated[
        Literal["CASH", "FNO"],
        Field(
            description="Market segment - CASH for equity orders, FNO for derivatives orders"
        ),
    ],
    subscribe_mode: Annotated[
        Literal["sync", "async"],
        Field(
            description="Mode of operation - 'sync' for immediate data retrieval, 'async' for callback-based updates"
        ),
    ] = "sync",
) -> dict:
    """
    Subscribe to and get real-time order execution updates for equity or derivatives.
    Provides updates on order status changes, fills, and executions.

    Use this tool when the user asks about:
    - "Show me my order updates"
    - "Get real-time order status"
    - "Track my order executions"
    - "Monitor order fills"
    - "Get live order updates"
    """
    try:
        if subscribe_mode == "sync":
            if segment == "CASH":
                # Subscribe to equity order updates
                feed.subscribe_equity_order_updates()

                # Get the order update data
                order_update_data = feed.get_equity_order_update()

                # Unsubscribe after getting data
                feed.unsubscribe_equity_order_updates()

            elif segment == "FNO":
                # Subscribe to derivatives order updates
                feed.subscribe_fno_order_updates()

                # Get the order update data
                order_update_data = feed.get_fno_order_update()

                # Unsubscribe after getting data
                feed.unsubscribe_fno_order_updates()

            return {
                "status": "success",
                "data": order_update_data,
                "segment": segment,
                "message": f"Order updates for {segment} retrieved successfully",
            }
        else:
            # For async mode, set up callback and subscribe
            def on_data_received(meta):
                if meta.feed_type == "order_update":
                    if segment == "CASH" and meta.segment == groww.SEGMENT_CASH:
                        # print("Equity order update received")
                        return feed.get_equity_order_update()
                    elif segment == "FNO" and meta.segment == groww.SEGMENT_FNO:
                        # print("Derivatives order update received")
                        return feed.get_fno_order_update()

            if segment == "CASH":
                feed.subscribe_equity_order_updates(on_data_received=on_data_received)
            elif segment == "FNO":
                feed.subscribe_fno_order_updates(on_data_received=on_data_received)

            return {
                "status": "subscribed",
                "segment": segment,
                "message": f"Subscribed to {segment} order updates. Use feed.consume() to start receiving data.",
            }

    except Exception as e:
        return {"status": "error", "message": f"Failed to get order updates: {str(e)}"}


@mcp.tool()
def get_position_updates(
    subscribe_mode: Annotated[
        Literal["sync", "async"],
        Field(
            description="Mode of operation - 'sync' for immediate data retrieval, 'async' for callback-based updates"
        ),
    ] = "sync"
) -> dict:
    """
    Subscribe to and get real-time position updates for derivatives trading.
    Provides updates on position changes, including credit/debit quantities and prices.

    Use this tool when the user asks about:
    - "Show me my position updates"
    - "Get real-time position changes"
    - "Track my derivatives positions"
    - "Monitor position modifications"
    - "Get live position updates"
    """
    try:
        if subscribe_mode == "sync":
            # Subscribe to derivatives position updates
            feed.subscribe_fno_position_updates()

            # Get the position update data
            position_update_data = feed.get_fno_position_update()

            # Unsubscribe after getting data
            feed.unsubscribe_fno_position_updates()

            return {
                "status": "success",
                "data": position_update_data,
                "message": "Position updates retrieved successfully",
            }
        else:
            # For async mode, set up callback and subscribe
            def on_data_received(meta):
                if meta.feed_type == "position_update":
                    # print("Position update received")
                    return feed.get_fno_position_update()

            feed.subscribe_fno_position_updates(on_data_received=on_data_received)

            return {
                "status": "subscribed",
                "message": "Subscribed to position updates. Use feed.consume() to start receiving data.",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get position updates: {str(e)}",
        }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)
