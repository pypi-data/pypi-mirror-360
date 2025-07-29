import os
import time
from typing import Optional, Dict, List, Annotated, Literal, Union
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from growwapi import GrowwAPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from ..helper import groww_login
import pandas as pd

groww = groww_login()

mcp = FastMCP(
    name="Groww Historical Data MCP Server",
    instructions=f"A Groww MCP Server for fetching historical market data including candle data with various time intervals",
)

# =============================================================================
# HISTORICAL DATA MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def get_historical_candle_data(
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
    Fetch historical candle data for an instrument with specified time range and interval.

    Use this tool when the user asks about:
    - "Get historical data for RELIANCE"
    - "Show me candle data for last week"
    - "Get 5-minute candles for NIFTY"
    - "Historical price data for TCS"
    - "Show me OHLC history"
    - "Get past trading data"
    - "Historical chart data"
    - "Price history with volume"

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
    response["candles"] = df.to_dict(orient="records")

    return response


@mcp.tool()
def get_daily_historical_data(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    days: Annotated[
        int, Field(description="Number of days of historical data to fetch")
    ] = 30,
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get daily historical candle data for a specified number of days.

    Use this tool when the user asks about:
    - "Get last 30 days data for RELIANCE"
    - "Show me daily candles for past month"
    - "Historical daily data for NIFTY"
    - "Get daily OHLC for last 60 days"
    - "Show me daily price history"
    - "Past month's trading data"

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
    # Calculate start and end times
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    # Format times as required by API
    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time_str,
        end_time=end_time_str,
        interval_in_minutes=1440,  # Daily candles
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
    response["candles"] = df.to_dict(orient="records")

    return response


@mcp.tool()
def get_intraday_historical_data(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    interval_minutes: Annotated[
        Literal["1", "5", "10", "60"], Field(description="Intraday interval in minutes")
    ] = "5",
    days: Annotated[int, Field(description="Number of days back to fetch data")] = 1,
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get intraday historical data with specified minute intervals.

    Use this tool when the user asks about:
    - "Get 5-minute candles for today"
    - "Show me hourly data for RELIANCE"
    - "Intraday 1-minute data for NIFTY"
    - "Get 10-minute intervals for last 3 days"
    - "Show me intraday price movements"
    - "Minute-by-minute data"

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
    # Calculate appropriate time range based on interval limits
    interval_minutes = int(interval_minutes)
    max_days = {1: 3, 5: 15, 10: 30, 60: 150}
    actual_days = min(days, max_days.get(interval_minutes, 3))

    end_time = datetime.now()
    start_time = end_time - timedelta(days=actual_days)

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time_str,
        end_time=end_time_str,
        interval_in_minutes=interval_minutes,
    )

    # Add metadata about limits
    response["metadata"] = {
        "requested_days": days,
        "actual_days": actual_days,
        "interval_minutes": interval_minutes,
        "max_days_for_interval": max_days.get(interval_minutes, 3),
    }

    df = pd.DataFrame(
        response["candles"],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], unit="s", utc=True)
        .dt.tz_convert("Asia/Kolkata")
        .dt.tz_localize(None)
    )
    response["candles"] = df.to_dict(orient="records")

    return response


