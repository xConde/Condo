import datetime as dt
from functools import lru_cache

import holidays
from datetime import datetime
from pytz import timezone
from stocks import stock_controller as s
from stocks.options.option_controller import validateExp, round10


@lru_cache(maxsize=200)
def DTE(expir):
    """Finds days until expiration

    :param expir:
    :return: int (DTE)
    """
    now = dt.datetime.now()
    year = int(expir[:4]) - int(now.year) + 1
    diff = int(str(expir[-2:])) - int(now.day)
    if int(expir[5:7]) == int(now.month):
        return diff
    else:
        return (diff + 30 * (int(expir[5:7]) * year - int(now.month))) % 365


def getMonthsOut(expir):
    now = dt.datetime.now()
    year = int(expir[-4:]) - int(now.year) + 1
    diff = int(expir[3:5]) - int(now.day)
    if int(expir[:2]) == int(now.month) and year == 1:
        return 1
    else:
        return 1 + ((diff + 30 * (int(expir[:2]) * year - int(now.month))) % 365) // 30


def convertDate(expir):
    return datetime.strptime(expir, '%m-%d-%Y').strftime('%Y-%m-%d')


@lru_cache(maxsize=200)
def find_friday():
    """Finds next Friday.

    :return: Year, Month, Date for Friday as a string.
    """
    now = dt.datetime.now()
    friday = (now.today() + dt.timedelta((4 - now.weekday()) % 7)).strftime("%Y-%m-%d")
    return friday


@lru_cache(maxsize=200)
def generate_next_month_exp(exp):
    """Generates a new exp for next monthly
    '2020-01-17'
    :param exp:
    :return:
    """
    newDate = third_friday(int(str(exp)[:4]), int(str(exp)[5:7]), int(str(exp)[8:10]) + 1)
    return str(newDate)


@lru_cache(maxsize=200)
def generate_multiple_months(ticker, quantity):
    strike = round10(s.tickerPrice(ticker))
    monthly1 = validateExp(ticker, str(third_friday(getYear(), getMonth(), getMonthlyDay())), 'call', strike)
    months = [monthly1]
    for i in range(1, quantity):
        months.append(validateExp(ticker, generate_next_month_exp(months[i - 1]), 'call', strike))
    return months


@lru_cache(maxsize=200)
def third_friday(year, month, day):
    """Return datetime.date for monthly option expiration given year and month.

    :param year:
    :param month:
    :param day:
    :return: string (YYYY-MM-DD)
    """
    if month > 12:
        diff = int(month / 12)
        month = month % 12
        year += diff
    # The 15th is the lowest third week in the month
    third = dt.date(year, month, 15)
    # What day of the week is the 15th?
    w = third.weekday()
    # Friday is weekday 4
    if w != 4:
        # Replace just the day (of month)
        third = third.replace(day=(15 + (4 - w) % 7))

    if day > third.day:
        month += 1
        if month > 12:
            diff = int(month / 12)
            month = month % 12
            year += diff
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


def getEstHour():
    return datetime.now(timezone('US/Eastern')).hour


def getEstTimestamp():
    if getMinute() == 0:
        sMin = "00"
    else:
        sMin = str(getMinute())
    return str(getEstHour()) + ":" + sMin + " EST"


def getDayStamp():
    return str(datetime.utcnow().today())[:10]


def getHolidays():
    holidayDate = {}
    marketOpenHolidays = ['Columbus Day', 'Veterans Day']
    irrelevantHolidays = ['Independence Day (Observed)']
    for date in holidays.USA(years=getYear()).items():
        if str(date[1]) not in marketOpenHolidays and str(date[1]) not in irrelevantHolidays:
            holidayDate[str(date[0])[5:]] = str(date[1])

    for date in holidays.Australia(years=getYear()).items():
        if str(date[1]) == "Good Friday":
            holidayDate[str(date[0])[5:]] = str(date[1])
    return holidayDate


def formatIntForHumans(num):
    """Formats integer into a readable string format

    :param num:
    :return:
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def formatStrForComputers(num):
    numSwitch = {
        'K': 1000,
        'M': 1000000,
    }
    mult = num[len(num) - 1]
    return int(num[:-1]) * numSwitch.get(mult)
