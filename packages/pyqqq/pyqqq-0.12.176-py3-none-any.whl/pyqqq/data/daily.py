import datetime
from typing import Dict, List, Optional, Union

import pandas as pd
import pytz

import pyqqq.config as c
from pyqqq.datatypes import DataExchange
from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.array import chunk
from pyqqq.utils.local_cache import DiskCacheManager
from pyqqq.utils.logger import get_logger

logger = get_logger(__name__)
dailyCache = DiskCacheManager("daily_cache")


@dailyCache.memoize()
def get_all_ohlcv_for_date(
    date: datetime.date,
    adjusted: bool = True,
    exchange: Union[str, DataExchange] = "KRX",
) -> pd.DataFrame:
    """
    주어진 날짜에 대한 모든 주식의 OHLCV(Open, High, Low, Close, Volume) 데이터를 조회합니다.

    이 함수는 특정 날짜에 대한 모든 주식의 시가, 고가, 저가, 종가 및 거래량 데이터를 API를 통해 요청하고,
    이를 pandas DataFrame 형태로 반환합니다. 반환된 DataFrame은 'code'를 인덱스로 사용합니다.

    KRX: 2018년 1월 1일 데이터 부터 조회 가능합니다.
    NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

    Args:
        date (datetime.date): 조회할 날짜.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        pd.DataFrame: OHLCV 데이터를 포함하는 DataFrame. 'code' 컬럼은 DataFrame의 인덱스로 설정됩니다.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (int): 시가.
        - high (int): 고가.
        - low (int): 저가.
        - close (int): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.
        - diff (int): 종가 대비 전일 종가의 차이.
        - diff_rate (float): 종가 대비 전일 종가의 변화율.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> ohlcv_data = get_all_ohlcv_for_date(datetime.date(2023, 5, 8))
        >>> print(ohlcv_data)
                    open   high    low  close  volume       value  diff  diff_rate
            code
            000020   8710   8790   8710   8770   39019   341233350    60       0.69
            000040   1052   1133   1047   1047  590401   632158688     8       0.77
            000050   7740   7870   7700   7750    1445    11211730    10       0.13
            000070  68300  68800  67400  67600   33358  2261622200  -800      -1.17
            000075  54800  54900  54800  54800     177     9702400  -100      -0.18
            ...
    """
    if isinstance(date, datetime.datetime):
        date = date.date()

    exchange = DataExchange.validate(exchange)
    url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/daily/all/{date}"
    r = send_request(
        "GET",
        url,
        params={
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        },
    )
    raise_for_status(r)

    data = r.json()

    cols = data["cols"]
    rows = data["rows"]

    if not rows:
        return pd.DataFrame()
    else:
        df = pd.DataFrame(rows, columns=cols)
        df = df.astype({"open": int, "high": int, "low": int, "close": int, "volume": int, "value": int, "diff": int, "diff_rate": float})
        df.drop(columns=["date"], inplace=True)
        df.set_index("code", inplace=True)

        return df


def get_ohlcv_by_codes_for_period(
    codes: List[str],
    start_date: datetime.date,
    end_date: Optional[datetime.date] = None,
    adjusted: bool = True,
    ascending: bool = False,
    exchange: Union[str, DataExchange] = "KRX",
) -> Dict[str, pd.DataFrame]:
    """
    지정된 코드 리스트와 기간에 대한 OHLCV 데이터를 조회합니다.

    이 함수는 하나 이상의 주식 코드와 시작 날짜, 선택적으로 종료 날짜를 지정하여 해당 기간 동안의 OHLCV 데이터를 API를 통해 요청합니다.
    반환된 데이터는 각 주식 코드별로 시가, 고가, 저가, 종가, 거래량을 포함하는 pandas DataFrame 객체들로 구성된 딕셔너리 형태로 제공됩니다.
    각 DataFrame은 해당 주식의 날짜를 기반으로 역순으로 정렬됩니다.

    KRX: 2018년 1월 1일 데이터 부터 조회 가능합니다.
    NXT: 2025년 3월 4일 데이터 부터 조회 가능합니다.

    Args:
        codes (List[str]): 조회할 주식 코드들의 리스트.
        start_date (datetime.date): 조회할 기간의 시작 날짜.
        end_date (Optional[datetime.date]): 조회할 기간의 종료 날짜. 지정하지 않으면 최근 거래일 까지 조회됩니다.
        adjusted (bool): 수정주가 여부. 기본값은 True.
        ascending (bool): 날짜 오름차순 여부. 기본값은 False.
        exchange (Union[str, DataExchange]): 거래소. 기본값은 KRX.

    Returns:
        dict: 주식 코드를 키로 하고, 해당 코드의 OHLCV 데이터를 포함하는 DataFrame을 값으로 하는 딕셔너리.

        DataFrame의 컬럼은 다음과 같습니다.

        - open (int): 시가.
        - high (int): 고가.
        - low (int): 저가.
        - close (int): 종가.
        - volume (int): 거래량.
        - value (int): 거래대금.
        - diff (int): 종가 대비 전일 종가의 차이.
        - diff_rate (float): 종가 대비 전일 종가의 변화율.

    Raises:
        HTTPError: API 요청이 실패했을 때 발생.

    Examples:
        >>> dfs = get_ohlcv_by_codes_for_period(['005930', '319640'], datetime.date(2024, 5, 7), datetime.date(2024, 5, 9))
        >>> print(dfs)
        {'319640':              open   high    low  close  volume      value  diff  diff_rate
                    date
                    2024-05-09  15380  15445  15365  15430   16200  249577480    -5      -0.03
                    2024-05-08  15445  15460  15365  15435    6419   99007660    -5      -0.03
                    2024-05-07  15355  15525  15355  15440   22318  345280470    85       0.55,
        '005930':              open   high    low  close    volume          value  diff  diff_rate
                    date
                    2024-05-09  81100  81500  79700  79700  18700919  1504404274500 -1600  -1.97
                    2024-05-08  80800  81400  80500  81300  12960682  1050108654400     0   0.00
                    2024-05-07  79600  81300  79400  81300  26238868  2112619288066  3700   4.77}
    """
    exchange = DataExchange.validate(exchange)
    tz = pytz.timezone("Asia/Seoul")
    chunks = chunk(codes, 20)
    result = {}

    for i, asset_codes in enumerate(chunks):
        url = f"{c.PYQQQ_API_URL}/domestic-stock/ohlcv/daily/series"
        params = {
            "codes": ",".join(asset_codes),
            "start_date": start_date,
            "adjusted": "true" if adjusted else "false",
            "current_date": datetime.date.today(),
            "exchange": exchange.value,
        }
        if end_date is not None:
            params["end_date"] = end_date

        r = send_request("GET", url, params=params)
        raise_for_status(r)

        data = r.json()
        cols = data["cols"]
        dataset = data["rows"]

        if not dataset:
            continue

        for code in dataset.keys():
            rows = dataset[code]
            for row in rows:
                dt = row[0]
                if dt[-1] == "Z":
                    dt = dt[:-1] + "+00:00"
                dt = datetime.datetime.fromisoformat(dt).astimezone(tz).replace(tzinfo=None)
                row[0] = dt

            rows.reverse()

            df = pd.DataFrame(rows, columns=cols)
            df = df.astype({"open": int, "high": int, "low": int, "close": int, "volume": int, "value": int, "diff": int, "diff_rate": float})
            df.set_index("date", inplace=True)
            df.sort_index(ascending=ascending, inplace=True)
            result[code] = df

    return result
