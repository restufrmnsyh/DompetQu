from datetime import datetime, timezone, timedelta

WIB = timezone(
    timedelta(hours=7)
)

def sekarang_wib():
    return datetime.now(WIB)