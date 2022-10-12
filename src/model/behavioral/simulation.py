from typing import List
from src.model.behavioral import agent_manager
from src.model.behavioral.agent import Agent
from src.util.time_stamp import TimeStamp
import src.model.map.a_star as a_star
class Simulation:
	def __init__(self,config,kd_map,rng,agents_count,logger, threads = 1, report = None):
		self.agents: List[Agent] = []
		self.logger = logger
		attribute_generator = agent_manager.load_attributes_generator(config["attributes"],rng, self.logger)
		self.agents = agent_manager.generate_agents(kd_map,attribute_generator,agents_count, self.logger)
		self.conditions = agent_manager.load_conditions(config["condition"],rng, self.logger)
		self.behaviors = {}
		for key in config["behaviors"]:
			self.behaviors[key] = agent_manager.load_behavior(key, config["behaviors"][key], self.conditions, rng, self.logger)
		self.logger.write_line("log.txt", "Adding behaviors to agents")
		for x in self.agents:
			x.behaviors = self.behaviors
			x.default_behavior = self.behaviors[config["default_behavior"]]
		self.attributes = {}
		attribute_generator.generate_attribute_for_simulation(self,kd_map, self.logger)
		self.rng = rng
		self.ts = TimeStamp(0)
		self.threads = threads
		self.kd_map = kd_map
		self.report = report
		self.d_agents_by_location = {}
		self.modules = []
		self.pathfind_cache = {}

	def add_attribute(self,attr):
		self.attributes[attr.name] = attr

	def get_attribute(self,name):
		return self.attributes[name].get_value

	def __str__(self):
		tempstring = "[Simulation]\n"
		tempstring += f"Total agents = {len(self.agents)}\n"
		tempstring += f"Condition = {len(self.conditions)}\n"
		tempstring += f"Attributes:\n"
		for x in self.attributes:
			tempstring +=  f"  - {x} = {self.attributes[x].get_value}\n"

		return tempstring

	def attribute_step(self,kd_sim,kd_map,ts,step_length,rng,logger):
		#update attribute
		for attr in self.attributes:
			self.attributes[attr].step(kd_sim,kd_map,ts,step_length,rng,None)

	def step(self,step_length,logger):
		self.ts.step(step_length)
		# todo: this function basically cast types to the attrs, change its names
		# why doesnt this happen on init?
		self.attribute_step(self,self.kd_map,self.ts,step_length,self.rng,logger)
		##############################################################################
		# update all agents attribute
		##############################################################################
		for agent in self.agents:
			agent.attribute_step(self,self.kd_map,self.ts,step_length,self.rng,logger)

		##############################################################################
		# check for activities
		##############################################################################
		move_action_pool = []
		for agent in self.agents:
			# function below create all agents action but just returns the move actions, the others are saved on the agent
			move_actions = agent.behavior_step(self,self.kd_map,self.ts,step_length,self.rng,logger)
			move_action_pool.extend(move_actions)

		##############################################################################
		# pathfind
		##############################################################################
		# print(f"{len(move_action_pool)} move actions was generated")
		if (len(move_action_pool) > 0):
			self.pathfind(move_action_pool)

		##############################################################################
		# action step
		##############################################################################
		for agent in self.agents:
			agent.action_step(self,self.kd_map,self.ts,step_length,self.rng,logger)

		##############################################################################
		# construct location dictionary for ease of use
		##############################################################################
		self.group_agents_by_location()
		##############################################################################
		# Plugins steps
		##############################################################################
		for module in self.modules:
			module.step(self,self.kd_map,self.ts,step_length,self.rng,logger)
		##############################################################################
		# epidemicon
		##############################################################################

	def group_agents_by_location(self):
		self.d_agents_by_location = {}
		for agent in self.agents:
			if (agent.get_attribute("current_node_id") not in self.d_agents_by_location.keys()):
				self.d_agents_by_location[agent.get_attribute('current_node_id')] = []
			self.d_agents_by_location[agent.get_attribute('current_node_id')].append(agent)

	def pathfind(self,move_actions):
		pool = []
		for x in move_actions:
			temp = (x.origin ,x.destination)
			if (temp not in pool):
				pool.append(temp)
		# print(f"Starting pathfinding consisting of {len(pool)} unique pathfinding request")
		results = a_star.parallel_a_star(self.kd_map, pool, n_threads=self.threads, pathfind_cache=self.pathfind_cache, report = self.report)
		for x in move_actions:
			temp = (x.origin ,x.destination)
			x.generate_vector(self.kd_map, results[temp])

	def summarized_attribute(self,attribute_name):
		temp = {}
		for agent in self.agents:
			key = agent.get_attribute(attribute_name)
			if key not in temp.keys():
				temp[key] = 0
			temp[key] += 1
		return temp
