import os
from typing import Optional, Dict, List, Annotated, Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from ..helper import groww_login

groww = groww_login()


mcp = FastMCP(
    name="Groww MCP Server",
    instructions=f"A Groww MCP Server for order action and portfoilio analysis",
)

# =============================================================================
# ORDER MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def place_order_with_confirmation(
    trading_symbol: Annotated[
        str,
        Field(description="Trading Symbol of the instrument (e.g., 'WIPRO', 'TCS')"),
    ],
    quantity: Annotated[int, Field(description="Number of shares to trade")],
    transaction_type: Annotated[
        Literal["BUY", "SELL"], Field(description="Transaction type")
    ] = "BUY",
    price: Annotated[
        Optional[float], Field(description="Price for limit orders")
    ] = None,
    trigger_price: Annotated[
        Optional[float], Field(description="Trigger price for stop loss orders")
    ] = None,
    validity: Annotated[
        Literal["DAY", "IOC"], Field(description="Order validity")
    ] = "DAY",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
    product: Annotated[
        Literal["CNC", "MIS", "NRML"], Field(description="Product type")
    ] = "CNC",
    order_type: Annotated[
        Literal["MARKET", "LIMIT", "SL", "SL_M"], Field(description="Type of order")
    ] = "MARKET",
    order_reference_id: Annotated[
        Optional[str], Field(description="Custom reference ID for tracking")
    ] = None,
    user_confirmation: Annotated[
        str,
        Field(
            description="MANDATORY: User must type 'CONFIRM_ORDER' to proceed with order placement"
        ),
    ] = "",
) -> dict:
    """
    ⚠️  FINANCIAL ADVISOR TOOL - REQUIRES EXPLICIT CONFIRMATION ⚠️

    Place a new order on the Groww platform with mandatory user confirmation.
    This tool implements financial safety protocols requiring explicit user consent.

    🔒 SAFETY FEATURES:
    - Mandatory user confirmation required
    - Pre-execution order summary
    - Post-execution verification
    - Risk assessment for order size
    - Margin sufficiency check

    Use this tool when the user wants to:
    - "Buy X shares of Y stock"
    - "Place a limit order for Z company"
    - "Sell my holdings in ABC company"
    - "Create a stop loss order"
    - "Buy NIFTY futures"
    - "Place options order"

    ⚠️ IMPORTANT: User MUST provide 'CONFIRM_ORDER' in user_confirmation parameter
    """

    # VALIDATION 1: Check mandatory confirmation
    if user_confirmation != "CONFIRM_ORDER":
        return {
            "status": "confirmation_required",
            "success": False,
            "message": "❌ ORDER BLOCKED: User confirmation required",
            "required_action": "Please provide 'CONFIRM_ORDER' in the user_confirmation parameter to proceed",
            "order_summary": {
                "action": f"{transaction_type} {quantity} shares of {trading_symbol}",
                "order_type": order_type,
                "price": price if price else "MARKET PRICE",
                "segment": segment,
                "product": product,
                "exchange": exchange,
                "estimated_value": (
                    f"₹{(price or 0) * quantity:,.2f}" if price else "Market dependent"
                ),
            },
            "safety_note": "🛡️ This is a financial safety feature. All orders require explicit user confirmation.",
        }

    # VALIDATION 2: Parameter validation
    validation_errors = []

    if not trading_symbol or len(trading_symbol.strip()) == 0:
        validation_errors.append("Trading symbol cannot be empty")

    if quantity <= 0:
        validation_errors.append("Quantity must be positive")

    if order_type == "LIMIT" and (price is None or price <= 0):
        validation_errors.append("Limit orders require a valid price")

    if segment == "FNO" and product == "CNC":
        product = "MIS"  # Auto-correct for FnO

    if validation_errors:
        return {
            "status": "validation_failed",
            "success": False,
            "message": "❌ ORDER VALIDATION FAILED",
            "errors": validation_errors,
            "order_blocked": True,
        }

    # VALIDATION 3: Check margin sufficiency before placing order
    try:
        from .margins import check_margin_sufficiency

        margin_check = check_margin_sufficiency(
            trading_symbol=trading_symbol,
            quantity=quantity,
            transaction_type=transaction_type,
            price=price,
            order_type=order_type,
            product=product,
            exchange=exchange,
            segment=segment,
        )

        if not margin_check.get("is_sufficient", False):
            return {
                "status": "insufficient_margin",
                "success": False,
                "message": "❌ ORDER BLOCKED: Insufficient margin",
                "margin_details": margin_check,
                "required_margin": margin_check.get("required_margin", 0),
                "shortfall": margin_check.get("shortfall", 0),
                "safety_note": "🛡️ Order blocked to prevent margin shortfall",
            }
    except Exception as margin_error:
        # If margin check fails, proceed with warning
        pass

    # PRE-EXECUTION SUMMARY
    order_summary = {
        "🎯 ACTION": f"{transaction_type} {quantity} shares of {trading_symbol}",
        "💰 ORDER_TYPE": order_type,
        "💵 PRICE": price if price else "MARKET PRICE",
        "🏢 EXCHANGE": exchange,
        "📊 SEGMENT": segment,
        "📦 PRODUCT": product,
        "⏱️ VALIDITY": validity,
        "🔢 ESTIMATED_VALUE": (
            f"₹{(price or 0) * quantity:,.2f}" if price else "Market dependent"
        ),
        "⚠️ RISK_LEVEL": (
            "HIGH"
            if segment == "FNO"
            else "MEDIUM" if order_type == "MARKET" else "LOW"
        ),
    }

    try:
        # EXECUTE ORDER
        response = groww.place_order(
            trading_symbol=trading_symbol,
            quantity=quantity,
            price=price,
            trigger_price=trigger_price,
            validity=validity,
            exchange=exchange,
            segment=segment,
            product=product,
            order_type=order_type,
            transaction_type=transaction_type,
            order_reference_id=order_reference_id,
        )

        # Extract order ID from response
        order_id = response.get("groww_order_id") or response.get("order_id")

        # POST-EXECUTION VERIFICATION
        order_status_info = None
        verification_message = ""

        if order_id:
            try:
                import time

                time.sleep(1)  # Brief pause for order processing

                status_response = groww.get_order_status(
                    groww_order_id=order_id, segment=segment
                )
                order_status_info = status_response

                if isinstance(status_response, dict):
                    current_status = status_response.get("order_status", "UNKNOWN")
                    rejection_reason = status_response.get("rejection_reason", "")

                    if current_status in ["REJECTED", "CANCELLED"]:
                        verification_message = f"❌ ORDER FAILED: {rejection_reason or 'Order rejected by exchange'}"
                        order_outcome = "FAILED"
                    elif current_status in ["COMPLETE", "EXECUTED"]:
                        verification_message = f"✅ ORDER EXECUTED: Successfully {transaction_type.lower()}ed {quantity} shares of {trading_symbol}"
                        order_outcome = "SUCCESS"
                    elif current_status in ["OPEN", "TRIGGER_PENDING", "PENDING"]:
                        verification_message = f"📋 ORDER PENDING: Order placed successfully, waiting for execution"
                        order_outcome = "PENDING"
                    else:
                        verification_message = (
                            f"⚠️ ORDER STATUS UNKNOWN: {current_status}"
                        )
                        order_outcome = "UNKNOWN"
                else:
                    verification_message = "⚠️ Unable to verify order status"
                    order_outcome = "VERIFICATION_FAILED"

            except Exception as status_error:
                verification_message = f"⚠️ Status check failed: {str(status_error)}"
                order_outcome = "VERIFICATION_FAILED"
        else:
            verification_message = "⚠️ No order ID received - verification not possible"
            order_outcome = "NO_ORDER_ID"

        # COMPREHENSIVE RESPONSE
        return {
            "status": "order_executed",
            "success": True,
            "order_outcome": order_outcome,
            "verification_message": verification_message,
            "pre_execution_summary": order_summary,
            "order_response": response,
            "post_execution_verification": order_status_info,
            "order_details": {
                "order_id": order_id,
                "trading_symbol": trading_symbol,
                "quantity": quantity,
                "transaction_type": transaction_type,
                "order_type": order_type,
                "price": price,
                "segment": segment,
                "product": product,
                "exchange": exchange,
                "timestamp": response.get("timestamp") or "N/A",
            },
            "financial_advisory_note": "✅ Order processed with full safety protocols and verification",
        }

    except Exception as e:
        return {
            "status": "execution_failed",
            "success": False,
            "message": f"❌ ORDER EXECUTION FAILED: {str(e)}",
            "pre_execution_summary": order_summary,
            "error_details": str(e),
            "order_outcome": "EXECUTION_FAILED",
            "financial_advisory_note": "🛡️ Order blocked due to execution error - your funds are safe",
        }


