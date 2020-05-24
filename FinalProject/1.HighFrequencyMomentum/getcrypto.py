"""
IEOR E4729 MODEL-BASED TRADING: THEORY AND PRACTICE ASSIGNMENT Final Project

Get the data of the hourly prices of cryptocurrencies versus the US Dollar from cryptocompare.com

Author: Weihang Ren
April 22nd, 2020

"""

import requests
import pandas as pd
from datetime import datetime, timezone

apiKey = "0a233b8ee245c8a7fb1cb4c4ac59ec1bcdbf475e0dca450a964fad8744a364fa"


def unix(time):
    """
    Convert datetime (UTC) to unix time.
    
    """
    dt = datetime.strptime(time,"%Y-%m-%d %H:%M")
    unix_time = dt.replace(tzinfo=timezone.utc).timestamp()
    
    return unix_time


def get_unit(symbol, to_date, to_symbol="USD", frequency="hour"):
    """
    Get 2000 rows of OHLCV from the daily/hourly/minute historical data.
    frequency = "day" / "hour" / "minute"

    """
    
    url = f"https://min-api.cryptocompare.com/data/histo{frequency}"

    payload = {
        "api_key": apiKey,
        "fsym": symbol,
        "tsym": to_symbol,
        "limit": 2000,
        "toTs": to_date
    }

    result = requests.get(url, params=payload).json()

    df = pd.DataFrame(result['Data'])

    return df


def get_historical(symbol, from_date, to_date):
    """
    Get historical data of a symbol between specified dates.

    """
    container = []
    
    while to_date > from_date:
        unit_data = get_unit(symbol, to_date)
        container.append(unit_data)
        to_date = unit_data['time'][0]

    df = pd.concat(container, axis=0)
    # Remove data points from before from_date
    df = df[df['time'] > from_date].drop_duplicates()
    # Convert to timestamp to readable date format
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # Make the DataFrame index the time
    df.set_index('time', inplace=True)
    # And sort it so its in time order
    df.sort_index(ascending=True, inplace=True)

    return df


def get_panel(symbol_list, from_date, to_date, idx=True):
    """
    Get close prices for all symbols in the list.

    """
    container = []
    
    to_date = unix(to_date)
    from_date = unix(from_date)

    for symbol in symbol_list:
        symbol_data = get_historical(symbol, from_date, to_date)
        container.append(symbol_data['close'])

    df = pd.concat(container, axis=1)
    # rename columns by symbol
    df.columns = symbol_list
    # change index to hour
    if idx:
        df = df.reset_index(drop=True)

    return df

