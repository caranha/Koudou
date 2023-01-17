import json

class Disease:
    def __init__(self, name, attributes, transitions, infection_method_file, infectious_states, infected_starting_state):
        self.name = name
        self.attributes = attributes
        self.transitions = transitions
        self.infectious_states = infectious_states
        with open(infection_method_file) as file:
            self.infection_method = json.load(file)
        self.starting_state = infected_starting_state
