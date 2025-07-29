import os
from typing import Optional, Dict, List, Annotated, Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
import pandas as pd
import re
from datetime import datetime, timedelta
from ..helper import groww_login

groww = groww_login()

mcp = FastMCP(
    name="Groww Instruments MCP Server",
    instructions=f"A Groww MCP Server for instrument data and lookup operations",
)

# =============================================================================
# EXCHANGE DETECTION UTILITY
# =============================================================================

def detect_exchange_for_underlying(underlying_symbol: str) -> str:
    """
    Automatically detect the correct exchange (NSE or BSE) for a given underlying symbol
    based on Indian market knowledge and actual instrument data.
    
    Args:
        underlying_symbol: The underlying symbol (e.g., 'NIFTY', 'SENSEX', 'RELIANCE')
        
    Returns:
        str: 'NSE' or 'BSE' based on where the underlying is primarily traded
    """
    underlying_upper = underlying_symbol.upper().strip()
    
    # Known BSE indices and symbols
    bse_indices = {
        'SENSEX', 'BSE30', 'BANKEX', 'BSESML', 'BSEMID', 'BSEIT', 'BSEREALTY',
        'BSEHC', 'BSEPOWER', 'BSECG', 'BSEMETAL', 'BSEOIL', 'BSEPSU'
    }
    
    # Known NSE indices and symbols  
    nse_indices = {
        'NIFTY', 'BANKNIFTY', 'NIFTYNEXT50', 'NIFTYIT', 'NIFTYPHARMA', 
        'NIFTYBANK', 'NIFTYFIN', 'NIFTYAUTO', 'NIFTYMETAL', 'NIFTYREALTY',
        'CNXNIFTY', 'NIFTY50', 'FINNIFTY', 'MIDCPNIFTY'
    }
    
    # Direct match for known indices
    if underlying_upper in bse_indices:
        return 'BSE'
    elif underlying_upper in nse_indices:
        return 'NSE'
    
    # For individual stocks, check both exchanges and return the one with more FnO instruments
    try:
        instruments_df = groww.get_all_instruments()
        
        # Check NSE first (as it's more common for FnO)
        nse_fno_count = len(instruments_df[
            (instruments_df['segment'] == 'FNO') & 
            (instruments_df['exchange'] == 'NSE') &
            (instruments_df['groww_symbol'].str.contains(f'NSE-{underlying_upper}-', na=False))
        ])
        
        # Check BSE
        bse_fno_count = len(instruments_df[
            (instruments_df['segment'] == 'FNO') & 
            (instruments_df['exchange'] == 'BSE') &
            (instruments_df['groww_symbol'].str.contains(f'BSE-{underlying_upper}-', na=False))
        ])
        
        # Return exchange with more FnO instruments, prefer NSE if tie
        if bse_fno_count > nse_fno_count:
            return 'BSE'
        else:
            return 'NSE'
            
    except Exception:
        # Default fallback logic
        # SENSEX variants go to BSE, everything else to NSE
        if 'SENSEX' in underlying_upper or underlying_upper.startswith('BSE'):
            return 'BSE'
        else:
            return 'NSE'

# =============================================================================
# INSTRUMENT LOOKUP AND DATA TOOLS
# =============================================================================


@mcp.tool()
def get_instrument_by_groww_symbol(
    groww_symbol: Annotated[
        str, Field(description="Groww symbol of the instrument (e.g., 'NSE-RELIANCE')")
    ]
) -> dict:
    """
    Get detailed information about an instrument using its Groww symbol.

    Use this tool when the user asks about:
    - "Get details of NSE-RELIANCE"
    - "Show information about instrument by groww symbol"
    - "Find instrument using groww symbol"
    - "Look up instrument details"
    """
    response = groww.get_instrument_by_groww_symbol(groww_symbol=groww_symbol)
    return response


@mcp.tool()
def get_instrument_by_exchange_and_trading_symbol(
    exchange: Annotated[Literal["NSE", "BSE"], Field(description="Exchange code")],
    trading_symbol: Annotated[
        str, Field(description="Trading symbol of the instrument")
    ],
) -> dict:
    """
    Get detailed information about an instrument using exchange and trading symbol.

    Use this tool when the user asks about:
    - "Get details of RELIANCE on NSE"
    - "Show information about TCS stock"
    - "Find instrument by trading symbol"
    - "Look up stock details on specific exchange"
    """
    response = groww.get_instrument_by_exchange_and_trading_symbol(
        exchange=exchange, trading_symbol=trading_symbol
    )
    return response


@mcp.tool()
def get_instrument_by_exchange_token(
    exchange_token: Annotated[
        str, Field(description="Exchange token of the instrument")
    ]
) -> dict:
    """
    Get detailed information about an instrument using its exchange token.

    Use this tool when the user asks about:
    - "Get instrument details by token 2885"
    - "Find instrument using exchange token"
    - "Look up instrument by token ID"
    - "Search instrument with token number"
    """
    response = groww.get_instrument_by_exchange_token(exchange_token=exchange_token)
    return response


@mcp.tool()
def get_all_instruments() -> dict:
    """
    Get all available instruments data as a structured response.

    Use this tool when the user asks about:
    - "Get all instruments data"
    - "Show complete instrument list"
    - "Download all available instruments"
    - "Get full instrument database"
    """
    try:
        instruments_df = groww.get_all_instruments()
        # Convert DataFrame to dict format for JSON serialization
        instruments_dict = instruments_df.to_dict(orient="records")
        return {
            "status": "success",
            "data": instruments_dict,
            "total_instruments": len(instruments_dict),
            "message": f"Retrieved {len(instruments_dict)} instruments",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}