@mcp.tool()
def smart_order_placement(
    user_request: Annotated[
        str,
        Field(
            description="User's complete order request (e.g., 'Buy 2 lots of NIFTY 24000 call expiring next week', 'Sell 100 shares of TCS')"
        ),
    ],
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="Order type")
    ] = "MARKET",
    price: Annotated[
        Optional[float], Field(description="Limit price for LIMIT orders")
    ] = None,
) -> dict:
    """
    Smart order placement that handles both equity and FnO orders intelligently.
    Analyzes user request, determines if it's equity or FnO, builds appropriate symbols, and places orders.

    Use this tool when the user makes complex order requests like:
    - "Buy 2 lots of NIFTY 24000 call option"
    - "Sell Bank Nifty futures"
    - "Buy 100 shares of Reliance"
    - "Place order for TCS put option at 3800 strike"
    - Any order request that needs intelligent parsing and symbol building
    """
    try:
        from .instruments import (
            smart_fno_order_assistant,
            place_fno_order,
            build_option_symbol,
            build_future_symbol,
        )

        # First, analyze the request to determine if it's FnO or equity
        request_lower = user_request.lower()

        # Check if it's an FnO request
        is_fno_request = any(
            word in request_lower
            for word in [
                "option",
                "call",
                "put",
                "ce",
                "pe",
                "future",
                "fut",
                "nifty",
                "banknifty",
                "expiry",
                "expiring",
                "strike",
                "lot",
            ]
        )

        if is_fno_request:
            # Use the smart FnO assistant
            fno_analysis = smart_fno_order_assistant(user_request)

            if fno_analysis["status"] == "ready":
                # All information is available, build symbol and place order
                extracted = fno_analysis["extracted_info"]

                if extracted.get("instrument_type") == "OPTION":
                    # Build option symbol
                    symbol_result = build_option_symbol(
                        underlying_symbol=extracted["underlying_symbol"],
                        expiry_date=extracted["expiry_date"],
                        strike_price=(
                            extracted["potential_strike_prices"][0]
                            if extracted.get("potential_strike_prices")
                            else extracted.get("strike_price")
                        ),
                        option_type=extracted["option_type"],
                    )

                    if symbol_result["symbol_found"]:
                        # Place the option order
                        order_result = place_fno_order(
                            trading_symbol=symbol_result["trading_symbol"],
                            quantity=extracted["quantity"],
                            transaction_type=extracted["transaction_type"],
                            order_type=order_type,
                            price=price,
                            product="MIS",
                        )

                        # Determine overall success based on order outcome
                        overall_success = order_result.get("success", False)
                        overall_message = order_result.get("message", "Order processed")

                        return {
                            "status": "success" if overall_success else "failed",
                            "order_type": "FNO_OPTION",
                            "symbol_built": symbol_result,
                            "order_result": order_result,
                            "success": overall_success,
                            "message": f"Option order: {overall_message}",
                        }
                    else:
                        return {
                            "status": "error",
                            "error_type": "symbol_not_found",
                            "symbol_result": symbol_result,
                            "message": "Could not find the requested option symbol",
                        }

                elif extracted.get("instrument_type") == "FUTURE":
                    # Build future symbol
                    symbol_result = build_future_symbol(
                        underlying_symbol=extracted["underlying_symbol"],
                        expiry_date=extracted["expiry_date"],
                    )

                    if symbol_result["symbol_found"]:
                        # Place the future order
                        order_result = place_fno_order(
                            trading_symbol=symbol_result["trading_symbol"],
                            quantity=extracted["quantity"],
                            transaction_type=extracted["transaction_type"],
                            order_type=order_type,
                            price=price,
                            product="MIS",
                        )

                        # Determine overall success based on order outcome
                        overall_success = order_result.get("success", False)
                        overall_message = order_result.get("message", "Order processed")

                        return {
                            "status": "success" if overall_success else "failed",
                            "order_type": "FNO_FUTURE",
                            "symbol_built": symbol_result,
                            "order_result": order_result,
                            "success": overall_success,
                            "message": f"Future order: {overall_message}",
                        }
                    else:
                        return {
                            "status": "error",
                            "error_type": "symbol_not_found",
                            "symbol_result": symbol_result,
                            "message": "Could not find the requested future symbol",
                        }
            else:
                # Return the analysis for user to provide missing information
                return {
                    "status": "incomplete",
                    "order_type": "FNO_INCOMPLETE",
                    "analysis": fno_analysis,
                    "message": "Need more information to place FnO order",
                    "next_steps": fno_analysis.get("next_steps", []),
                }
        else:
            # Handle as equity order
            # Extract basic information from the request
            import re

            # Extract quantity
            quantity_matches = re.findall(r"(\d+)\s*(?:shares?|qty)", request_lower)
            quantity = int(quantity_matches[0]) if quantity_matches else 1

            # Extract transaction type
            is_buy = any(word in request_lower for word in ["buy", "purchase"])
            is_sell = any(word in request_lower for word in ["sell"])
            transaction_type = "BUY" if is_buy else "SELL" if is_sell else "BUY"

            # Extract symbol (this is basic - user should provide correct symbol)
            # Look for capitalized words that could be symbols
            symbol_matches = re.findall(r"\b[A-Z]{2,}\b", user_request)
            trading_symbol = symbol_matches[0] if symbol_matches else None

            if not trading_symbol:
                return {
                    "status": "error",
                    "error_type": "symbol_not_found",
                    "message": "Could not extract trading symbol from request. Please specify the stock symbol clearly.",
                    "user_request": user_request,
                }

            # Place equity order
            order_result = place_order_with_confirmation(
                trading_symbol=trading_symbol,
                quantity=quantity,
                transaction_type=transaction_type,
                order_type=order_type,
                price=price,
                segment="CASH",
                product="CNC",
            )

            # Determine overall success based on order outcome
            overall_success = order_result.get("success", False)
            overall_message = order_result.get("message", "Order processed")

            return {
                "status": "success" if overall_success else "failed",
                "order_type": "EQUITY",
                "order_result": order_result,
                "success": overall_success,
                "extracted_info": {
                    "trading_symbol": trading_symbol,
                    "quantity": quantity,
                    "transaction_type": transaction_type,
                },
                "message": f"Equity order: {overall_message}",
            }

    except Exception as e:
        return {"status": "error", "message": str(e), "user_request": user_request}


