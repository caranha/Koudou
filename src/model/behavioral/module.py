from abc import ABC, abstractmethod

class Module(ABC):
	"""
	[Class] Action
	An abstract class that represent agents actions
	
	Properties:
		- name	  : (string) name of the action

	can 
	"""   	
	@abstractmethod
	def step(self,kd_sim,kd_map,step_count,step_length,rng,logger):
		"""
		[Method]
		Update method

		parameter:
		- step_length : (int) how many seconds elapsed

		return:
		- (int) the remainder of the step_length that was not consumed by this action
		"""
		pass
		