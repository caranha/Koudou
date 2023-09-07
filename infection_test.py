import pickle
import numpy as np

from src.util.parser import load_parameters
from src.model.behavioral.simulation import Simulation
from src.model.infection.infection_manager import initialize_infection, infection_step
from src.model.map.a_star import a_star_search
from src.util.paths import fromRoot
from src.logger import NoLog
from src.util.time_stamp import TimeStamp


def infection_test():
    parameters = load_parameters("parameters/test-setting.py", seed=101512)
    with open(fromRoot("cache/TX-To-TU.pkl"), "rb") as file:
        kd_map = pickle.load(file)

    rng = np.random.default_rng(seed=101512)
    agents_count = 5
    logger = NoLog

    sim = Simulation(parameters["SIM_CONFIG"], kd_map, rng, logger, agents_count, threads=2)
    infection = initialize_infection(parameters["DISEASES"], sim.agents, rng, logger)

    print(sim)
    print("#####################################################################")

    day = 1 * 24 *12
    step_size = 300

    for x in range(0, day):
        infection_step(step_size, kd_map, sim.agents, infection, rng, logger, TimeStamp(x*step_size))

    infected_ags = [ag for ag in sim.agents if ag.get_attribute("covid") != "susceptible"]
    print(len(infected_ags))

if __name__ == "__main__":
    infection_test()
