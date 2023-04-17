from datetime import date
from dateutil.relativedelta import relativedelta

try:
    date_birth = date(2021, 2, 29)
except ValueError:
    date_birth = date(2021, 2, 28)

date1 = date(2022, 12, 31)
date2 = date.today()
date3 = date2 + relativedelta(days=20)
last_year_date = date(date.today().year, 12, 31)

days_delta = (date3 - date2).days

day_of_year = date3.timetuple().tm_yday

print(days_delta)
print(day_of_year)
