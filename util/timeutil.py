from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta



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

def date_range(s_date, e_date, by="second"):
    if s_date >= e_date:
        return []

    date_list = []
    if by == "second":
        time_diff = (e_date - s_date).seconds
        date_list = [s_date + timedelta(seconds=x) for x in range(0, time_diff)]
    elif by == "minute":
        time_diff = (e_date - s_date).minutes
        date_list = [s_date + timedelta(minutes=x) for x in range(0, time_diff)]
    elif by == "hour":
        time_diff = (e_date - s_date).hours
        date_list = [s_date + timedelta(hours=x) for x in range(0, time_diff)]
    elif by == "day":
        time_diff = (e_date - s_date).days
        date_list = [s_date + timedelta(days=x) for x in range(0, time_diff)]
    elif by == "week":
        time_diff = (e_date - s_date).weeks
        date_list = [s_date + timedelta(weeks=x) for x in range(0, time_diff)]
    elif by == "month":
        # need to implement
        # time_diff = (e_date - s_date).months
        # date_list = [s_date + relativedelta(month=x) for x in range(0, time_diff)]
        pass
    elif by == "year":
        # need to implement
        # time_diff = (e_date - s_date).years
        # date_list = [s_date + relativedelta(year=x) for x in range(0, time_diff)]
        pass
    else:
        pass

    return date_list