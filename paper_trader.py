import time
import csv
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/silver/signal"

capital = 10000
risk_per_trade_pct = 0.004  # 0.4% risk (same as backtest)
open_trade = None

log_file = "paper_trades.csv"


def log_trade(trade_data):
    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(trade_data)


print("🚀 Paper Trader Started")
print("Initial Capital:", capital)

while True:
    try:
        response = requests.get(BASE_URL)
        data = response.json()

        price = data["price"]
        signal = data["signal"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Price: {price} | Signal: {signal}")

        stop = data["stop_loss"]
        target = data["target"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ======================
        # CHECK EXIT
        # ======================
        if open_trade:

            if open_trade["type"] == "BUY":
                if price <= open_trade["stop"] or price >= open_trade["target"]:
                    pnl = (price - open_trade["entry"]) * open_trade["size"]
                    capital += pnl

                    print(f"[{now}] CLOSED BUY | PnL: {round(pnl,2)} | Capital: {round(capital,2)}")

                    log_trade([now, "CLOSE BUY", open_trade["entry"], price, pnl, capital])

                    open_trade = None

            elif open_trade["type"] == "SELL":
                if price >= open_trade["stop"] or price <= open_trade["target"]:
                    pnl = (open_trade["entry"] - price) * open_trade["size"]
                    capital += pnl

                    print(f"[{now}] CLOSED SELL | PnL: {round(pnl,2)} | Capital: {round(capital,2)}")

                    log_trade([now, "CLOSE SELL", open_trade["entry"], price, pnl, capital])

                    open_trade = None

        # ======================
        # CHECK ENTRY
        # ======================
        if not open_trade and signal in ["BUY", "SELL"]:

            risk_amount = capital * risk_per_trade_pct
            stop_distance = abs(price - stop)

            if stop_distance == 0:
                continue

            position_size = risk_amount / stop_distance

            open_trade = {
                "type": signal,
                "entry": price,
                "stop": stop,
                "target": target,
                "size": position_size
            }

            print(f"[{now}] OPEN {signal} at {price}")

            log_trade([now, f"OPEN {signal}", price, "-", "-", capital])

        time.sleep(300)  # Wait 5 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
