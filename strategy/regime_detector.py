import pandas as pd


def detect_regime(data, ema9, ema21, atr_values, rsi_values):
    latest_price = data[-1]["close"]
    latest_ema9 = ema9[-1]
    latest_ema21 = ema21[-1]
    latest_atr = atr_values[-1]
    latest_rsi = rsi_values[-1]

    atr_series = pd.Series(atr_values)
    atr_mean = atr_series.tail(30).mean()

    # --- Volatility Ratio ---
    atr_ratio = latest_atr / atr_mean if atr_mean != 0 else 1

    # --- Trend Strength ---
    trend_strength = abs(latest_ema9 - latest_ema21) / latest_atr if latest_atr != 0 else 0


    # 🔴 HIGH VOLATILITY
    if atr_ratio > 1.5:
        return "HIGH_VOLATILITY"

    # 🟢 STRONG TREND UP
    if trend_strength > 1.0 and latest_ema9 > latest_ema21 and latest_rsi > 55:

        return "TRENDING_UP"

    # 🔴 STRONG TREND DOWN
    if trend_strength > 1.0 and latest_ema9 < latest_ema21 and latest_rsi < 45:
        return "TRENDING_DOWN"

    # 🟡 Otherwise
    return "RANGING"
