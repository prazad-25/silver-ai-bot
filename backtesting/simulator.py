from strategy.decision_engine import generate_signal
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from indicators.atr import calculate_atr
from datetime import datetime


def run_backtest(data, initial_capital=10000):


    capital = initial_capital
    equity_curve = [capital]
    peak_equity = capital
    max_drawdown = 0
    losing_streak = 0
    max_losing_streak = 0

    open_trades = []
    trade_history = []

    # --- Daily Controls ---
    current_day = None
    daily_trades = 0
    daily_loss = 0

    ema9 = calculate_ema(data, 9)
    ema21 = calculate_ema(data, 21)
    rsi = calculate_rsi(data, 14)
    atr = calculate_atr(data, 14)

    max_concurrent_trades = 2
    risk_per_trade_pct = 0.004   # 0.5% risk per trade
    total_risk_cap_pct = 0.03

    for i in range(30, len(data)):

        # --- Daily Reset ---
        candle_time = datetime.fromisoformat(data[i]["datetime"].replace("Z", ""))
        day = candle_time.date()

        if current_day != day:
            current_day = day
            daily_trades = 0
            daily_loss = 0

        current_slice = data[:i+1]

        signal_data = generate_signal(
            current_slice,
            ema9[:i+1],
            ema21[:i+1],
            rsi[:i+1],
            atr[:i+1]
        )

        current_price = signal_data["price"]

        # =========================
        # ---- EXIT LOGIC ----
        # =========================
        for trade in open_trades[:]:

            if trade["type"] == "BUY":
                if current_price <= trade["stop"] or current_price >= trade["target"]:
                    pnl = (current_price - trade["entry"]) * trade["position_size"]

                    capital += pnl
                    trade_history.append(pnl)
                    equity_curve.append(capital)

                    daily_trades += 1
                    daily_loss += pnl

                    # Drawdown tracking
                    if capital > peak_equity:
                        peak_equity = capital

                    drawdown = (peak_equity - capital) / peak_equity
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

                    # Losing streak tracking
                    if pnl < 0:
                        losing_streak += 1
                        if losing_streak > max_losing_streak:
                            max_losing_streak = losing_streak
                    else:
                        losing_streak = 0

                    open_trades.remove(trade)

            elif trade["type"] == "SELL":
                if current_price >= trade["stop"] or current_price <= trade["target"]:
                    pnl = (trade["entry"] - current_price) * trade["position_size"]

                    capital += pnl
                    trade_history.append(pnl)
                    equity_curve.append(capital)

                    daily_trades += 1
                    daily_loss += pnl

                    # Drawdown tracking
                    if capital > peak_equity:
                        peak_equity = capital

                    drawdown = (peak_equity - capital) / peak_equity
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

                    # Losing streak tracking
                    if pnl < 0:
                        losing_streak += 1
                        if losing_streak > max_losing_streak:
                            max_losing_streak = losing_streak
                    else:
                        losing_streak = 0

                    open_trades.remove(trade)

        # =========================
        # ---- ENTRY LOGIC ----
        # =========================

        current_risk = sum(trade["risk_amount"] for trade in open_trades)

        if (
            signal_data["signal"] in ["BUY", "SELL"]
            and len(open_trades) < max_concurrent_trades
            and current_risk < (capital * total_risk_cap_pct)
            and daily_trades < 2
            and daily_loss > -0.015 * capital
        ):

            risk_amount = capital * risk_per_trade_pct
            stop_distance = abs(current_price - signal_data["stop_loss"])

            if stop_distance == 0:
                continue

            position_size = risk_amount / stop_distance

            trade = {
                "type": signal_data["signal"],
                "entry": current_price,
                "stop": signal_data["stop_loss"],
                "target": signal_data["target"],
                "position_size": position_size,
                "risk_amount": risk_amount
            }

            open_trades.append(trade)

    # =========================
    # ---- FINAL METRICS ----
    # =========================

    wins = [p for p in trade_history if p > 0]
    losses = [p for p in trade_history if p < 0]

    expectancy = (sum(trade_history) / len(trade_history)) if trade_history else 0

    return {
        "final_capital": capital,
        "total_trades": len(trade_history),
        "profit_loss": capital - initial_capital,
        "win_rate": (len(wins) / len(trade_history) * 100) if trade_history else 0,
        "average_win": sum(wins)/len(wins) if wins else 0,
        "average_loss": sum(losses)/len(losses) if losses else 0,
        "max_drawdown_percent": max_drawdown * 100,
        "max_losing_streak": max_losing_streak,
        "expectancy_per_trade": expectancy
    }
