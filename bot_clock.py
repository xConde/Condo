import datetime as dt
import holidays
from datetime import datetime


dayIndex = dt.datetime.today().weekday()  # 0-6 index
hour = datetime.now().hour + 1  # datetime.now().hour+1 for central to eastern (fix later)
min = datetime.now().minute
currentDay = str(dt.datetime.today().date())[5:7] + '-' + str(dt.datetime.today().date())[8:]

holidayDate = {}
for date in holidays.UnitedStates(years=2020).items():
    holidayDate[str(date[0])[5:]] = str(date[1])


if hour < 12:
    AM = True
else:
    AM = False

