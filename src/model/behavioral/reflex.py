

class Reflex:
    def __init__(self, priority, reflexion):
        self.priority = priority
        self.reflexion = reflexion
        self.agent = None

    def __call__(self):
        self.reflexion()