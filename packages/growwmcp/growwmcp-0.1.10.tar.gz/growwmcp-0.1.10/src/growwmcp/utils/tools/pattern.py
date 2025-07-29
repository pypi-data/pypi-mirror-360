import os
import time
from typing import Optional, Dict, List, Annotated, Literal, Union
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ..helper import groww_login
from ..pattern_helper import (
    is_engulfing,
    is_doji,
    is_hammer,
    is_shooting_star,
    is_marubozu,
    is_tweezer,
    is_momentum_candle,
    is_three_white_soldiers,
)
import pandas as pd

groww = groww_login()

mcp = FastMCP(
    name="Groww Historical Data MCP Server",
    instructions=f"A Groww MCP Server for analyzing candle patterns",
)


def get_patterns(df: pd.DataFrame) -> pd.DataFrame:
    # Initialize patterns list column
    df["patterns"] = ""

    # Pattern detection functions mapping
    pattern_functions = {
        "Engulfing": is_engulfing,
        "Doji": is_doji,
        "Hammer": is_hammer,
        "Shooting Star": is_shooting_star,
        "Marubozu": is_marubozu,
        "Tweezer": is_tweezer,
        "Momentum": is_momentum_candle,
        "Three White Soldiers": is_three_white_soldiers,
    }

    # Check each pattern for each row
    for i in range(len(df)):
        patterns_found = []

        # Get the data up to current row for pattern analysis
        current_data = df.iloc[: i + 1]

        # Check each pattern
        for pattern_name, pattern_func in pattern_functions.items():
            if pattern_func(current_data):
                patterns_found.append(pattern_name)

        # Join patterns with comma
        df.iloc[i, df.columns.get_loc("patterns")] = ", ".join(patterns_found)

    return df


@mcp.tool()
def get_historical_candlestick_patterns(
    trading_symbol: Annotated[
        str,
        Field(
            description="Trading Symbol of the instrument (e.g., 'RELIANCE', 'NIFTY')"
        ),
    ],
    start_time: Annotated[
        str,
        Field(
            description="Start time in YYYY-MM-DD HH:mm:ss format or epoch milliseconds"
        ),
    ],
    end_time: Annotated[
        str,
        Field(
            description="End time in YYYY-MM-DD HH:mm:ss format or epoch milliseconds"
        ),
    ],
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
    interval_in_minutes: Annotated[
        int,
        Field(
            description="Interval in minutes for candle data (1, 5, 10, 60, 240, 1440, 10080)"
        ),
    ] = 5,
) -> dict:
    """
    Get candle patterns on historical data of a given instrument for a given time range and interval.
    Disclaimer: The patterns might be dependent on  neighboring candles, so please add some offset candles to the start and end time. (3-4 candles before and after)

    Use this tool when the user asks about:
    - "Find candlestick patterns in RELIANCE"
    - "Show me bullish patterns from last week"
    - "Get 5-minute pattern analysis for NIFTY"
    - "Identify patterns in TCS chart"
    - "Show me candlestick formations"

    limitations in time-range and interval
    | Candle Interval | Max Duration per Request | Historical Data Available |
    | :--- | :--- | :--- |
    | **1 min** | 7 days | Last 3 months |
    | **5 min** | 15 days | Last 3 months |
    | **10 min** | 30 days | Last 3 months |
    | **1 hour (60 min)** | 150 days | Last 3 months |
    | **4 hours (240 min)**| 365 days | Last 3 months |
    | **1 day (1440 min)** | 1080 days (~3 years) | Full history |
    | **1 week (10080 min)**| No Limit | Full history |

    """
    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time,
        end_time=end_time,
        interval_in_minutes=interval_in_minutes,
    )

    df = pd.DataFrame(
        response["candles"],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], unit="s", utc=True)
        .dt.tz_convert("Asia/Kolkata")
        .dt.tz_localize(None)
    )
    df = get_patterns(df)
    response["candles"] = df.to_dict(orient="records")

    return response
