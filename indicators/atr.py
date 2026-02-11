import pandas as pd


def calculate_atr(data, period=14):
    df = pd.DataFrame(data)

    df["previous_close"] = df["close"].shift(1)

    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = abs(df["high"] - df["previous_close"])
    df["tr3"] = abs(df["low"] - df["previous_close"])

    df["true_range"] = df[["tr1", "tr2", "tr3"]].max(axis=1)

    atr = df["true_range"].rolling(window=period).mean()

    return atr.tolist()
