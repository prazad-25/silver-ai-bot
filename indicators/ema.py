import pandas as pd

def calculate_ema(data, period=9):
    df = pd.DataFrame(data)
    df["ema"] = df["close"].ewm(span=period, adjust=False).mean()
    return df["ema"].tolist()
