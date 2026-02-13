import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from data_pipeline.fetch_data import fetch_silver_intraday
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from indicators.atr import calculate_atr
from strategy.decision_engine import generate_signal
from backtesting.simulator import run_backtest
from telegram_bot import send_telegram_message

# Prevent duplicate alerts
last_signal = None


async def signal_runner():
    global last_signal

    while True:
        try:
            print("Checking signal...")

            data = fetch_silver_intraday()

            if not isinstance(data, dict):

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

                current_signal = result["signal"]

                print("Current Signal:", current_signal)

                # Send only if new BUY/SELL signal
                # if current_signal in ["BUY", "SELL"] and current_signal != last_signal:

                if current_signal in ["BUY", "SELL"] and current_signal != last_signal:
                

                    stop = result.get("stop_loss")
                    target = result.get("target")

                    message = (
                        f"🚀 {current_signal} SIGNAL\n\n"
                        f"Price: {round(result['price'], 2)}\n"
                        f"Stop: {round(stop, 2) if stop else 'N/A'}\n"
                        f"Target: {round(target, 2) if target else 'N/A'}\n"
                        f"Trend Strength: {round(result['trend_strength'], 2)}"
                    )

                    send_telegram_message(message)
                    last_signal = current_signal


        except Exception as e:
            print("Background Error:", e)

        # Wait 5 minutes
        await asyncio.sleep(120)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting background signal runner...")
    task = asyncio.create_task(signal_runner())
    yield
    print("Stopping background signal runner...")
    task.cancel()


app = FastAPI(
    title="Silver AI Trading Engine",
    lifespan=lifespan
)


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

    return result


@app.get("/silver/backtest")
def backtest():
    data = fetch_silver_intraday()

    if isinstance(data, dict):
        return data

    result = run_backtest(data)
    return result
