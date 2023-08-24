# Func that open order
def open_order(df, i, max_trade_percent, binance_taker_fee):

    if df.at[i-1, "signal"] == "buy":
        # Calculate amount of spend on of buy order
        order_amount = round((df.at[i-1, "balance"] * max_trade_percent), 2)
        # Set order price
        df.at[i, "order_price"] = df.at[i-1, "close"]
        # Calculate coin quantity for order
        df.at[i, "qty_coin"] = round((order_amount / df.at[i, "order_price"]), 5)
        # Update balance after spend on buy order
        df.at[i, "balance"] = df.at[i-1, "balance"] - order_amount - \
                              (order_amount * binance_taker_fee)
        df.at[i, "order_amount"] = order_amount + (order_amount * binance_taker_fee)
        # Set signal to active
        df.at[i, "signal"] = "active"

    elif df.at[i-1, "signal"] == "sell":
        # Calculate amount of spend on of buy order
        order_amount = round((df.at[i-1, "balance"] * max_trade_percent), 2)
        # Set order price
        df.at[i, "order_price"] = df.at[i-1, "close"]
        # Calculate coin quantity for order
        df.at[i, "qty_coin"] = round((order_amount / df.at[i, "order_price"]), 5)
        # Update balance after spend on buy order
        df.at[i, "balance"] = df.at[i-1, "balance"] - order_amount - \
                              (order_amount * binance_taker_fee)
        df.at[i, "order_amount"] = order_amount + (order_amount * binance_taker_fee)
        # Set signal to active
        df.at[i, "signal"] = "active"

    elif df.at[i-1, "signal"] == "none" or df.at[i-1, "signal"] == "close_order":
        # Update balance after spend on buy order
        df.at[i, "balance"] = df.at[i-1, "balance"]
        # Set signal to active
        df.at[i, "signal"] = "none"
        print("Awaiting signal")

    else:
        print("Error in open_order()!")

    return df


# Func that close order
def close_order(df, i, binance_taker_fee, take_profit, stop_loss):

    # Set coin price
    current_price = df.at[i-1, "close"]
    # Set order price
    order_price = df.at[i-1, "order_price"]
    # Calculate amount of spend on open order
    open_order_spend = round(df.at[i-1, "order_amount"], 2)

    # Target profit price
    target_profit = (open_order_spend * (1 + take_profit)) / df.at[i-1, "qty_coin"]
    # Target loss price
    target_loss = (open_order_spend * (1 - stop_loss)) / df.at[i-1, "qty_coin"]

    if target_profit <= current_price:
        # Update balance after spend on buy order
        balance = df.at[i-1, "balance"] + (current_price * df.at[i-1, "qty_coin"])\
                  - ((current_price * df.at[i-1, "qty_coin"]) * binance_taker_fee)
        df.at[i, "balance"] = balance
        # Update coin quantity
        df.at[i, "qty_coin"] = 0
        # Update signal
        df.at[i, "signal"] = "close_order"

    elif target_loss >= current_price:
        # Update balance after spend on buy order
        balance = df.at[i - 1, "balance"] + (current_price * df.at[i - 1, "qty_coin"]) \
                  - ((current_price * df.at[i - 1, "qty_coin"]) * binance_taker_fee)
        df.at[i, "balance"] = balance
        # Update coin quantity
        df.at[i, "qty_coin"] = 0
        # Update signal
        df.at[i, "signal"] = "close_order"
    else:
        #print("Order active! awaiting profit or loss. Count line:", i,
        #      "target_profit:", target_profit, "<= current_price:", current_price)
        df.at[i, "qty_coin"] = df.at[i-1, "qty_coin"]
        df.at[i, "balance"] = df.at[i-1, "balance"]
        df.at[i, "order_price"] = df.at[i-1, "order_price"]
        df.at[i , "order_amount"] = df.at[i-1, "order_amount"]
        df.at[i, "signal"] = "active"

    return df


# Func that create signal base on signal from indicators
def signal(df):
    df = df.assign(signal="none")

    for i in range(1, len(df)):
        if df.at[i, "ema_signal"] == "buy" and df.at[i, "rsi_signal"] == "buy":
            df.at[i, "signal"] = "buy"
            i += 1

        elif df.at[i, "ema_signal"] == "sell" and df.at[i, "rsi_signal"] == "sell":
            df.at[i, "signal"] = "sell"
            i += 1

        else:
            df.at[i, "signal"] = "none"
            i += 1

    return df[["timestamp", "close", "signal"]]


# main function than start or stop orders base on signal
def strategy(df, max_trade_percent, binance_taker_fee, take_profit, stop_loss):

    for i in range(1, len(df)):
        if df.at[i-1, "signal"] == "buy":
            df.at[i, "balance"] = df.at[i - 1, "balance"]
            open_order(df, i, max_trade_percent, binance_taker_fee)
            i += 1
        elif df.at[i-1, "signal"] == "sell":
            df.at[i, "balance"] = df.at[i - 1, "balance"]
            open_order(df, i, max_trade_percent, binance_taker_fee)
            i += 1
        elif df.at[i-1, "signal"] == "active":
            df.at[i, "balance"] = df.at[i - 1, "balance"]
            close_order(df, i, binance_taker_fee, take_profit, stop_loss)
            i += 1
        elif df.at[i-1, "signal"] == "close_order":
            df.at[i, "balance"] = df.at[i - 1, "balance"]
            i += 1
        else:
            df.at[i, "balance"] = df.at[i - 1, "balance"]


    return df
