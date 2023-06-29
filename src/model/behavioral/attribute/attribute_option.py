from .attribute import Attribute, cast

class AttributeOption(Attribute):
    def __init__(self,name, value,options, typing = "string"):
        super(AttributeOption,self).__init__(name,value,typing)
        self.options = options
        for option in self.options:
            try:
                option["value"] = cast(option["value"],self.typing) #cast the options just to ensure
            except ValueError as e:
                if ("[Casting] " in str(e)):
                    self._unknown_type(self.typing)
                else:
                    self._casting_error(option["value"],self.typing)

    def get_options(self):
        return self.options

    def set_value(self,value):
        try:
            temp_value = cast(value,self.typing)
        except ValueError as e:
            if ("[Casting] " in str(e)):
                self._unknown_type(self.typing)
            else:
                self._casting_error(value,self.typing)

        success = False
        for x in self.options:
            if (x["value"] == temp_value):
                self.value = temp_value
                success = True
        if not success:
            tempstring = "\nInvalid value:\n"
            tempstring += self._get_object_details()
            tempstring += f" {temp_value} is not available in options.\n"
            tempstring += " Available options:\n"
            for option in self.options:
                tempstring += f" - {option['value']}\n"
            raise(ValueError(tempstring))

    def step(self,kd_sim,kd_map,step_count,step_length,rng,agent):
        pass

    def __str__(self):
        tempstring = "[AttributeOption]\n"
        tempstring += self._get_object_details()
        tempstring += " Options:\n"
        for option in self.options:
            tempstring += f" - {option['value']}\n"