@mcp.tool()
def download_instruments_csv(
    save_path: Annotated[
        str, Field(description="Path where to save the CSV file")
    ] = "instruments.csv"
) -> dict:
    """
    Download complete instruments data and save as CSV file.

    Use this tool when the user asks about:
    - "Save instruments to CSV"
    - "Export instruments to file"
    - "Download instruments data"
    - "Create CSV of all instruments"
    """
    try:
        instruments_df = groww.get_all_instruments()
        instruments_df.to_csv(save_path, index=False)
        return {
            "status": "success",
            "message": f"Instruments data saved to {save_path}",
            "file_path": save_path,
            "total_instruments": len(instruments_df),
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "file_path": None}


@mcp.tool()
def get_instrument_csv_url() -> dict:
    """
    Get the URL to download the latest instruments CSV file.

    Use this tool when the user asks about:
    - "Get CSV download URL"
    - "Where can I download instruments data?"
    - "Show CSV file link"
    - "Get instrument data URL"
    """
    try:
        csv_url = groww.INSTRUMENT_CSV_URL
        return {
            "status": "success",
            "csv_url": csv_url,
            "message": "Use this URL to download the latest instruments CSV file",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "csv_url": None}


@mcp.tool()
def search_instruments_by_name(
    name_query: Annotated[
        str, Field(description="Instrument name or partial name to search for")
    ],
    limit: Annotated[
        int, Field(description="Maximum number of results to return", ge=1, le=100)
    ] = 10,
) -> dict:
    """
    Search for instruments by name or partial name match.

    Use this tool when the user asks about:
    - "Find stocks containing 'Reliance'"
    - "Search for companies with 'Bank' in name"
    - "Look for instruments matching 'HDFC'"
    - "Find all stocks with specific keyword"
    """
    try:
        instruments_df = groww.get_all_instruments()
        # Filter instruments by name containing the query (case insensitive)
        filtered_df = instruments_df[
            instruments_df["name"].str.contains(name_query, case=False, na=False)
        ].head(limit)

        results = filtered_df.to_dict(orient="records")
        return {
            "status": "success",
            "data": results,
            "total_found": len(results),
            "search_query": name_query,
            "message": f"Found {len(results)} instruments matching '{name_query}'",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": [],
            "search_query": name_query,
        }


@mcp.tool()
def get_instruments_by_exchange(
    exchange: Annotated[Literal["NSE", "BSE"], Field(description="Exchange code")],
    limit: Annotated[
        int, Field(description="Maximum number of results to return", ge=1, le=1000)
    ] = 100,
) -> dict:
    """
    Get instruments filtered by specific exchange.

    Use this tool when the user asks about:
    - "Show all NSE instruments"
    - "List BSE stocks"
    - "Get instruments from specific exchange"
    - "Filter instruments by exchange"
    """
    try:
        instruments_df = groww.get_all_instruments()
        # Filter by exchange
        filtered_df = instruments_df[instruments_df["exchange"] == exchange].head(limit)

        results = filtered_df.to_dict(orient="records")
        return {
            "status": "success",
            "data": results,
            "total_found": len(results),
            "exchange": exchange,
            "message": f"Found {len(results)} instruments on {exchange}",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "data": [], "exchange": exchange}


@mcp.tool()
def get_instruments_by_segment(
    segment: Annotated[Literal["CASH", "FNO"], Field(description="Market segment")],
    limit: Annotated[
        int, Field(description="Maximum number of results to return", ge=1, le=1000)
    ] = 100,
) -> dict:
    """
    Get instruments filtered by market segment.

    Use this tool when the user asks about:
    - "Show all CASH segment instruments"
    - "List FNO instruments"
    - "Get derivatives instruments"
    - "Filter instruments by segment"
    """
    try:
        instruments_df = groww.get_all_instruments()
        # Filter by segment
        filtered_df = instruments_df[instruments_df["segment"] == segment].head(limit)

        results = filtered_df.to_dict(orient="records")
        return {
            "status": "success",
            "data": results,
            "total_found": len(results),
            "segment": segment,
            "message": f"Found {len(results)} instruments in {segment} segment",
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "data": [], "segment": segment}


# =============================================================================
# FNO SYMBOL BUILDING TOOLS
# =============================================================================


