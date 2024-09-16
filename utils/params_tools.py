import pandas as pd
from datetime import timedelta


def get_month_week(execution):
    month_week = {}

    for month, weeks in execution.groupby('Month')['Week Number']:
         week_dates = []
         for week in weeks:
             week_dates.append(week)
         month_week[month] = sorted(list(set(week_dates)))

    return month_week


def get_week_dates(year, month, week):
    month_start = pd.Timestamp(f'{year}-{month:02d}-01')

    day_of_week = month_start.weekday()

    if day_of_week != 0:
        first_week_start = month_start - timedelta(days=day_of_week)
    else:
        first_week_start = month_start
    
    week_start = first_week_start + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)

    if week_start.month != month and week == 1:
        week_start = month_start
    
    if week_end.month != month:
        week_end = month_start + pd.offsets.MonthEnd(0)
    
    return week_start.date(), week_end.date()


def get_days_for_month(year, month, min_date, max_date):
    min_day = pd.Timestamp(min_date)
    max_day = pd.Timestamp(max_date)

    month_start = pd.Timestamp(f'{year}-{month:02d}-01')
    month_end =  month_start + pd.offsets.MonthEnd(0)

    if min_day < month_start:
        min_day = month_start

    if max_day > month_end:
        max_day = month_end

    return min_day.day, max_day.day