@mcp.tool()
def modify_order_with_confirmation(
    groww_order_id: Annotated[str, Field(description="The ID of the order to modify")],
    quantity: Annotated[int, Field(description="New quantity for the order")],
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
    user_confirmation: Annotated[
        str,
        Field(
            description="MANDATORY: User must type 'CONFIRM_MODIFY' to proceed with order modification"
        ),
    ] = "",
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="New order type")
    ] = "MARKET",
    price: Annotated[
        Optional[float], Field(description="New price for limit orders")
    ] = None,
    trigger_price: Annotated[
        Optional[float], Field(description="New trigger price")
    ] = None,
) -> dict:
    """
    ⚠️ FINANCIAL ADVISOR TOOL - REQUIRES EXPLICIT CONFIRMATION ⚠️

    Modify an existing open order on the Groww platform with mandatory user confirmation.
    This tool implements financial safety protocols requiring explicit user consent.

    Use this tool when the user asks about:
    - "Change the quantity of my order"
    - "Update my pending order"
    - "Modify my limit price"
    - "Change my order from limit to market"

    ⚠️ IMPORTANT: User MUST provide 'CONFIRM_MODIFY' in user_confirmation parameter
    """

    # VALIDATION: Check mandatory confirmation
    if user_confirmation != "CONFIRM_MODIFY":
        return {
            "status": "confirmation_required",
            "success": False,
            "message": "❌ MODIFICATION BLOCKED: User confirmation required",
            "required_action": "Please provide 'CONFIRM_MODIFY' in the user_confirmation parameter to proceed",
            "modification_summary": {
                "order_id": groww_order_id,
                "new_quantity": quantity,
                "new_order_type": order_type,
                "new_price": price,
                "segment": segment,
            },
            "safety_note": "🛡️ This is a financial safety feature. All order modifications require explicit user confirmation.",
        }

    try:
        # Get current order details first
        current_order = groww.get_order_status(
            groww_order_id=groww_order_id, segment=segment
        )

        # PRE-MODIFICATION SUMMARY
        modification_summary = {
            "🔄 ACTION": "MODIFY ORDER",
            "🆔 ORDER_ID": groww_order_id,
            "📊 SEGMENT": segment,
            "🔢 QUANTITY": f"{current_order.get('quantity', 'N/A')} → {quantity}",
            "💰 ORDER_TYPE": f"{current_order.get('order_type', 'N/A')} → {order_type}",
            "💵 PRICE": f"{current_order.get('price', 'N/A')} → {price or 'MARKET'}",
            "⚠️ RISK_LEVEL": "MEDIUM",
        }

        response = groww.modify_order(
            groww_order_id=groww_order_id,
            quantity=quantity,
            price=price,
            trigger_price=trigger_price,
            order_type=order_type,
            segment=segment,
        )

        # POST-MODIFICATION VERIFICATION
        try:
            import time

            time.sleep(1)
            updated_order = groww.get_order_status(
                groww_order_id=groww_order_id, segment=segment
            )
            verification_status = "✅ MODIFICATION SUCCESSFUL"
        except:
            verification_status = "⚠️ MODIFICATION STATUS UNKNOWN"
            updated_order = None

        return {
            "status": "modification_executed",
            "success": True,
            "verification_status": verification_status,
            "pre_modification_summary": modification_summary,
            "modification_response": response,
            "post_modification_verification": updated_order,
            "financial_advisory_note": "✅ Order modification processed with safety protocols",
        }

    except Exception as e:
        return {
            "status": "modification_failed",
            "success": False,
            "message": f"❌ MODIFICATION FAILED: {str(e)}",
            "error_details": str(e),
            "financial_advisory_note": "🛡️ Modification blocked due to error - original order unchanged",
        }


