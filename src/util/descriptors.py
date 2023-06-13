

class LimitedAttribute:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return instance.__dict__[self.private_name]

    def __set__(self, instance, value):
        value = min(value, self.max_value)
        value = max(value, self.min_value)
        instance.__dict__[self.public_name] = value

    def set_max(self):
        self.value = self.max_value

    def set_min(self):
        self.value = self.min_value

class OptionsAttribute:
    def __init__(self, options):
        self.options = options

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return instance.__dict__[self.private_name]

    def __set__(self, instance, value):
        if value in self.options:
            instance.__dict__[self.public_name] = value
        else:
            tempstring = "\nInvalid value:\n"
            tempstring += self._get_object_details()
            tempstring += f" {value} is not available in options.\n"
            tempstring += " Available options:\n"
            for option in self.options:
                tempstring += f" - {option['value']}\n"
            raise (ValueError(tempstring))