@mcp.tool()
def get_available_option_expiries(
    underlying_symbol: Annotated[
        str,
        Field(description="Underlying symbol (e.g., 'NIFTY', 'BANKNIFTY', 'RELIANCE', 'SENSEX')"),
    ],
    exchange: Annotated[
        Optional[Literal["NSE", "BSE"]], Field(description="Exchange code (auto-detected if not provided)")
    ] = None,
) -> dict:
    """
    Get all available expiry dates for options of a given underlying symbol.
    Exchange is automatically detected based on the underlying symbol and Indian market knowledge.

    Use this tool when the user asks about:
    - "What are the available expiry dates for NIFTY options?"
    - "Show me all RELIANCE option expiries"  
    - "List expiry dates for Bank Nifty options"
    - "Available option expiry dates for SENSEX"
    - "Get SENSEX option expiries"
    """
    try:
        instruments_df = groww.get_all_instruments()

        # Auto-detect exchange if not provided
        if exchange is None:
            exchange = detect_exchange_for_underlying(underlying_symbol)

        # Filter for FNO options of the underlying symbol
        option_pattern = f"{underlying_symbol}.*CE|{underlying_symbol}.*PE"
        fno_options = instruments_df[
            (instruments_df["segment"] == "FNO")
            & (instruments_df["exchange"] == exchange)
            & (
                instruments_df["trading_symbol"].str.contains(
                    option_pattern, regex=True
                )
            )
        ]

        # If no options found with detected/provided exchange, try the other exchange
        if fno_options.empty:
            alternative_exchange = "BSE" if exchange == "NSE" else "NSE"
            fno_options = instruments_df[
                (instruments_df["segment"] == "FNO")
                & (instruments_df["exchange"] == alternative_exchange)
                & (
                    instruments_df["trading_symbol"].str.contains(
                        option_pattern, regex=True
                    )
                )
            ]
            if not fno_options.empty:
                exchange = alternative_exchange  # Update exchange to the one that worked

        if fno_options.empty:
            return {
                "status": "success",
                "underlying_symbol": underlying_symbol,
                "exchange_checked": exchange,
                "expiry_dates": [],
                "message": f"No options found for {underlying_symbol} on both NSE and BSE",
            }

        # Extract expiry dates from groww_symbol
        expiry_dates = set()
        for _, row in fno_options.iterrows():
            # Extract expiry from groww_symbol format: NSE-SYMBOL-DATE-STRIKE-CE/PE
            parts = str(row["groww_symbol"]).split("-")
            if len(parts) >= 3:
                expiry_dates.add(parts[2])

        sorted_expiries = sorted(list(expiry_dates))

        return {
            "status": "success",
            "underlying_symbol": underlying_symbol,
            "exchange": exchange,
            "expiry_dates": sorted_expiries,
            "total_expiries": len(sorted_expiries),
            "message": f"Found {len(sorted_expiries)} expiry dates for {underlying_symbol} options",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "underlying_symbol": underlying_symbol,
            "expiry_dates": [],
        }


@mcp.tool()
def get_available_option_strikes(
    underlying_symbol: Annotated[
        str,
        Field(description="Underlying symbol (e.g., 'NIFTY', 'BANKNIFTY', 'RELIANCE', 'SENSEX')"),
    ],
    expiry_date: Annotated[
        str, Field(description="Expiry date (e.g., '26Jun25', '28Aug25')")
    ],
    option_type: Annotated[
        Literal["CE", "PE", "BOTH"],
        Field(description="Option type - CE for Call, PE for Put, BOTH for both"),
    ] = "BOTH",
    exchange: Annotated[
        Optional[Literal["NSE", "BSE"]], Field(description="Exchange code (auto-detected if not provided)")
    ] = None,
) -> dict:
    """
    Get all available strike prices for options of a given underlying symbol and expiry.
    Exchange is automatically detected based on the underlying symbol and Indian market knowledge.

    Use this tool when the user asks about:
    - "What strike prices are available for NIFTY options expiring on 26Jun25?"
    - "Show me all strike prices for RELIANCE calls"
    - "List available strikes for Bank Nifty puts"
    - "Available option strikes for SENSEX"
    - "Get SENSEX option strikes"
    """
    try:
        instruments_df = groww.get_all_instruments()

        # Auto-detect exchange if not provided
        if exchange is None:
            exchange = detect_exchange_for_underlying(underlying_symbol)

        # Filter for specific options
        if option_type == "BOTH":
            option_pattern = f"{underlying_symbol}.*CE|{underlying_symbol}.*PE"
        else:
            option_pattern = f"{underlying_symbol}.*{option_type}"

        fno_options = instruments_df[
            (instruments_df["segment"] == "FNO")
            & (instruments_df["exchange"] == exchange)
            & (
                instruments_df["trading_symbol"].str.contains(
                    option_pattern, regex=True
                )
            )
        ]

        # Filter by expiry date
        filtered_options = fno_options[
            fno_options["groww_symbol"].str.contains(f"-{expiry_date}-")
        ]

        # If no options found with detected/provided exchange, try the other exchange
        if filtered_options.empty:
            alternative_exchange = "BSE" if exchange == "NSE" else "NSE"
            fno_options = instruments_df[
                (instruments_df["segment"] == "FNO")
                & (instruments_df["exchange"] == alternative_exchange)
                & (
                    instruments_df["trading_symbol"].str.contains(
                        option_pattern, regex=True
                    )
                )
            ]
            # Filter by expiry date again
            filtered_options = fno_options[
                fno_options["groww_symbol"].str.contains(f"-{expiry_date}-")
            ]
            if not filtered_options.empty:
                exchange = alternative_exchange  # Update exchange to the one that worked

        if filtered_options.empty:
            return {
                "status": "success",
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "option_type": option_type,
                "exchange_checked": exchange,
                "strike_prices": [],
                "message": f"No options found for {underlying_symbol} expiring on {expiry_date} on both NSE and BSE",
            }

        # Extract strike prices from groww_symbol
        strikes = []
        for _, row in filtered_options.iterrows():
            # Extract strike from groww_symbol format: NSE-SYMBOL-DATE-STRIKE-CE/PE
            parts = str(row["groww_symbol"]).split("-")
            if len(parts) >= 4:
                try:
                    strike_price = float(parts[3])
                    opt_type = parts[4] if len(parts) > 4 else "UNKNOWN"
                    strikes.append(
                        {
                            "strike_price": strike_price,
                            "option_type": opt_type,
                            "trading_symbol": row["trading_symbol"],
                            "groww_symbol": row["groww_symbol"],
                        }
                    )
                except ValueError:
                    continue

        # Sort by strike price
        strikes.sort(key=lambda x: x["strike_price"])

        return {
            "status": "success",
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
            "option_type": option_type,
            "exchange": exchange,
            "strike_prices": strikes,
            "total_strikes": len(strikes),
            "message": f"Found {len(strikes)} strike prices for {underlying_symbol} options expiring on {expiry_date}",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
            "strike_prices": [],
        }


