class TimeStamp:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(TimeStamp)
            cls.instance.__init__(*args, **kwargs)
        return cls.instance

    def __init__(self, step_count=0):
        self.step_count = step_count

    def get_hour(self):
        return int(int(self.step_count/3600) % 24)

    def get_day(self):
        return int((self.step_count/(24*3600)))

    def get_day_of_week(self):
        return int(int(self.step_count/(24*3600)) % 7)

    def get_second(self):
        return self.step_count % 60

    def get_day_of_week_str(self):
        temp = self.get_day_of_week()
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

    def get_minute(self):
        return int(int(self.step_count/60) % 60)

    def get_week(self):
        return int(self.step_count/(7*24*3600))

    def clone(self):
        return TimeStamp(self.step_count)

    def step(self, step_length):
        self.step_count += step_length

    def __str__(self):
        tempString = "{}, Week = {} Day = {}\n".format(
            self.get_day_of_week_str(), self.get_week(), self.get_day())
        tempString += "Current Time = {:02d}:{:02d}:{:02d}".format(
            self.get_hour(), self.get_minute(), self.get_second())
        return tempString

    def is_after(self, target_time_stamp):
        return target_time_stamp.step_count > self.step_count

    def get_time_only(self):
        return self.step_count % (24*60*60)

    def get_hour_min_str(self):
        h = self.get_hour()
        m = self.get_minute()
        return f"{h:02d}:{m:02d}"
