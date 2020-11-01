import datetime as dt
import holidays
from datetime import datetime
from pytz import timezone


def DTE(expir):
    """Finds days until expiration

    :param expir:
    :return: int (DTE)
    """
    now = dt.datetime.now()
    current_month = now.month
    today = now.day
    diff = int(expir[-2:]) - int(today)
    if int(expir[5:7]) == int(current_month):
        return diff
    else:
        return diff + 30 * (int(expir[5:7]) - int(current_month))


def find_friday():
    """Finds next Friday.

    :return: Year, Month, Date for Friday as a string.
    """
    now = dt.datetime.now()
    friday = (now.today() + dt.timedelta((4 - now.weekday()) % 7)).strftime("%Y-%m-%d")
    return friday


def third_friday(year, month, day):
    """Return datetime.date for monthly option expiration given year and month.

    :param year:
    :param month:
    :param day:
    :return: string (YYYY-MM-DD)
    """
    # The 15th is the lowest third day in the month
    third = dt.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))

    if day > third.day:
        month += 1
        third = dt.date(year, month, 15)
        w = third.weekday()
        if w != 4:
            third = third.replace(day=(15 + (4 - w) % 7))

    now = dt.datetime.now()
    currentDate = (now.today()).strftime("%Y-%m-%d")

    if str(third) != currentDate:  # See if current day is the monthly expiration, if it is move to next month.
        return third
    else:
        return third_friday(int(year), int(month), int(day) + 1)


def getHolidays():
    holidayDate = {}
    for date in holidays.USA(years=2021).items():
        if str(date[1]) != "Columbus Day" and str(date[1]) != "Labor day" and str(
                date[1]) != "Independence Day (Observed)" \
                and str(date[1]) != "Veterans Day":
            holidayDate[str(date[0])[5:]] = str(date[1])

    for date in holidays.Australia(years=2021).items():
        if str(date[1]) == "Good Friday":
            holidayDate[str(date[0])[5:]] = str(date[1])
    return holidayDate


def getYear():
    return dt.datetime.utcnow().year


def getMonth():
    return dt.datetime.utcnow().month


def getMonthlyDay():
    return dt.datetime.utcnow().day


def getDay():
    return dt.datetime.utcnow().today().weekday()


def getCurrentDay():
    return str(dt.datetime.utcnow().date())[5:7] + '-' + str(dt.datetime.utcnow().today().date())[8:]


def getMinute():
    return datetime.utcnow().minute


def getHour():
    return datetime.utcnow().hour


def getEstTimestamp():
    if getMinute() == 0:
        sMin = "00"
    else:
        sMin = str(getMinute())
    return str(datetime.now(timezone('US/Eastern')).hour) + ":" + sMin + " EST"


def getDayStamp():
    return str(datetime.utcnow().today())[:10]



