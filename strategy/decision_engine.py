def generate_signal(data, ema9, ema21, rsi_values, atr_values):
    latest_price = data[-1]["close"]
    prev_price = data[-2]["close"] if len(data) > 1 else latest_price

    latest_ema9 = ema9[-1]
    prev_ema9 = ema9[-2] if len(ema9) > 1 else latest_ema9

    latest_ema21 = ema21[-1]
    latest_atr = atr_values[-1]

    signal = "HOLD"
    stop_loss = None
    target = None

    if latest_atr == 0:
        return {"price": latest_price, "signal": "HOLD"}

    trend_strength = abs(latest_ema9 - latest_ema21) / latest_atr

    # ---- Bullish Trend Continuation ----
    if trend_strength > 0.3 and latest_ema9 > latest_ema21:

        # Pullback recovery condition
        distance_from_ema9 = abs(latest_price - latest_ema9) / latest_atr
        if distance_from_ema9 < 0.5 and latest_price > latest_ema9:
            signal = "BUY"
            stop_loss = latest_price - latest_atr
            target = latest_price + (2 * latest_atr)

    # ---- Bearish Trend Continuation ----
    elif trend_strength > 0.3 and latest_ema9 < latest_ema21:

        distance_from_ema9 = abs(latest_price - latest_ema9) / latest_atr
        if distance_from_ema9 < 0.5 and latest_price < latest_ema9:
            signal = "SELL"
            stop_loss = latest_price + latest_atr
            target = latest_price - (2 * latest_atr)

    return {
        "price": latest_price,
        "ema9": latest_ema9,
        "ema21": latest_ema21,
        "trend_strength": trend_strength,
        "signal": signal,
        "stop_loss": stop_loss,
        "target": target
    }
