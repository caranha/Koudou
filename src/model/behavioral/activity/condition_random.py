import operator
from .condition import Condition,_fetch_operator,_fetch_symbols
from src.model.behavioral.attribute.attribute import cast

class ConditionRandom(Condition):
    def __init__(self,name,value,min_value, max_value, rng, operator_string,typing = "string",target ="agent"):
        self.name = name
        self.min_value = cast(min_value,typing)
        self.max_value = cast(max_value,typing)
        self.value = value
        self.operator_string = operator_string
        self.operator = _fetch_operator(operator_string)
        self.typing = typing
        self.target = target.lower()
        self.rng = rng

    def check_value(self,agent,kd_sim):
        value2 = self.rng.uniform(self.min_value, self.max_value)
        value = self.value
        #print(str(value)+" "+str(value2))
        if ("$" in value):
            value = agent.get_attribute(value.replace("$",""))
        value = cast(value,self.typing)
        try:    
            return self.operator(value2, value)
        except:
            tempstring = f"\nProblem with random condition {self.name}\n"
            tempstring += f"value             = {value}\n"
            tempstring += f"randomizer result = {value2}\n"
            raise ValueError(tempstring)

    @property
    def short_string(self):
        return f"{self.attribute_name} {_fetch_symbols(self.operator_string)} {self.value}"

    def __str__(self):
        tempstring =   "[Condition]\n"
        tempstring += f"  name      = {self.name}\n"
        tempstring += f"  operator  = {self.operator_string}\n"
        tempstring += f"  value     = {self.value}\n\n"
        return tempstring