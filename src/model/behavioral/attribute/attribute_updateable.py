from .attribute import Attribute,cast

class AttributeUpdateable(Attribute):
    
    def __init__(self,name, value, min_val, max_val, step_change, typing):
        super(AttributeUpdateable,self).__init__(name,value,typing)
        self.min_val = cast(min_val,self.typing)
        self.max_val = cast(max_val,self.typing)
        self.step_change = cast(step_change,self.typing)


    def step(self,kd_sim,kd_map,step_count,step_length,rng,agent):
        self.value += self.step_change*step_length
        self.value = max(self.value,self.min_val) #protect minimum cap
        self.value = min(self.value, self.max_val) #protect max cap

    def set_max(self):
        self.value = self.max_val

    def set_min(self):
        self.value = self.min_val

    def __str__(self):
        tempstring = "[AttributeUpdateable]\n"
        tempstring += self._get_object_details()
        tempstring += f"   range       : {self.min_val} - {self.max_val}"
        tempstring += f"   step_update : {self.step_change} "
        return tempstring