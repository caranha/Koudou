from src.model.behavioral.module import Module
import json


class EmotionModule(Module):
    def __init__(self, parameters, logger):
        self.logger = logger
        with open(parameters[0]) as f:
            self.emotion_parameter = json.load(f)
        self.model_name = self.emotion_parameter["name"]
        self.concern_level_factor = self.emotion_parameter["concern_level"]
        self.cl_maximum = self.emotion_parameter["concern_level"]['negative']['maximum_value']
        self.cl_minimum = self.emotion_parameter["concern_level"]['positive']['minimum_value']
        self.transition_state = self.emotion_parameter["transition_states"]
        self.mask_change = self.emotion_parameter["masking_change"]
        self.logger_file = "emotion_log.txt"
        self.init_logger(logger)

    def init_logger(self, logger):
        """
        init to record log files as .csv and .txt
        """
        logger.add_file(self.logger_file)

        header = ["time", "time_stamp", "indifferent", "worried", "afraid", "numb"]
        logger.add_csv_file("emotion_summary.csv", header)

    def update_concern_level(self, agent):
        """
        update concern level for every agent every step
        GET and UPDATE all concern level factors for every agent
        Negative Part (contribute to the increase of concern level):
        1. community
            a. infection_rate_factor = (community_infection_rate - last_community_infection_rate) / last_community_infection_rate
            b. concern_level = concern_level + infection_rate_factor * 3
        2. family infection
            a. determine a new attribute for every agent at the initialization as family id
            b. broadcast the family infection information to the agents in the same family
            c. if a family member is infected (symptomatic & severe), the agent's concern level will increase every day by 0.1
        3. self infection
            a. if the agent is at symptomatic stage, the concern level will increase every day by 0.2
            b. if the agent is at severe stage, the concern level will increase every day by 0.3
        4. evacuation
            a. determine if the evacuation is triggered
            b. define a crowding factor: current_occupancy / max_capacity (should set max_capacity for every evacuation center)
            c. calculate the crowding factor when the agent is in the evacuation center
            d. contribute to the concern level: C = C + crowding_factor / 3
        Positive Part (contribute to the decrease of concern level):
        1. community
            a. similar as the negative part
        2. constant decay
            a. the concern level will decrease every day by 0.005

        Notice: the concern level will be bounded by the maximum and minimum value (can be adjusted):
            concern_level = min(1.5, max(0.5, concern_level))
        """

        pass

    def update_emotion_state(self, agent):
        """
        update emotion state for every agent every step
        """
        pass

    def emotion_step(self, kd_sim, kd_map, ts, step_length, rng, logger):
        """
        update emotion for every agent every step
        1. update concern level factors and integrate them for concern level update
        2. update emotion state
        """
        for agent in kd_sim.agents:
            self.update_concern_level(agent)
            self.update_emotion_state(agent)

        pass

    def step(self, kd_sim, kd_map, ts, step_length, rng, logger):
        self.emotion_step(kd_sim, kd_map, ts, step_length, rng, logger)