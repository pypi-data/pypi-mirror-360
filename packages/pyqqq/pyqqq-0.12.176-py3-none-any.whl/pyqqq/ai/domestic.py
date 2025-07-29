import datetime
import pandas
from typing import List, Optional
import pyqqq.data.domestic as domestic


def get_tickers(date: Optional[datetime.date] = None, market: Optional[str] = None) -> pandas.DataFrame:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    df = domestic.get_tickers(date, market)
    if df.empty:
        if date:
            raise ValueError(f"No tickers found for {date}")
        else:
            raise ValueError("No tickers found")

    return df


def get_market_cap(date: datetime.date = None) -> pandas.DataFrame:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    df = domestic.get_market_cap(date)
    if df.empty:
        if date:
            raise ValueError(f"No market cap data found for {date}")
        else:
            raise ValueError("No market cap data found")

    df.rename(columns={"value": "market_cap", "shares": "outstanding_shares"}, inplace=True)
    return df


def get_market_cap_by_codes(codes: List[str], date: datetime.date = None) -> pandas.DataFrame:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    df = domestic.get_market_cap_by_codes(codes, date)
    if df.empty:
        if date:
            raise ValueError(f"No market cap data found for {date}")
        else:
            raise ValueError("No market cap data found")

    df.rename(columns={"value": "market_cap", "shares": "outstanding_shares"}, inplace=True)
    return df