@mcp.tool()
def get_weekly_historical_data(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    weeks: Annotated[
        int, Field(description="Number of weeks of historical data to fetch")
    ] = 12,
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get weekly historical candle data for specified number of weeks.

    Use this tool when the user asks about:
    - "Get weekly data for RELIANCE"
    - "Show me weekly candles for past 3 months"
    - "Weekly OHLC data for NIFTY"
    - "Get weekly price history"
    - "Show me weekly trading patterns"

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
    end_time = datetime.now()
    start_time = end_time - timedelta(weeks=weeks)

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time_str,
        end_time=end_time_str,
        interval_in_minutes=10080,  # Weekly candles
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
    response["candles"] = df.to_dict(orient="records")
    return response


@mcp.tool()
def get_custom_timeframe_data(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    start_date: Annotated[str, Field(description="Start date in YYYY-MM-DD format")],
    end_date: Annotated[str, Field(description="End date in YYYY-MM-DD format")],
    interval_minutes: Annotated[
        Literal["1", "5", "10", "60", "240", "1440", "10080"],
        Field(description="Interval in minutes"),
    ] = "1440",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get historical data for a custom date range with specified interval.

    Use this tool when the user asks about:
    - "Get data from Jan 1 to Jan 31"
    - "Show me data between specific dates"
    - "Historical data for custom period"
    - "Get data from last month"
    - "Show me data for specific date range"

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
    # Convert dates to datetime format
    start_time_str = f"{start_date} 09:15:00"
    end_time_str = f"{end_date} 15:30:00"

    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time_str,
        end_time=end_time_str,
        interval_in_minutes=interval_minutes,
    )

    # Add validation info
    response["request_info"] = {
        "start_date": start_date,
        "end_date": end_date,
        "interval_minutes": interval_minutes,
        "trading_symbol": trading_symbol,
    }

    df = pd.DataFrame(
        response["candles"],
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], unit="s", utc=True)
        .dt.tz_convert("Asia/Kolkata")
        .dt.tz_localize(None)
    )
    response["candles"] = df.to_dict(orient="records")

    return response