@mcp.tool()
def build_option_symbol(
    underlying_symbol: Annotated[
        str,
        Field(description="Underlying symbol (e.g., 'NIFTY', 'BANKNIFTY', 'RELIANCE', 'SENSEX')"),
    ],
    expiry_date: Annotated[
        str, Field(description="Expiry date (e.g., '26Jun25', '28Aug25')")
    ],
    strike_price: Annotated[
        float, Field(description="Strike price (e.g., 24000, 375.0)")
    ],
    option_type: Annotated[
        Literal["CE", "PE"], Field(description="Option type - CE for Call, PE for Put")
    ],
    exchange: Annotated[
        Optional[Literal["NSE", "BSE"]], Field(description="Exchange code (auto-detected if not provided)")
    ] = None,
) -> dict:
    """
    Build correct option symbol based on user requirements and validate it exists.
    Exchange is automatically detected based on the underlying symbol and Indian market knowledge.

    Use this tool when the user asks about:
    - "Build option symbol for NIFTY 24000 CE expiring on 26Jun25"
    - "Create option symbol for RELIANCE 375 PE"
    - "Generate trading symbol for Bank Nifty call option"
    - "Build FnO symbol for options trading"
    - "Build SENSEX option symbol"
    """
    try:
        instruments_df = groww.get_all_instruments()

        # Auto-detect exchange if not provided
        if exchange is None:
            exchange = detect_exchange_for_underlying(underlying_symbol)

        # Construct expected groww symbol
        expected_groww_symbol = f"{exchange}-{underlying_symbol}-{expiry_date}-{int(strike_price)}-{option_type}"

        # Search for the exact symbol
        matching_instrument = instruments_df[
            (instruments_df["groww_symbol"] == expected_groww_symbol)
            & (instruments_df["segment"] == "FNO")
        ]

        # If no match found with detected/provided exchange, try the other exchange
        if matching_instrument.empty:
            alternative_exchange = "BSE" if exchange == "NSE" else "NSE"
            alternative_groww_symbol = f"{alternative_exchange}-{underlying_symbol}-{expiry_date}-{int(strike_price)}-{option_type}"
            
            matching_instrument = instruments_df[
                (instruments_df["groww_symbol"] == alternative_groww_symbol)
                & (instruments_df["segment"] == "FNO")
            ]
            
            if not matching_instrument.empty:
                expected_groww_symbol = alternative_groww_symbol
                exchange = alternative_exchange

        if not matching_instrument.empty:
            instrument_data = matching_instrument.iloc[0].to_dict()
            return {
                "status": "success",
                "symbol_found": True,
                "trading_symbol": instrument_data["trading_symbol"],
                "groww_symbol": instrument_data["groww_symbol"],
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
                "exchange": exchange,
                "exchange_token": instrument_data.get("exchange_token", ""),
                "message": f"Option symbol found: {instrument_data['trading_symbol']}",
            }
        else:
            # Try to find similar symbols to suggest alternatives
            similar_pattern = f"{underlying_symbol}.*{option_type}"
            similar_options = instruments_df[
                (instruments_df["segment"] == "FNO")
                & (instruments_df["exchange"] == exchange)
                & (
                    instruments_df["trading_symbol"].str.contains(
                        similar_pattern, regex=True
                    )
                )
                & (instruments_df["groww_symbol"].str.contains(f"-{expiry_date}-"))
            ]

            suggestions = []
            if not similar_options.empty:
                for _, row in similar_options.head(5).iterrows():
                    suggestions.append(
                        {
                            "trading_symbol": row["trading_symbol"],
                            "groww_symbol": row["groww_symbol"],
                        }
                    )

            return {
                "status": "success",
                "symbol_found": False,
                "requested_symbol": expected_groww_symbol,
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "strike_price": strike_price,
                "option_type": option_type,
                "exchange": exchange,
                "suggestions": suggestions,
                "message": f"Symbol not found: {expected_groww_symbol}. See suggestions for similar symbols.",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
            "strike_price": strike_price,
            "option_type": option_type,
        }


