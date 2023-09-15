    # def __str__(self):
    #     tempString = "{}, Week = {} Day = {}\n".format(
    #         self.get_day_of_week_str(), self.get_week(), self.get_day())
    #     tempString += "Current Time = {:02d}:{:02d}:{:02d}".format(
    #         self.get_hour(), self.get_minute(), self.get_second())
    #     return tempString


def get_hour(step_count):
    return int(int(step_count/3600) % 24)


def get_day(step_count):
    return int((step_count/(24*3600)))


def get_day_of_week(step_count):
    return int(int(step_count/(24*3600)) % 7)


def get_second(step_count):
    return step_count % 60

def get_day_of_week_str(step_count):
    temp = get_day_of_week(step_count)
    if (temp == 0):
        return "Mon"
    if (temp == 1):
        return "Tue"
    if (temp == 2):
        return "Wed"
    if (temp == 3):
        return "Thu"
    if (temp == 4):
        return "Fri"
    if (temp == 5):
        return "Sat"
    if (temp == 6):
        return "Sun"

def get_minute(step_count):
    return int(int(step_count/60) % 60)

def get_week(step_count):
    return int(step_count/(7*24*3600))

def is_after(step_count, target):
    return target > step_count

def get_time_only(step_count):
    return step_count % (24*60*60)

def get_hour_min_str(step_count):
    h = get_hour(step_count)
    m = get_minute(step_count)
    return f"{h:02d}:{m:02d}"
