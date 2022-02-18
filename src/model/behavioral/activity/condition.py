import operator
from src.model.behavioral.attribute.attribute import cast
class Condition:
    def __init__(self,name, attribute_name,value, operator_string,typing = "string"):
        self.name = name
        self.attribute_name = attribute_name
        self.value = value
        self.operator_string = operator_string
        self.operator = _fetch_operator(operator_string)
        self.typing = typing

    def check_value(self,agent):
        value = self.value
        if ("$" in value):
            value = agent.get_attribute(value.replace("$",""))

        value = cast(value,self.typing)
        print(f"{agent.get_attribute(self.attribute_name)} {_fetch_symbols(self.operator_string)} {value}")
        try:
            return self.operator(agent.get_attribute(self.attribute_name), value)
        except:
            tempstring = f"\nProblem with {self.attribute_name}\n"
            tempstring += f"value             = {value}\n"
            tempstring += f"agent's attribute = {agent.get_attribute(self.attribute_name)}\n"
            raise ValueError(tempstring)

    @property
    def short_string(self):
        return f"{self.attribute_name} {_fetch_symbols(self.operator_string)} {self.value}"

    def __str__(self):
        tempstring =   "[Condition]\n"
        tempstring += f"  name      = {self.name}\n"
        tempstring += f"  attribute = {self.attribute_name}\n"
        tempstring += f"  operator  = {self.operator_string}\n"
        tempstring += f"  value     = {self.value}\n\n"
        return tempstring

def _fetch_operator(operator_string):
    if(operator_string.lower() == "greater_than_equal"):
        return operator.ge
    elif(operator_string.lower() == "greater_than"):
        return operator.gt
    elif(operator_string == "less_than_equal"):
        return operator.le
    elif(operator_string == "less_than"):
        return operator.lt
    elif(operator_string == "equal"):
        return operator.eq
    elif(operator_string == "not_equal"):
        return operator.ne

def _fetch_symbols(operator_string):
    if(operator_string.lower() == "greater_than_equal"):
        return ">="
    elif(operator_string.lower() == "greater_than"):
        return ">"
    elif(operator_string == "less_than_equal"):
        return "<="
    elif(operator_string == "less_than"):
        return "<"
    elif(operator_string == "equal"):
        return "=="
    elif(operator_string == "not_equal"):
        return "!="