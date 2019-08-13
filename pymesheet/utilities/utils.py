import pendulum


def get_current_week_days(today):
    """
    Returns the datetimes for all days in the current work week as strings
    :param today: today as pd.datetime
    :return: string formatted datetimes (max 7)
    """
    days = [today]
    for day in range(1, 8):
        if days[-1].day_of_week == 0:
            new_day = today.subtract(days=day)
            days.append(new_day)
            break
        new_day = today.subtract(days=day)
        days.append(new_day)
    return [d.to_date_string() for d in days]


def generate_day_dict(days, tasks):
    """
    Creates a dictionary of days as keys and values as dictionaries of tasks with keys as empty lists
    :param days: days to use as keys
    :param tasks: tasks to use in the inner dicts
    :return: dictionary
    """
    day_dict = {}
    task_dict = {}
    for task in tasks:
        task_dict[task] = []
    for day in days:
        day_dict[day] = task_dict.copy()
    return day_dict