@mcp.tool()
def build_future_symbol(
    underlying_symbol: Annotated[
        str,
        Field(description="Underlying symbol (e.g., 'NIFTY', 'BANKNIFTY', 'RELIANCE', 'SENSEX')"),
    ],
    expiry_date: Annotated[
        str, Field(description="Expiry date (e.g., '26Jun25', '28Aug25')")
    ],
    exchange: Annotated[
        Optional[Literal["NSE", "BSE"]], Field(description="Exchange code (auto-detected if not provided)")
    ] = None,
) -> dict:
    """
    Build correct future symbol based on user requirements and validate it exists.
    Exchange is automatically detected based on the underlying symbol and Indian market knowledge.

    Use this tool when the user asks about:
    - "Build future symbol for NIFTY expiring on 26Jun25"
    - "Create future symbol for RELIANCE"
    - "Generate trading symbol for Bank Nifty future"
    - "Build FnO symbol for futures trading"
    - "Build SENSEX future symbol"
    """
    try:
        instruments_df = groww.get_all_instruments()

        # Auto-detect exchange if not provided
        if exchange is None:
            exchange = detect_exchange_for_underlying(underlying_symbol)

        # Construct expected groww symbol
        expected_groww_symbol = f"{exchange}-{underlying_symbol}-{expiry_date}-FUT"

        # Search for the exact symbol
        matching_instrument = instruments_df[
            (instruments_df["groww_symbol"] == expected_groww_symbol)
            & (instruments_df["segment"] == "FNO")
        ]

        # If no match found with detected/provided exchange, try the other exchange
        if matching_instrument.empty:
            alternative_exchange = "BSE" if exchange == "NSE" else "NSE"
            alternative_groww_symbol = f"{alternative_exchange}-{underlying_symbol}-{expiry_date}-FUT"
            
            matching_instrument = instruments_df[
                (instruments_df["groww_symbol"] == alternative_groww_symbol)
                & (instruments_df["segment"] == "FNO")
            ]
            
            if not matching_instrument.empty:
                expected_groww_symbol = alternative_groww_symbol
                exchange = alternative_exchange

        if not matching_instrument.empty:
            instrument_data = matching_instrument.iloc[0].to_dict()
            return {
                "status": "success",
                "symbol_found": True,
                "trading_symbol": instrument_data["trading_symbol"],
                "groww_symbol": instrument_data["groww_symbol"],
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "exchange": exchange,
                "exchange_token": instrument_data.get("exchange_token", ""),
                "message": f"Future symbol found: {instrument_data['trading_symbol']}",
            }
        else:
            # Try to find similar symbols to suggest alternatives
            similar_pattern = f"{underlying_symbol}.*FUT"
            similar_futures = instruments_df[
                (instruments_df["segment"] == "FNO")
                & (instruments_df["exchange"] == exchange)
                & (
                    instruments_df["trading_symbol"].str.contains(
                        similar_pattern, regex=True
                    )
                )
            ]

            suggestions = []
            if not similar_futures.empty:
                for _, row in similar_futures.head(5).iterrows():
                    suggestions.append(
                        {
                            "trading_symbol": row["trading_symbol"],
                            "groww_symbol": row["groww_symbol"],
                        }
                    )

            return {
                "status": "success",
                "symbol_found": False,
                "requested_symbol": expected_groww_symbol,
                "underlying_symbol": underlying_symbol,
                "expiry_date": expiry_date,
                "exchange": exchange,
                "suggestions": suggestions,
                "message": f"Symbol not found: {expected_groww_symbol}. See suggestions for similar symbols.",
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
        }


