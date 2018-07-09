from datetime import datetime


def get_time(format="YYMMDD-HHMMSS"):
    if format == "YYMMDD":
        t = datetime.today().strftime("%y%m%d")
    elif format == "YYYYMMDD":
        t = datetime.today().strftime("%Y%m%d")
    elif format == "YYMMDD-HHMMSS":
        t = datetime.today().strftime("%y%m%d-%H%M%S")
    else:
        t = datetime.today().strftime("%y%m%d-%H%M%S")
    return t
