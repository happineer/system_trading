import re
from datetime import datetime


def convert_data(f, v):
    """
    open api 통신 데이터를 적절한 data type으로 변환해주는 함수
    :param f: str - field
    :param v: str - open api 의 문자열 데이터
    :return:
    """
    v = v.strip()
    if not bool(v):
        return 0

    if f in ["현재가", "거래량", "시가", "고가", "저가", "전일종가", "거래대금", "기준가", "매도호가", "매수호가",
             "매도1차호가", "매도2차호가", "매도3차호가", "매도4차호가", "매도5차호가",
             "매수1차호가", "매수2차호가", "매수3차호가", "매수4차호가", "매수5차호가",
             "상한가", "하한가", "예상체결가", ""]:
        if v[0] in ["+", "-"]:
            v = v[1:]
        return float(v)
    elif f in ["체결시간", "호가시간"]:
        if len(v) == 14:
            regexp = "(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})"
        elif len(v) == 6:
            regexp = "(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})"
        args = (int(n) for n in re.search(regexp, v).groups())
        return datetime(*args)
    elif f in ["일자"]:
        regexp = "(\d{4})(\d{2})(\d{2})"
        args = (int(n) for n in re.search(regexp, v).groups())
        return datetime(*args)
    elif f in ["종목코드"]:
        return v
    return v
