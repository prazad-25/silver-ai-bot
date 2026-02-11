import yfinance as yf
import pandas as pd


def fetch_silver_intraday():
    ticker = "SI=F"

    data = yf.download(
        ticker,
        interval="5m",
        period="45d",
        progress=False,
        auto_adjust=False,
        group_by="column"
    )

    if data.empty:
        return {"error": "No data returned"}

    # If MultiIndex columns exist, flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    # Convert datetime column to string
    if "Datetime" in data.columns:
        data["Datetime"] = data["Datetime"].astype(str)
    elif "Date" in data.columns:
        data["Date"] = data["Date"].astype(str)

   # Keep only required columns
    data = data[["Datetime", "Open", "High", "Low", "Close", "Volume"]]

    records = data.to_dict(orient="records")


    clean_records = []
    for row in records:
        clean_row = {
            "datetime": row["Datetime"],
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"])
        }
        clean_records.append(clean_row)

    return clean_records
