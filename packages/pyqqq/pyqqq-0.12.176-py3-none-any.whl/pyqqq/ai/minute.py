import datetime
import pandas
from typing import Dict, List
import pyqqq.data.minutes as minutes


def get_all_minute_data(time: datetime.datetime, source: str = "ebest", adjusted: bool = False) -> pandas.DataFrame:
    if isinstance(time, str):
        try:
            time = datetime.datetime.fromisoformat(time)
        except AttributeError:
            raise TypeError("Invalid time format. Please use 'YYYY-MM-DDTHH:MM' format.")

    df = minutes.get_all_minute_data(time, source, adjusted)
    if df.empty:
        raise ValueError(f"No minute data found for {time}")

    return df


def get_all_day_data(
    date: datetime.date,
    codes: List[str] | str,
    period: datetime.timedelta = datetime.timedelta(minutes=1),
    source: str = "ebest",
    adjusted: bool = False,
    ascending: bool = True,
) -> Dict[str, pandas.DataFrame]:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    result = minutes.get_all_day_data(date, codes, period, source, adjusted, ascending)

    # Ensure the result is a dict
    if isinstance(result, pandas.DataFrame):
        # Single DataFrame -> Convert to dict with one key
        if isinstance(codes, str):
            codes = [codes]  # Handle single string case
        result = {codes[0]: result}

    if not result or all(df.empty for df in result.values()):
        raise ValueError(f"No minute data found for {date}")

    # Convert existing index to DatetimeIndex
    for code, df in result.items():
        if not isinstance(df.index, pandas.DatetimeIndex):
            df.index = pandas.to_datetime(df.index)

    return result
