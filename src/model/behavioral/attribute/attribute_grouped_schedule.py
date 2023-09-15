from .attribute import Attribute

class AttributeGroupedSchedule(Attribute):
    """
    [Class] AttributeGroupedSchedule
    A class that represent agent's schedule. 
    Think of it as the agent have an appointment.
    
    Properties:
        - name      : (string-inherited) "is_working"/ "is_praying" etc
        - value     : (string) the profession name e.g "Student"
        - schedules : (list-AttributeSchedule) list of work schedule
    """
    def __init__(self, name):
        super(AttributeGroupedSchedule,self).__init__(name, False, "bool") 
        self.schedules = []
        self.active_schedule = None

    def add_schedule(self, schedule):
        self.schedules.append(schedule)

    def step(self,kd_sim,kd_map,step_count,step_length,rng,agent):
        self.value = False
        for x in self.schedules:
            x.step(kd_sim,kd_map,step_count,step_length,rng,agent)
            if x.get_value:
                self.value = True
                break

    def __str__(self):
        tempstring = "[AttributeGroupedSchedule]\n"
        tempstring += self._get_object_details()
        tempstring += f"   schedules :\n"
        for x in self.schedules:
            tempstring += f"   - {x.short_string}\n"
        return tempstring
