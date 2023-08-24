import numpy as np
import pandas_ta as ta

# ------------------------------------------Momentum indicators------------------------------------------

# Calculate RSI------------------------------------------------------------------------------------
def rsi(df, rsi_period, rsi_high, rsi_low):
    df = df.assign(rsi_signal="none")
    df["rsi"] = round(ta.rsi(df["close"], length=rsi_period))

    # Signal
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

# Calculate MACD------------------------------------------------------------------------------------
def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

def macd(df, fast_window, slow_window, signal_window):
    # Args:
    #         data (pd.Series): Series of 'close's
    #         fast (int): The short period. Default: 12
    #         slow (int): The long period. Default: 26
    #         signal (int): The signal period. Default: 9
    #         talib (bool): If TA Lib is installed and talib is True, Returns the TA Lib
    #             version. Default: True
    #         offset (int): How many periods to offset the result. Default: 0

    df = df.assign(macd_signal="none")
    # Calculate the MACD line (difference between fast and slow EMAs)
    df['macd_line'] = calculate_ema(df['close'], fast_window) - calculate_ema(df['close'], slow_window)

    # Calculate the signal line (EMA of the MACD line)
    df['macd_signal_line'] = calculate_ema(df['macd_line'], signal_window)

    # The histogram is the difference between the MACD Line and the Signal Line.
    # It visually represents the distance between the MACD and its Signal Line.
    df['histogram'] = df['macd_line'] - df['macd_signal_line']

    # MACD Line and Signal Line Crosses: When the MACD Line crosses above the Signal Line,
    # it may be a bullish signal indicating the potential for an upward trend.
    # Conversely, when the MACD Line crosses below the Signal Line,
    # it may be a bearish signal indicating a potential downward trend.
    for i in range(1, len(df)):
        if df.at[i, 'macd_line'] > df.at[i, 'macd_signal_line']:
            df.at[i, 'line_to_signal'] = 'buy'
            i += 1
        else:
            df.at[i, 'line_to_signal'] = 'sell'
            i += 1
    # Zero Line Crosses: When the MACD Line crosses above the zero line,
    # it suggests potential bullish momentum.
    # When it crosses below the zero line, it suggests potential bearish momentum.
    for i in range(1, len(df)):
        if df.at[i, 'macd_line'] > 0:
            df.at[i, 'line_position'] = 'buy'
            i += 1
        else:
            df.at[i, 'line_position'] = 'sell'
            i += 1
    # Histogram Contraction and Expansion: A histogram that contracts suggests that the trend might be losing momentum.
    # Conversely, a histogram that expands indicates increasing momentum.
    for i in range(2, len(df)):
        if df.at[i, 'histogram'] > df.at[i-1, 'histogram']:
            if df.at[i, 'histogram'] > df.at[i-2, 'histogram']:
                df.at[i, 'histogram_moving_average'] = "up"
                i += 1
            else:
                df.at[i, 'histogram_moving_average'] = "change"
                i += 1
        elif df.at[i, 'histogram'] < df.at[i - 1, 'histogram']:
            if df.at[i, 'histogram'] < df.at[i - 2, 'histogram']:
                df.at[i, 'histogram_moving_average'] = "down"
                i += 1
            else:
                df.at[i, 'histogram_moving_average'] = "change"
                i += 1

    # Signal
    for i in range(2, len(df)):
        if df.at[i, 'line_to_signal'] == df.at[i, 'line_position']:

            df.at[i, 'macd_signal'] = df.at[i, 'line_to_signal']
            i += 1

    return df

# ------------------------------------------Overlap indicators------------------------------------------

# Calculate EMA------------------------------------------------------------------------------------
def ema(df, ema_period):
    df = df.assign(ema_signal="none")
    df['ema'] = round(df['close'].ewm(span=ema_period, adjust=False).mean())

    # Signal
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

