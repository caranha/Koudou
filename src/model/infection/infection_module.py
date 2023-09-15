from src.model.behavioral.module import Module
from src.model.infection.infection_manager import initialize_infection, infection_step
class InfectionModule(Module):

	def __init__(self, parameters, kd_sim, rng, logger):
		self.infection = initialize_infection(parameters, kd_sim.agents, rng, logger)

	def step(self,kd_sim,kd_map,step_count,step_length,rng,logger):
	    infection_step(step_length, kd_map, kd_sim.agents, self.infection, rng,logger,step_count)