@mcp.tool()
def smart_fno_order_assistant(
    user_query: Annotated[
        str,
        Field(
            description="User's order request (e.g., 'I want to buy NIFTY 24000 call option', 'Buy RELIANCE future')"
        ),
    ],
    quantity: Annotated[
        Optional[int], Field(description="Number of lots/shares")
    ] = None,
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="Order type")
    ] = "MARKET",
    price: Annotated[
        Optional[float], Field(description="Limit price (required for LIMIT orders)")
    ] = None,
) -> dict:
    """
    Intelligent FnO order assistant that analyzes user queries and guides them to place correct FnO orders.
    Asks appropriate questions and builds the right symbol for options and futures.

    Use this tool when the user asks about:
    - "I want to buy NIFTY call option"
    - "Place order for Bank Nifty put"
    - "Buy RELIANCE future"
    - "Trade options on TCS"
    - Any FnO order request where symbol details are incomplete
    """
    try:
        # Parse the user query to extract information
        query_lower = user_query.lower()

        # Initialize result structure
        result = {
            "status": "analyzing",
            "user_query": user_query,
            "extracted_info": {},
            "missing_info": [],
            "next_steps": [],
            "available_options": {},
            "ready_to_order": False,
        }

        # Extract underlying symbol
        instruments_df = groww.get_all_instruments()
        underlying_symbols = set()
        fno_instruments = instruments_df[instruments_df["segment"] == "FNO"]

        for _, row in fno_instruments.iterrows():
            # Extract underlying from groww_symbol: NSE-SYMBOL-DATE-...
            parts = str(row["groww_symbol"]).split("-")
            if len(parts) >= 2:
                underlying_symbols.add(parts[1])

        # Try to find underlying symbol in query
        found_underlying = None
        for symbol in underlying_symbols:
            if symbol.lower() in query_lower:
                found_underlying = symbol
                break

        if found_underlying:
            result["extracted_info"]["underlying_symbol"] = found_underlying
        else:
            result["missing_info"].append("underlying_symbol")
            result["next_steps"].append(
                "Please specify the underlying symbol (e.g., NIFTY, BANKNIFTY, RELIANCE)"
            )

        # Determine instrument type (option vs future)
        is_option = any(
            word in query_lower for word in ["option", "call", "put", "ce", "pe"]
        )
        is_future = any(word in query_lower for word in ["future", "fut"])

        if is_option:
            result["extracted_info"]["instrument_type"] = "OPTION"

            # Determine option type
            if any(word in query_lower for word in ["call", "ce"]):
                result["extracted_info"]["option_type"] = "CE"
            elif any(word in query_lower for word in ["put", "pe"]):
                result["extracted_info"]["option_type"] = "PE"
            else:
                result["missing_info"].append("option_type")
                result["next_steps"].append(
                    "Please specify option type: Call (CE) or Put (PE)?"
                )

            # Look for strike price in query
            import re

            strike_matches = re.findall(r"(\d+(?:\.\d+)?)", user_query)
            if strike_matches:
                # Take the largest number as potential strike price
                potential_strikes = [float(match) for match in strike_matches]
                result["extracted_info"]["potential_strike_prices"] = potential_strikes
            else:
                result["missing_info"].append("strike_price")
                result["next_steps"].append("Please specify the strike price")

        elif is_future:
            result["extracted_info"]["instrument_type"] = "FUTURE"
        else:
            result["missing_info"].append("instrument_type")
            result["next_steps"].append(
                "Please specify if you want to trade Options or Futures"
            )

        # Get available expiries if underlying is known
        if found_underlying:
            try:
                # Get expiries directly from instruments data
                exchange_for_underlying = detect_exchange_for_underlying(found_underlying)
                
                # Filter for FNO options of the underlying symbol
                option_pattern = f"{found_underlying}.*CE|{found_underlying}.*PE"
                fno_options = instruments_df[
                    (instruments_df["segment"] == "FNO")
                    & (instruments_df["exchange"] == exchange_for_underlying)
                    & (
                        instruments_df["trading_symbol"].str.contains(
                            option_pattern, regex=True
                        )
                    )
                ]

                if not fno_options.empty:
                    # Extract expiry dates from groww_symbol
                    expiry_dates = set()
                    for _, row in fno_options.iterrows():
                        # Extract expiry from groww_symbol format: NSE-SYMBOL-DATE-STRIKE-CE/PE
                        parts = str(row["groww_symbol"]).split("-")
                        if len(parts) >= 3:
                            expiry_dates.add(parts[2])

                    sorted_expiries = sorted(list(expiry_dates))[:5]  # First 5 expiries
                    
                    if sorted_expiries:
                        result["available_options"]["expiry_dates"] = sorted_expiries

                        # If no expiry specified, suggest the nearest
                        if "expiry_date" not in result["extracted_info"]:
                            result["missing_info"].append("expiry_date")
                            result["next_steps"].append(
                                f"Please choose expiry date from: {sorted_expiries[:3]}"
                            )
            except:
                pass

        # Determine transaction type
        is_buy = any(word in query_lower for word in ["buy", "purchase", "long"])
        is_sell = any(word in query_lower for word in ["sell", "short"])

        if is_buy:
            result["extracted_info"]["transaction_type"] = "BUY"
        elif is_sell:
            result["extracted_info"]["transaction_type"] = "SELL"
        else:
            result["missing_info"].append("transaction_type")
            result["next_steps"].append("Please specify if you want to BUY or SELL")

        # Check if quantity is provided
        if quantity:
            result["extracted_info"]["quantity"] = quantity
        else:
            result["missing_info"].append("quantity")
            result["next_steps"].append("Please specify the quantity (number of lots)")

        # Check if all required info is available
        required_for_option = [
            "underlying_symbol",
            "instrument_type",
            "option_type",
            "strike_price",
            "expiry_date",
            "transaction_type",
            "quantity",
        ]
        required_for_future = [
            "underlying_symbol",
            "instrument_type",
            "expiry_date",
            "transaction_type",
            "quantity",
        ]

        if result["extracted_info"].get("instrument_type") == "OPTION":
            missing_required = [
                field
                for field in required_for_option
                if field in result["missing_info"]
            ]
        elif result["extracted_info"].get("instrument_type") == "FUTURE":
            missing_required = [
                field
                for field in required_for_future
                if field in result["missing_info"]
            ]
        else:
            missing_required = result["missing_info"]

        if not missing_required:
            result["ready_to_order"] = True
            result["status"] = "ready"
            result["message"] = (
                "All required information collected. Ready to build symbol and place order."
            )
        else:
            result["status"] = "incomplete"
            result["message"] = f"Missing information: {', '.join(missing_required)}"

        return result

    except Exception as e:
        return {"status": "error", "message": str(e), "user_query": user_query}


