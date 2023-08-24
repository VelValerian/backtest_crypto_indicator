import pandas as pd
import indicators
import exchange

# Data that you work with
file_path = None    # Write name of your csv file in project directory

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)

# Convert timestamp to datetime objects
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Remain id Dataframe only 2 column for work
df = df[["timestamp", "close"]]

# If you need work only with certain rows
# df = df.head(31)

# Inputs values
balance_start = 1000  # Initialize balance
max_trade_percent = 0.01  # Initialize % of balance that max amount for one trade
take_profit = 0.015  # Initialize % when we close the open trade to take profit
stop_loss = 0.005  # Initialize % when we close the open trade to take loss
rsi_period = 14
ema_period = 9
rsi_high = 55
rsi_low = 45
i = 0
binance_taker_fee = 0.0004

# # Indicators function
df_indicators = indicators.rsi(df, rsi_period, rsi_high, rsi_low)
df_indicators = indicators.ema(df_indicators, ema_period)
df = df_indicators[["timestamp", "close", "rsi_signal", "ema_signal"]]

# Function that check the indicators, if they are met expectations, makes decisions
signal = exchange.signal(df)

# Add a column in DataFrame with default value 0

signal = signal.assign(order_amount=0, order_price=0, qty_coin=0, balance=balance_start)
df = signal[["timestamp", "close", "signal", "order_amount", "order_price", "qty_coin", "balance"]]

# Function that check all conditions and open or close orders
strategy = exchange.strategy(df, max_trade_percent, binance_taker_fee, take_profit, stop_loss)

# print total results
balance = strategy.iloc[-1]["balance"]
profit = round((((balance - balance_start ) / balance_start) * 100), 2)
print(f"Total balance: {balance} \n"
      f"Profit: {profit}%")

# Save DataFrame to csv file
# file_name = "BTC2222.csv"
# file_path = Path('/home/vel/PycharmProjects/crypto_trade_indicator/', file_name)
# strategy.to_csv(file_path, index=False)
