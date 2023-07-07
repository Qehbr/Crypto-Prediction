import pandas as pd
import requests
import datetime
import numpy as np
import sqlite3
import sys


def get_data(symbol):
    res = pd.DataFrame()
    # Binance API Endpoint URLs
    klines_url = "https://api.binance.com/api/v3/klines"
    # price_ticker_url = "https://api.binance.com/api/v3/ticker/price"
    # order_book_url = "https://api.binance.com/api/v3/depth"
    # circulating_supply_url = "https://api.binance.com/api/v3/ticker/24hr"

    # Trading Pair and Interval
    interval = "1d"

    # Start and End Dates
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=1)

    end_date = datetime.datetime.combine(end_date, datetime.time.min)
    start_date = datetime.datetime.combine(start_date, datetime.time.min)

    # Calculate the start and end timestamps for the current day
    start_timestamp = int(start_date.timestamp() * 1000)
    end_timestamp = int((end_date.timestamp()) * 1000)

    # Retrieve OHLC data for the current day
    klines_params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_timestamp,
        "endTime": end_timestamp,
        "limit": 1000
    }
    klines_response = requests.get(klines_url, params=klines_params)
    if klines_response.status_code == 200:
        klines_data = klines_response.json()

        open_times = np.array([datetime.datetime.fromtimestamp(k[0] / 1000).date() for k in klines_data])
        open_prices = np.array([float(k[1]) for k in klines_data])
        high_prices = np.array([float(k[2]) for k in klines_data])
        low_prices = np.array([float(k[3]) for k in klines_data])
        close_prices = np.array([float(k[4]) for k in klines_data])
        volumes = np.array([float(k[5]) for k in klines_data])
        qav = np.array([float(k[7]) for k in klines_data])
        number_of_trades = np.array([k[8] for k in klines_data])

        data = {
            'Open Time': open_times,
            'Open Price': open_prices,
            'High Price': high_prices,
            'Low Price': low_prices,
            'Close Price': close_prices,
            'Volume': volumes,
            'Quote Asset Volume': qav,
            'Number of Trades': number_of_trades,
        }

        res = pd.concat([res, pd.DataFrame(data)])

    return res


def update_all_data(coins):
    conn = sqlite3.connect('crypto.db')
    for coin in coins:
        output = get_data(coin)
        output.to_sql(coin, conn, if_exists='append', index=False)