@mcp.tool()
def build_iron_condor(
    underlying_symbol: Annotated[
        str,
        Field(description="Underlying symbol (e.g., 'NIFTY', 'BANKNIFTY', 'SENSEX')"),
    ],
    expiry_date: Annotated[
        str, Field(description="Expiry date (e.g., '01Jul25', '26Jun25')")
    ],
    center_strike: Annotated[
        float, Field(description="Center strike price around which to build the condor")
    ],
    wing_width: Annotated[
        int, Field(description="Distance between strikes (e.g., 100, 500)")
    ] = 100,
    exchange: Annotated[
        Optional[Literal["NSE", "BSE"]], Field(description="Exchange (auto-detected if not provided)")
    ] = None,
) -> dict:
    """
    Build a complete iron condor strategy with all four option legs.
    An iron condor consists of:
    - Sell 1 Call at center_strike + wing_width/2
    - Buy 1 Call at center_strike + wing_width
    - Sell 1 Put at center_strike - wing_width/2  
    - Buy 1 Put at center_strike - wing_width

    Use this tool when the user asks about:
    - "Build iron condor for SENSEX"
    - "Create wide iron condor strategy"
    - "Set up iron condor for July expiry"
    - "Build condor strategy on NIFTY"
    """
    try:
        # Auto-detect exchange if not provided
        if exchange is None:
            exchange = detect_exchange_for_underlying(underlying_symbol)

        # Calculate the four strikes for iron condor
        short_call_strike = center_strike + (wing_width / 2)
        long_call_strike = center_strike + wing_width
        short_put_strike = center_strike - (wing_width / 2)
        long_put_strike = center_strike - wing_width

        strikes = [
            {"strike": long_put_strike, "type": "PE", "action": "BUY", "leg": "Long Put"},
            {"strike": short_put_strike, "type": "PE", "action": "SELL", "leg": "Short Put"}, 
            {"strike": short_call_strike, "type": "CE", "action": "SELL", "leg": "Short Call"},
            {"strike": long_call_strike, "type": "CE", "action": "BUY", "leg": "Long Call"}
        ]

        # Build symbols for each leg
        legs = []
        successful_legs = 0
        failed_legs = []

        for strike_info in strikes:
            try:
                # Try to build the option symbol
                symbol_result = build_option_symbol.__wrapped__(
                    underlying_symbol=underlying_symbol,
                    expiry_date=expiry_date,
                    strike_price=strike_info["strike"],
                    option_type=strike_info["type"],
                    exchange=exchange
                )

                if symbol_result.get("symbol_found", False):
                    legs.append({
                        "leg_name": strike_info["leg"],
                        "action": strike_info["action"],
                        "strike_price": strike_info["strike"],
                        "option_type": strike_info["type"],
                        "trading_symbol": symbol_result["trading_symbol"],
                        "groww_symbol": symbol_result["groww_symbol"],
                        "exchange_token": symbol_result.get("exchange_token", ""),
                        "status": "found"
                    })
                    successful_legs += 1
                else:
                    failed_legs.append({
                        "leg_name": strike_info["leg"],
                        "strike_price": strike_info["strike"],
                        "option_type": strike_info["type"],
                        "status": "not_found",
                        "requested_symbol": symbol_result.get("requested_symbol", "")
                    })
            except Exception as e:
                failed_legs.append({
                    "leg_name": strike_info["leg"],
                    "strike_price": strike_info["strike"],
                    "option_type": strike_info["type"],
                    "status": "error",
                    "error": str(e)
                })

        # Determine overall status
        if successful_legs == 4:
            status = "complete"
            message = f"✅ Iron condor built successfully for {underlying_symbol} with all 4 legs"
        elif successful_legs > 0:
            status = "partial" 
            message = f"⚠️ Iron condor partially built: {successful_legs}/4 legs found"
        else:
            status = "failed"
            message = f"❌ Could not build iron condor: No option symbols found"

        return {
            "status": status,
            "strategy": "Iron Condor",
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
            "exchange": exchange,
            "center_strike": center_strike,
            "wing_width": wing_width,
            "successful_legs": successful_legs,
            "total_legs": 4,
            "legs": legs,
            "failed_legs": failed_legs,
            "message": message,
            "strategy_description": f"Iron Condor: Sell {short_put_strike}PE + {short_call_strike}CE, Buy {long_put_strike}PE + {long_call_strike}CE",
            "max_profit_zone": f"Between {short_put_strike} and {short_call_strike}",
            "breakeven_points": [
                short_put_strike - (wing_width / 2),  # Lower breakeven
                short_call_strike + (wing_width / 2)   # Upper breakeven  
            ]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to build iron condor: {str(e)}",
            "underlying_symbol": underlying_symbol,
            "expiry_date": expiry_date,
            "center_strike": center_strike,
            "wing_width": wing_width
        }


# =============================================================================
# FNO ORDER PLACEMENT TOOLS
# =============================================================================


