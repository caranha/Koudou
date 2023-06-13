import json
from src.util.paths import fromRoot

class Disease:
    def __init__(self, name, symptoms, attributes, transitions, infection_method_file, infectious_states,
                 infected_starting_state, precautionary_measures):
        self.name = name
        self.symptoms = symptoms
        self.attributes = attributes
        self.transitions = transitions
        self.infectious_states = infectious_states
        self.precautionary_measures = precautionary_measures
        with open(fromRoot(infection_method_file)) as file:
            self.infection_method = json.load(file)
        self.starting_state = infected_starting_state
    def __str__(self):
        info = "name : " + str(self.name)
        info += "\n symptoms : " + str(self.symptoms)
        info += "\n transitions : " + str(self.transitions)
        info += "\n starting_state : " + str(self.starting_state)
        return info