@mcp.tool()
def get_multiple_instruments_historical_data(
    instruments: Annotated[
        List[Dict],
        Field(description="List of instrument details to get historical data for"),
    ],
    days: Annotated[int, Field(description="Number of days of historical data")] = 7,
    interval_minutes: Annotated[int, Field(description="Interval in minutes")] = 1440,
) -> dict:
    """
    Get historical data for multiple instruments at once.

    Each instrument in the list should contain:
    - trading_symbol: Trading symbol (e.g., 'RELIANCE', 'NIFTY')
    - exchange: 'NSE' or 'BSE' (optional, defaults to 'NSE')
    - segment: 'CASH' or 'FNO' (optional, defaults to 'CASH')

    Use this tool when the user asks about:
    - "Get historical data for multiple stocks"
    - "Compare historical performance"
    - "Show me data for my watchlist"
    - "Historical data for basket of stocks"

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
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    historical_data = {}

    for instrument in instruments:
        try:
            trading_symbol = instrument.get("trading_symbol")
            exchange = instrument.get("exchange", "NSE")
            segment = instrument.get("segment", "CASH")

            if trading_symbol:
                data = groww.get_historical_candle_data(
                    trading_symbol=trading_symbol,
                    exchange=exchange,
                    segment=segment,
                    start_time=start_time_str,
                    end_time=end_time_str,
                    interval_in_minutes=interval_minutes,
                )
                df = pd.DataFrame(
                    data["candles"],
                    columns=["timestamp", "open", "high", "low", "close", "volume"],
                )
                df["timestamp"] = (
                    pd.to_datetime(df["timestamp"], unit="s", utc=True)
                    .dt.tz_convert("Asia/Kolkata")
                    .dt.tz_localize(None)
                )
                data["candles"] = df.to_dict(orient="records")
                historical_data[f"{exchange}_{trading_symbol}"] = data

        except Exception as e:
            historical_data[
                f"{instrument.get('exchange', 'NSE')}_{instrument.get('trading_symbol', 'UNKNOWN')}"
            ] = {"error": str(e)}

    return {
        "historical_data": historical_data,
        "request_params": {
            "days": days,
            "interval_minutes": interval_minutes,
            "start_time": start_time_str,
            "end_time": end_time_str,
        },
    }


@mcp.tool()
def get_price_analysis_from_history(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    days: Annotated[int, Field(description="Number of days to analyze")] = 30,
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get historical data with basic price analysis including highs, lows, and averages.

    Use this tool when the user asks about:
    - "Analyze price trends for RELIANCE"
    - "Get price statistics from history"
    - "Show me price analysis"
    - "Historical price trends"
    - "Price performance analysis"
    - "Get highs and lows from history"

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
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        historical_data = groww.get_historical_candle_data(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time_str,
            end_time=end_time_str,
            interval_in_minutes=1440,  # Daily data for analysis
        )

        candles = historical_data.get("candles", [])

        if not candles:
            return {
                "error": "No historical data available",
                "symbol": f"{exchange}_{trading_symbol}",
            }

        # Extract price data for analysis
        opens = [candle[1] for candle in candles]
        highs = [candle[2] for candle in candles]
        lows = [candle[3] for candle in candles]
        closes = [candle[4] for candle in candles]
        volumes = [candle[5] for candle in candles]

        # Calculate statistics
        analysis = {
            "symbol": f"{exchange}_{trading_symbol}",
            "period_days": days,
            "total_candles": len(candles),
            "price_statistics": {
                "highest_price": max(highs),
                "lowest_price": min(lows),
                "average_close": sum(closes) / len(closes),
                "first_close": closes[0] if closes else 0,
                "last_close": closes[-1] if closes else 0,
                "price_change": closes[-1] - closes[0] if len(closes) > 1 else 0,
                "price_change_percent": (
                    ((closes[-1] - closes[0]) / closes[0] * 100)
                    if len(closes) > 1 and closes[0] > 0
                    else 0
                ),
            },
            "volume_statistics": {
                "total_volume": sum(volumes),
                "average_volume": sum(volumes) / len(volumes),
                "max_volume": max(volumes),
                "min_volume": min(volumes),
            },
            "raw_data": historical_data,
        }

        return analysis

    except Exception as e:
        return {
            "error": str(e),
            "symbol": f"{exchange}_{trading_symbol}",
            "period_days": days,
        }


@mcp.tool()
def get_historical_data_with_epoch_time(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    start_time_epoch: Annotated[
        int, Field(description="Start time in epoch milliseconds")
    ],
    end_time_epoch: Annotated[int, Field(description="End time in epoch milliseconds")],
    interval_minutes: Annotated[int, Field(description="Interval in minutes")] = 5,
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get historical data using epoch timestamps for precise time control.

    Use this tool when the user asks about:
    - "Get data using epoch time"
    - "Historical data with precise timestamps"
    - "Get data using millisecond timestamps"
    - "Fetch data with exact time range"

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
        start_time=str(start_time_epoch),
        end_time=str(end_time_epoch),
        interval_in_minutes=interval_minutes,
    )

    # Add epoch time info
    response["epoch_time_info"] = {
        "start_time_epoch": start_time_epoch,
        "end_time_epoch": end_time_epoch,
        "start_time_readable": datetime.fromtimestamp(start_time_epoch / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "end_time_readable": datetime.fromtimestamp(end_time_epoch / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    return response


@mcp.tool()
def get_recent_historical_data(
    trading_symbol: Annotated[
        str, Field(description="Trading Symbol of the instrument")
    ],
    hours: Annotated[int, Field(description="Number of hours back to fetch data")] = 24,
    interval_minutes: Annotated[
        Literal["1", "5", "10", "60"], Field(description="Interval in minutes")
    ] = "5",
    exchange: Annotated[
        Literal["NSE", "BSE"], Field(description="Stock exchange")
    ] = "NSE",
    segment: Annotated[
        Literal["CASH", "FNO"], Field(description="Market segment")
    ] = "CASH",
) -> dict:
    """
    Get recent historical data for the last few hours with minute-level precision.

    Use this tool when the user asks about:
    - "Get data for last 24 hours"
    - "Show me recent price movements"
    - "Get today's trading data"
    - "Recent historical candles"
    - "Last few hours data"

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
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)

    start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    response = groww.get_historical_candle_data(
        trading_symbol=trading_symbol,
        exchange=exchange,
        segment=segment,
        start_time=start_time_str,
        end_time=end_time_str,
        interval_in_minutes=interval_minutes,
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
    response["candles"] = df.to_dict(orient="records")

    response["request_info"] = {
        "hours_back": hours,
        "interval_minutes": interval_minutes,
        "start_time": start_time_str,
        "end_time": end_time_str,
    }

    return response


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8894)