@mcp.tool()
def place_fno_order(
    trading_symbol: Annotated[
        str,
        Field(
            description="Trading symbol of the FnO instrument (e.g., 'NIFTY25JUN24000CE', 'BANKNIFTY25AUGFUT')"
        ),
    ],
    quantity: Annotated[int, Field(description="Number of lots to trade")],
    transaction_type: Annotated[
        Literal["BUY", "SELL"], Field(description="BUY or SELL")
    ],
    order_type: Annotated[
        Literal["MARKET", "LIMIT"], Field(description="Order type")
    ] = "MARKET",
    price: Annotated[
        Optional[float], Field(description="Limit price (required for LIMIT orders)")
    ] = None,
    product: Annotated[
        Literal["MIS", "NRML"],
        Field(description="Product type - MIS for intraday, NRML for positional"),
    ] = "MIS",
    exchange: Annotated[Optional[Literal["NSE", "BSE"]], Field(description="Exchange (auto-detected if not provided)")] = None,
) -> dict:
    """
    Place FnO (Futures and Options) order with proper validation and margin checks.
    Automatically checks order status after placement and provides detailed feedback.
    Exchange is automatically detected if not provided.

    Use this tool when the user wants to:
    - "Place order for NIFTY call option"
    - "Buy Bank Nifty futures"
    - "Sell put options"
    - "Trade derivatives"
    - "Buy SENSEX options"

    This tool automatically validates the symbol exists, checks margins, places order, and verifies status.
    """
    try:
        # First validate that the trading symbol exists and is an FnO instrument
        instruments_df = groww.get_all_instruments()
        
        # Try to find the instrument, auto-detecting exchange if needed
        if exchange is None:
            # Try to find the instrument on both exchanges
            matching_instrument = instruments_df[
                (instruments_df["trading_symbol"] == trading_symbol)
                & (instruments_df["segment"] == "FNO")
            ]
            if not matching_instrument.empty:
                # Use the exchange where the instrument is found
                exchange = matching_instrument.iloc[0]["exchange"]
            else:
                # Default to NSE if no match found
                exchange = "NSE"
        
        matching_instrument = instruments_df[
            (instruments_df["trading_symbol"] == trading_symbol)
            & (instruments_df["segment"] == "FNO")
            & (instruments_df["exchange"] == exchange)
        ]

        # If no match found, try the other exchange
        if matching_instrument.empty:
            alternative_exchange = "BSE" if exchange == "NSE" else "NSE"
            matching_instrument = instruments_df[
                (instruments_df["trading_symbol"] == trading_symbol)
                & (instruments_df["segment"] == "FNO")
                & (instruments_df["exchange"] == alternative_exchange)
            ]
            if not matching_instrument.empty:
                exchange = alternative_exchange

        if matching_instrument.empty:
            return {
                "status": "error",
                "success": False,
                "error_type": "symbol_not_found",
                "message": f"❌ FnO trading symbol '{trading_symbol}' not found on {exchange}",
                "failure_reason": f"Invalid trading symbol: {trading_symbol}",
                "trading_symbol": trading_symbol,
                "suggestion": "Use build_option_symbol or build_future_symbol tools to find correct symbol",
            }

        instrument_data = matching_instrument.iloc[0]

        # Check margin requirement before placing order
        try:
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

            if price:
                order_details[0]["price"] = price

            margin_response = groww.get_order_margin_details(
                segment="FNO", orders=order_details
            )

            margin_required = margin_response.get("total_requirement", 0)

        except Exception as margin_error:
            # Continue with order placement even if margin check fails
            margin_required = "Could not calculate"
            margin_response = {"error": str(margin_error)}

        # Place the FnO order
        order_response = groww.place_order(
            trading_symbol=trading_symbol,
            quantity=quantity,
            transaction_type=transaction_type,
            order_type=order_type,
            price=price,
            product=product,
            validity="DAY",
            exchange=exchange,
            segment="FNO",
        )

        # Extract order ID from response
        order_id = order_response.get("groww_order_id") or order_response.get(
            "order_id"
        )

        # Check order status if order ID is available
        order_status_info = None
        if order_id:
            try:
                # Wait a brief moment for order to be processed
                import time

                time.sleep(1)

                # Get order status using the underlying API directly
                status_response = groww.get_order_status(order_id, "FNO")
                order_status_info = status_response

                # Analyze order status
                if isinstance(status_response, dict):
                    current_status = status_response.get("order_status", "UNKNOWN")
                    rejection_reason = status_response.get("rejection_reason", "")
                    executed_quantity = status_response.get("executed_quantity", 0)
                    pending_quantity = status_response.get("pending_quantity", quantity)

                    # Determine if order was successful, failed, or pending
                    if current_status in ["REJECTED", "CANCELLED"]:
                        order_outcome = "FAILED"
                        failure_reason = (
                            rejection_reason or "Order was rejected by exchange"
                        )
                    elif current_status in ["COMPLETE", "EXECUTED"]:
                        order_outcome = "SUCCESS"
                        failure_reason = None
                    elif current_status in ["OPEN", "TRIGGER_PENDING", "PENDING"]:
                        order_outcome = "PENDING"
                        failure_reason = None
                    else:
                        order_outcome = "UNKNOWN"
                        failure_reason = f"Unknown order status: {current_status}"
                else:
                    order_outcome = "STATUS_CHECK_FAILED"
                    failure_reason = "Could not retrieve order status"

            except Exception as status_error:
                order_outcome = "STATUS_CHECK_FAILED"
                failure_reason = f"Error checking order status: {str(status_error)}"
                order_status_info = {"error": str(status_error)}
        else:
            order_outcome = "NO_ORDER_ID"
            failure_reason = "No order ID received from broker"

        # Prepare comprehensive response
        result = {
            "status": "order_placed",
            "order_outcome": order_outcome,
            "order_response": order_response,
            "order_status_check": order_status_info,
            "instrument_details": {
                "trading_symbol": trading_symbol,
                "groww_symbol": instrument_data["groww_symbol"],
                "exchange": exchange,
                "segment": "FNO",
                "exchange_token": instrument_data.get("exchange_token", ""),
            },
            "order_details": {
                "trading_symbol": trading_symbol,
                "quantity": quantity,
                "transaction_type": transaction_type,
                "order_type": order_type,
                "price": price,
                "product": product,
                "exchange": exchange,
                "order_id": order_id,
            },
            "margin_info": {
                "margin_required": margin_required,
                "margin_details": margin_response,
            },
        }

        # Add outcome-specific information
        if order_outcome == "SUCCESS":
            result["message"] = (
                f"✅ FnO order placed and EXECUTED successfully for {trading_symbol}"
            )
            result["success"] = True
        elif order_outcome == "PENDING":
            result["message"] = (
                f"📋 FnO order placed successfully for {trading_symbol} and is PENDING execution"
            )
            result["success"] = True
        elif order_outcome == "FAILED":
            result["message"] = f"❌ FnO order placed but FAILED for {trading_symbol}"
            result["failure_reason"] = failure_reason
            result["success"] = False
        else:
            result["message"] = (
                f"⚠️ FnO order placed for {trading_symbol} but status verification failed"
            )
            result["failure_reason"] = failure_reason
            result["success"] = False

        return result

    except Exception as e:
        return {
            "status": "error",
            "success": False,
            "error_type": "order_placement_failed",
            "message": f"❌ Failed to place FnO order: {str(e)}",
            "failure_reason": str(e),
            "trading_symbol": trading_symbol,
            "order_details": {
                "quantity": quantity,
                "transaction_type": transaction_type,
                "order_type": order_type,
                "price": price,
                "product": product,
            },
            "order_outcome": "PLACEMENT_FAILED",
        }


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)
