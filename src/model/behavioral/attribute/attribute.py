from typing import Dict
import warnings

class Attribute:

    def __init__(self,name,value,typing = "string"):
        self.name = name
        self.typing = typing.lower()
        if (self.typing == "integer"):
            self.typing = "int"
        self.value = cast(value,self.typing)
        self._cast_value()

    @property
    def get_value(self):
        return self.value

    def set_value(self,value):
        try:
            self.value = cast(value,self.typing)
        except ValueError as e:
            if ("[Casting] " in str(e)):
                self._unknown_type(self.typing)
            else:
                self._casting_error(value, self.typing)
        

    def update_value(self,value):
        if self.typing == "int" or self.typing == "integer" or self.typing == "float":
            self.value += cast(value,self.typing)
        else:
            tempstring = "[Attribute] this attribute cannot be updated:\n"
            tempstring += self._get_object_details()
            tempstring += "Only integer or float type are updatable.\n"
            tempstring += "Use set_value(value) for other type.\n"
            raise(ValueError(tempstring))

    def set_max(self):
        tempstring = "[Attribute] setting max value failed:\n"
        tempstring += self._get_object_details()
        tempstring += "set max value is not available for this attribute.\n"
        warnings.warn(tempstring)

    def set_min(self):
        tempstring = "[Attribute] setting min value failed:\n"
        tempstring += self._get_object_details()
        tempstring += "set min value is not available for this attribute.\n"
        warnings.warn(tempstring)

    # todo: this func just cast types, shouldnt it update the values ionstead?
    def step(self,kd_sim,kd_map,step_count,step_length,rng,agent):
        self._cast_value() # just to make sure the data is safe

    def _get_object_details(self):
        tempstring =  f"   attribute   : {self.name}\n"
        tempstring += f"   type        : {self.typing}\n"
        tempstring += f"   value       : {self.value}\n"
        return tempstring

    def _cast_value(self):
        try:
            self._value =  cast(self.value,self.typing)
        except ValueError as e:
            if ("[Casting] " in str(e)):
                self._unknown_type(self.typing)
            else:
                self._casting_error(self.value, self.typing)

    def _casting_error(self, value, typing):               
        tempstring = f"\nUnable to cast value {value} to {typing} :\n"
        tempstring += self._get_object_details()
        raise(ValueError(tempstring))


    def _unknown_type(self,typing):
        tempstring = f"\nUnknown typing: {typing} :\n"
        tempstring += self._get_object_details()
        raise(ValueError(tempstring))

    def __str__(self):
        tempstring = "[Attribute]\n"
        tempstring += self._get_object_details()
        return tempstring

def cast(value,typing):
    if typing == "string":
        return f"{value}"
    elif typing == "bool":
        temp = value
        if isinstance(temp, str):
            temp = temp.lower()== "true"
        return bool(temp)
    elif typing == "int" or typing == "integer":
        return int(value)
    elif typing == "float":
        return float(value)
    else:
        tempstring = f"\n[Casting] Unknown typing: {typing}\n"
        raise(ValueError(tempstring))