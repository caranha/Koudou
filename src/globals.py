#TODO: Bring loading responsabilities from controller to globals

class Globals:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(Globals)
            cls.instance.__init__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        self.params = None

        self.simulation = None
        self.map = None
        self.step_length = None
        self.timestamp = None
        self.rng = None
        self.logger = None

    def load_parameters(self, params):
        pass

    def init(self):
        pass

    def init_test(self):
        pass
