"""
"""

class Converter:
    def min2hour(self, mins):
        hours = mins // 60
        mins = mins % 60
        return hours, mins

    def hour2day(self, hours):
        days = hours // 24
        if days == 0:
            return hours
        else:
            hours = hours % 24
            return days, hours

    def parse_HM(self, time):
        hours_rest = time.split('h')
        hours = int(hours_rest[0])
        minutes_rest = hours_rest[1].split('m')
        minutes = int(minutes_rest[0])
        return hours, minutes

    @staticmethod
    def convert2string(hours, minutes):
        return "{}h{}m".format(hours, minutes)

    @staticmethod
    def convert2string_days(days, hours, minutes):
        if minutes != 0:
            return "{}d{}h{}m".format(days, hours, minutes)
        else:
            return "{}d{}h".format(days, hours)