import datetime
import pyqqq.utils.market_schedule as market_schedule


def get_last_trading_day(date: datetime.date = None, exchange: str = "KRX") -> str:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    return market_schedule.get_last_trading_day(date, exchange).isoformat()


def get_next_trading_day(date: datetime.date = None, exchange: str = "KRX") -> str:
    if isinstance(date, str):
        try:
            date = datetime.date.fromisoformat(date)
        except AttributeError:
            raise TypeError("Invalid date format. Please use 'YYYY-MM-DD' format.")

    return market_schedule.get_next_trading_day(date, exchange).isoformat()
