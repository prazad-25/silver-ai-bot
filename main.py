from fastapi import FastAPI
from data_pipeline.fetch_data import fetch_silver_intraday
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from strategy.decision_engine import generate_signal
from indicators.atr import calculate_atr
from backtesting.simulator import run_backtest
from telegram_bot import send_telegram_message


app = FastAPI(title="Silver AI Trading Engine")

@app.get("/")
def home():
    return {"message": "Silver AI Backend Running 🚀"}


@app.get("/silver/signal")
def silver_signal():
    data = fetch_silver_intraday()

    if isinstance(data, dict):
        return data

    ema_9 = calculate_ema(data, 9)
    ema_21 = calculate_ema(data, 21)
    rsi_14 = calculate_rsi(data, 14)
    atr_14 = calculate_atr(data, 14)

    result = generate_signal(
        data,
        ema_9,
        ema_21,
        rsi_14,
        atr_14
    )

    # 🔔 Send Telegram Alert only for BUY/SELL
    if result["signal"] in ["BUY", "SELL"]:
        message = (
            f"🚀 {result['signal']} SIGNAL\n\n"
            f"Price: {round(result['price'], 2)}\n"
            f"Stop: {round(result['stop_loss'], 2)}\n"
            f"Target: {round(result['target'], 2)}\n"
            f"Trend Strength: {round(result['trend_strength'], 2)}"
        )

        send_telegram_message(message)

    return result



@app.get("/silver/backtest")
def backtest():
    data = fetch_silver_intraday()

    if isinstance(data, dict):
        return data

    result = run_backtest(data)

    return result
