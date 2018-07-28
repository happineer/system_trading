from datetime import datetime


def get_time_str(format="YYMMDD-HHMMSS"):
    """시간 포맷 문자열에 해당하는 실제 날짜 문자열을 생성하여 반환합니다.

    :param format:
    :return:
    """
    if format == "YYMMDD":
        t = datetime.today().strftime("%y%m%d")
    elif format == "YYYYMMDD":
        t = datetime.today().strftime("%Y%m%d")
    elif format == "YYMMDD-HHMMSS":
        t = datetime.today().strftime("%y%m%d-%H%M%S")
    else:
        t = datetime.today().strftime("%y%m%d-%H%M%S")
    return t

def get_datetime(format="YYMMDD"):
    """시간포맷 문자열로부터 datetime 객체를 생성하여 반환합니다.

        need to implement..

    :param format:
    :return:
    """
    return datetime.today()