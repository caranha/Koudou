import itertools
from typing import Dict, List, Tuple
from src.util import time_stamp as ts

class Business:
    idCounter = itertools.count().__next__

    def __init__(self, node_id: str, place_id:str, road_connection_id: str, business_type: str):
        self.id = self.idCounter()
        self.road_connection_id: str = road_connection_id
        self.node_id: str = node_id
        self.place_id: str = place_id
        self.type: str = business_type

        self.workers_ids: List[str] = []

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        # working hours is an dictionary where the key is the day of the week.
        # the value is an array of tuples where each tuple is a period of time in that day when the restaurant is open
        # Ex: if a store is open on Tuesdays from 9:00~12:00 and 13:00~18:00
        #     self.working_hours["Tue"] = [("9:00", "12:00"), ("13:00", "18:00")]
        self.working_hours: Dict[str, Tuple[str, str]] = {w: [] for w in weekdays}


    def add_worker(self, agent_id):
        self.workers_ids.append(agent_id)

    def add_working_hour(self, day, open_hour, close_hour):
        if day not in self.working_hours:
            raise KeyError("day should be one of the following: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']")
        t = (open_hour, close_hour)
        self.working_hours[day].append(t)

    def is_open(self, step_count):
        day = ts.get_day_of_week_str(step_count)
        t_hour = ts.get_hour(step_count)
        t_min = ts.get_minute(step_count)
        for start, finish in self.working_hours[day]:
            if start==finish:
                #Means it is open 24 hours
                return True 
                
            start_hour, start_minute = [int(i) for i in start.split(":")]
            finish_hour, finish_minute = [int(i) for i in finish.split(":")]
            
            if start_hour < t_hour and t_hour < finish_hour:
                return True
            elif start_hour == t_hour and start_minute <= t_min:
                return True
            elif finish_hour == t_hour and t_min <= finish_minute:
                return True
                
        return False

    def __str__(self):
        tempstring = "[Business]\n"
        return tempstring