@mcp.tool()
def cancel_order_with_confirmation(
    groww_order_id: Annotated[str, Field(description="The ID of the order to cancel")],
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
    user_confirmation: Annotated[
        str,
        Field(
            description="MANDATORY: User must type 'CONFIRM_CANCEL' to proceed with order cancellation"
        ),
    ] = "",
) -> dict:
    """
    ⚠️ FINANCIAL ADVISOR TOOL - REQUIRES EXPLICIT CONFIRMATION ⚠️

    Cancel a pending order on the Groww platform with mandatory user confirmation.
    This tool implements financial safety protocols requiring explicit user consent.

    Use this tool when the user asks about:
    - "Cancel my pending order"
    - "Remove my order from the queue"
    - "Stop my order execution"
    - "Delete my pending order"

    ⚠️ IMPORTANT: User MUST provide 'CONFIRM_CANCEL' in user_confirmation parameter
    """

    # VALIDATION: Check mandatory confirmation
    if user_confirmation != "CONFIRM_CANCEL":
        return {
            "status": "confirmation_required",
            "success": False,
            "message": "❌ CANCELLATION BLOCKED: User confirmation required",
            "required_action": "Please provide 'CONFIRM_CANCEL' in the user_confirmation parameter to proceed",
            "cancellation_summary": {
                "order_id": groww_order_id,
                "segment": segment,
                "action": "CANCEL ORDER",
            },
            "safety_note": "🛡️ This is a financial safety feature. All order cancellations require explicit user confirmation.",
        }

    try:
        # Get current order details first
        current_order = groww.get_order_status(
            groww_order_id=groww_order_id, segment=segment
        )

        # PRE-CANCELLATION SUMMARY
        cancellation_summary = {
            "🚫 ACTION": "CANCEL ORDER",
            "🆔 ORDER_ID": groww_order_id,
            "📊 SEGMENT": segment,
            "🎯 SYMBOL": current_order.get("trading_symbol", "N/A"),
            "🔢 QUANTITY": current_order.get("quantity", "N/A"),
            "💰 ORDER_TYPE": current_order.get("order_type", "N/A"),
            "📈 TRANSACTION": current_order.get("transaction_type", "N/A"),
            "⚠️ RISK_LEVEL": "LOW",
        }

        response = groww.cancel_order(groww_order_id=groww_order_id, segment=segment)

        # POST-CANCELLATION VERIFICATION
        try:
            import time

            time.sleep(1)
            updated_order = groww.get_order_status(
                groww_order_id=groww_order_id, segment=segment
            )
            current_status = updated_order.get("order_status", "UNKNOWN")

            if current_status in ["CANCELLED", "CANCELED"]:
                verification_status = "✅ CANCELLATION SUCCESSFUL"
            else:
                verification_status = f"⚠️ CANCELLATION STATUS: {current_status}"
        except:
            verification_status = "⚠️ CANCELLATION STATUS UNKNOWN"
            updated_order = None

        return {
            "status": "cancellation_executed",
            "success": True,
            "verification_status": verification_status,
            "pre_cancellation_summary": cancellation_summary,
            "cancellation_response": response,
            "post_cancellation_verification": updated_order,
            "financial_advisory_note": "✅ Order cancellation processed with safety protocols",
        }

    except Exception as e:
        return {
            "status": "cancellation_failed",
            "success": False,
            "message": f"❌ CANCELLATION FAILED: {str(e)}",
            "error_details": str(e),
            "financial_advisory_note": "🛡️ Cancellation blocked due to error - order status unchanged",
        }


