import numpy as np
import pandas_ta as ta


# Calculate RSI
def rsi(df, rsi_period, rsi_high, rsi_low):
    df = df.assign(rsi_signal="none")
    df["rsi"] = round(ta.rsi(df["close"], length=rsi_period))

    for i in range(1, len(df)):
        if np.isnan(df.at[i, "rsi"]):
            df.at[i, "rsi_signal"] = "none"
            i += 1

        elif rsi_high >= df.at[i, "rsi"] >= rsi_low:
            df.at[i, "rsi_signal"] = "none"
            i += 1

        elif rsi_high < df.at[i, "rsi"]:
            df.at[i, "rsi_signal"] = "sell"
            i += 1
        elif rsi_low > df.at[i, "rsi"]:
            df.at[i, "rsi_signal"] = "buy"
            i += 1

    return df


# Calculate EMA
def ema(df, ema_period):
    df = df.assign(ema_signal="none")
    df['ema'] = round(df['close'].ewm(span=ema_period, adjust=False).mean())

    for i in range(1, len(df)):
        if df.at[i, "ema"] == df.at[i, "close"]:
            df.at[i, "ema_signal"] = "none"
            i += 1

        elif df.at[i, "ema"] > df.at[i, "close"]:
            df.at[i, "ema_signal"] = "sell"
            i += 1

        elif df.at[i, "ema"] < df.at[i, "close"]:
            df.at[i, "ema_signal"] = "buy"
            i += 1

    return df
