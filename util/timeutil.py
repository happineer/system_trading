from datetime import datetime


def get_time_str(format="YYMMDD-HHMMSS"):
    """시간정보를 문자열로 만들어 반환합니다.

        >>> t_str = get_time_str("YYMMDD-HHMMSS")
        >>> print(t_str)

    :param format:
    :return:
    """
    if format == "YYMMDD":
        t = datetime.today().strftime("%y%m%d")
    elif format == "YYYYMMDD":
        t = datetime.today().strftime("%Y%m%d")
    elif format == "YYMMDD-HHMMSS":
        t = datetime.today().strftime("%y/%m/%d-%H:%M:%S")
    else:
        t = datetime.today().strftime("%y/%m/%d-%H:%M:%S")
    return t


def get_datetime(format="YYMMDD"):
    """시간정보를 datetime객체로 만들어 반환합니다.

        need to implement..

    :param format:
    :return:
    """
    return datetime.today()