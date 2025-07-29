import pandas as pd


def is_engulfing(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    c1 = df.iloc[-1]
    c0 = df.iloc[-2]
    c1_is_bullish = c1["close"] > c1["open"]
    c0_is_bearish = c0["close"] < c0["open"]
    c1_is_bearish = c1["close"] < c1["open"]
    c0_is_bullish = c0["close"] > c0["open"]

    is_bullish_engulfing = (
        c1_is_bullish
        and c0_is_bearish
        and c1["close"] > c0["open"]
        and c1["open"] < c0["close"]
    )

    is_bearish_engulfing = (
        c1_is_bearish
        and c0_is_bullish
        and c1["open"] > c0["close"]
        and c1["close"] < c0["open"]
    )

    return is_bullish_engulfing or is_bearish_engulfing


def is_momentum_candle(df: pd.DataFrame) -> bool:
    if len(df) < 1:
        return False
    c = df.iloc[-1]
    body = abs(c["close"] - c["open"])
    candle_range = c["high"] - c["low"]
    return candle_range > 0 and body / candle_range > 0.7


def is_three_white_soldiers(df: pd.DataFrame) -> bool:
    if len(df) < 3:
        return False
    c2, c1, c0 = df.iloc[-3], df.iloc[-2], df.iloc[-1]

    cond1 = (
        c0["close"] > c0["open"]
        and c1["close"] > c1["open"]
        and c2["close"] > c2["open"]
    )

    cond2 = c0["close"] > c1["close"] and c1["close"] > c2["close"]

    cond3 = (
        c0["open"] > c1["open"]
        and c0["open"] < c1["close"]
        and c1["open"] > c2["open"]
        and c1["open"] < c2["close"]
    )

    return cond1 and cond2 and cond3


def is_doji(df: pd.DataFrame) -> bool:
    if len(df) < 1:
        return False
    c = df.iloc[-1]
    body = abs(c["close"] - c["open"])
    candle_range = c["high"] - c["low"]
    return candle_range > 0 and body / candle_range < 0.05


def is_hammer(df: pd.DataFrame) -> bool:
    if len(df) < 1:
        return False
    c = df.iloc[-1]
    body = abs(c["close"] - c["open"])
    lower_wick = min(c["open"], c["close"]) - c["low"]
    upper_wick = c["high"] - max(c["open"], c["close"])
    return body > 0 and lower_wick >= 2 * body and upper_wick < body


def is_shooting_star(df: pd.DataFrame) -> bool:
    if len(df) < 1:
        return False
    c = df.iloc[-1]
    body = abs(c["close"] - c["open"])
    upper_wick = c["high"] - max(c["open"], c["close"])
    lower_wick = min(c["open"], c["close"]) - c["low"]
    return body > 0 and upper_wick >= 2 * body and lower_wick < body


def is_tweezer(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    c1 = df.iloc[-1]
    c0 = df.iloc[-2]

    tweezer_top = (
        c0["close"] > c0["open"]
        and c1["close"] < c1["open"]
        and abs(c0["high"] - c1["high"]) / c0["high"] < 0.005
    )

    tweezer_bottom = (
        c0["close"] < c0["open"]
        and c1["close"] > c1["open"]
        and abs(c0["low"] - c1["low"]) / c0["low"] < 0.005
    )

    return tweezer_top or tweezer_bottom


def is_marubozu(df: pd.DataFrame) -> bool:
    if len(df) < 1:
        return False
    c = df.iloc[-1]
    body = abs(c["close"] - c["open"])
    candle_range = c["high"] - c["low"]
    return candle_range > 0 and body / candle_range > 0.98