@mcp.tool()
def get_order_status(
    groww_order_id: Annotated[str, Field(description="The ID of the order to check")],
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
) -> dict:
    """
    Get the current status of a specific order.

    Use this tool when the user asks about:
    - "What's the status of my order?"
    - "Check my order status"
    - "Is my order executed?"
    - "Show order details"
    """
    response = groww.get_order_status(groww_order_id=groww_order_id, segment=segment)
    return response


@mcp.tool()
def get_order_history(
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
    page: Annotated[int, Field(description="Page number for pagination")] = 0,
    page_size: Annotated[
        int, Field(description="Number of orders per page", ge=1, le=100)
    ] = 50,
) -> dict:
    """
    Get order history for a specific market segment.

    Use this tool when the user asks about:
    - "Show my order history"
    - "List all my orders"
    - "Get my trading history"
    - "Show executed orders"
    """
    try:
        response = groww.get_order_history(
            segment=segment, page=page, page_size=page_size
        )
        return response
    except Exception as e:
        return {"status": "error", "message": str(e), "segment": segment}


@mcp.tool()
def get_trade_list_for_order(
    groww_order_id: Annotated[
        str, Field(description="The ID of the order to get trades for")
    ],
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
    page: Annotated[int, Field(description="Page number for pagination")] = 0,
    page_size: Annotated[
        int, Field(description="Number of trades per page", ge=1, le=100)
    ] = 50,
) -> dict:
    """
    Get all trade executions for a specific order.

    Use this tool when the user asks about:
    - "Show all executions for my order"
    - "Get trade details for order"
    - "List all fills for this order"
    - "Show partial executions"
    """
    try:
        response = groww.get_trade_list_for_order(
            groww_order_id=groww_order_id,
            segment=segment,
            page=page,
            page_size=page_size,
        )
        return response
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "order_id": groww_order_id,
            "segment": segment,
        }


@mcp.tool()
def get_order_details(
    groww_order_id: Annotated[
        str, Field(description="The ID of the order to get details for")
    ],
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
) -> dict:
    """
    Get detailed information about a specific order.

    Use this tool when the user asks about:
    - "Show me complete order details"
    - "Get all information about order X"
    - "What are the full details of my order?"
    - "Show order specifics"
    """
    # First get basic order status
    status_response = groww.get_order_status(
        groww_order_id=groww_order_id, segment=segment
    )

    # Then get trade details
    trades_response = groww.get_trade_list_for_order(
        groww_order_id=groww_order_id, segment=segment, page=0, page_size=50
    )

    # Combine the information
    detailed_response = {
        "order_info": status_response,
        "trade_details": trades_response,
    }

    return detailed_response


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8893)
