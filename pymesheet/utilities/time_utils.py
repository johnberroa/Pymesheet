"""
Time utilities for the manipulation of time.
@author: John Berroa
"""


class Converter:
    """
    Converts times from one measurement to another, and also parses or creates strings related to time
    """

    @staticmethod
    def sec2min(secs):
        mins = secs // 60
        return mins

    @staticmethod
    def min2hour(mins):
        hours = mins // 60
        if hours == 0:
            return 0, mins
        else:
            mins = mins % 60
            return hours, mins

    @staticmethod
    def min2decimal_hour(mins):
        hours = round(mins / 60, 1)
        return hours

    @staticmethod
    def hour2day(hours):
        days = hours // 24
        if days == 0:
            return 0, hours
        else:
            hours = hours % 24
            return days, hours

    @staticmethod
    def parse_DHM(time):
        days_rest = time.split('d')
        days = days_rest[0]
        hours_rest = days_rest[1].split('h')
        hours = hours_rest[0]
        mins_rest = hours_rest[1].split('m')
        mins = mins_rest[0]
        return int(days), int(hours), int(mins)

    @staticmethod
    def convert2string(hours, minutes):
        if minutes != 0:
            return "{} hours, {} minutes".format(hours, minutes)
        else:
            return "{} hours".format(hours, minutes)

    @staticmethod
    def convert2string_days(days, hours, minutes):
        if minutes != 0:
            return "{} days, {} hours, {} minutes".format(days, hours, minutes)
        else:
            return "{} days, {} hours".format(days, hours)

    @staticmethod
    def convert_int2day(number):
        if number == 0:
            return "Sunday"
        elif number == 1:
            return "Monday"
        elif number == 2:
            return "Tuesday"
        elif number == 3:
            return "Wednesday"
        elif number == 4:
            return "Thursday"
        elif number == 5:
            return "Friday"
        elif number == 6:
            return "Saturday"
        else:
            raise ValueError("Invalid integer input (0-6 allowed, input={})".format(number))


class TimeCalculator:
    """
    Adds or subtracts time
    """

    @staticmethod
    def add(hours1, minutes1, hours2, minutes2):
        total_hours = hours1 + hours2
        total_minutes = minutes1 + minutes2
        minute_hours, minutes = Converter.min2hour(total_minutes)
        hours = total_hours + minute_hours
        return hours, minutes

    @staticmethod
    def subtract(hours1, minutes1, hours2, minutes2):
        hours2 = hours2 + (minutes2 / 60)
        hours1 = hours1 + (minutes1 / 60)
        if hours1 < hours2:
            return None, None
        total_hours = hours1 - hours2
        hours = int(total_hours)
        minutes = round((total_hours % 1) * 60)
        return hours, minutes
