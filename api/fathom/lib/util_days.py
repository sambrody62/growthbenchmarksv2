import datetime as dt

def get_today_as_str():
    today = dt.datetime.today().strftime('%Y-%m-%d')
    return today

def get_this_month_as_str():
    this_month = dt.datetime.today().strftime('%Y-%m')
    return this_month

def get_last_month_as_str():
    today = dt.datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - dt.timedelta(days=1)
    return last_day_of_last_month.strftime('%Y-%m')

def get_date_as_month_str(date_str):
    datetime = dt.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime.strftime('%Y-%m')

def get_day_x_days_ago_as_str(days=1):
    date = dt.datetime.now() - dt.timedelta(days=days)
    return date.strftime('%Y-%m-%d')

def get_yesterday_as_str():
    date = get_day_x_days_ago_as_str(days=1)
    return date

def get_since_and_until_dates_as_str(days=90):
    # End date is yesterday
    until = get_day_x_days_ago_as_str(days=1)

    # X days before yesterday
    since = get_day_x_days_ago_as_str(days=days)
    return since, until

def get_start_and_end_dates_for_2_months_as_str():
    today = dt.datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - dt.timedelta(days=1)

    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    last_day_of_prev_month = first_day_of_last_month - dt.timedelta(days=1)
    first_day_of_prev_month = last_day_of_prev_month.replace(day=1)

    last_month_end_date = last_day_of_last_month.strftime('%Y-%m-%d')
    prev_month_start_date = first_day_of_prev_month.replace(day=1).strftime('%Y-%m-%d')

    return prev_month_start_date, last_month_end_date