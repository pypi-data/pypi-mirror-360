import datetime
import pandas
from typing import Dict, List, Optional
import pyqqq.data.daily as daily


def get_all_ohlcv_for_date(date: datetime.date, adjusted: bool = False) -> pandas.DataFrame:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    df = daily.get_all_ohlcv_for_date(date, adjusted)
    if df.empty:
        raise ValueError(f"No OHLCV data found for {date}")

    return df


def get_ohlcv_by_codes_for_period(
    codes: List[str],
    start_date: datetime.date,
    end_date: Optional[datetime.date] = None,
    adjusted: bool = False,
    ascending: bool = False,
) -> Dict[str, pandas.DataFrame]:
    if isinstance(start_date, str):
        try:
            start_date = datetime.date.fromisoformat(start_date)
        except AttributeError:
            raise TypeError("Invalid start_date format. Please use 'YYYY-MM-DD' format.")
    if isinstance(end_date, str):
        try:
            end_date = datetime.date.fromisoformat(end_date)
        except AttributeError:
            raise TypeError("Invalid end_date format. Please use 'YYYY-MM-DD' format.")

    dict = daily.get_ohlcv_by_codes_for_period(codes, start_date, end_date, adjusted, ascending)
    if not dict:
        if end_date:
            raise ValueError(f"No OHLCV data found for {start_date} to {end_date}")
        else:
            raise ValueError(f"No OHLCV data found for {start_date}")

    return dict
