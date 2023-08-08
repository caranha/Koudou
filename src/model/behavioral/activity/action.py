from abc import ABC, abstractmethod

class Action(ABC):
	"""
	[Class] Action
	An abstract class that represent agents actions
	
	Properties:
		- name	  : (string) name of the action

	can 
	"""   	
	@abstractmethod
	def step(self, kd_sim, kd_map, step_length, rng):
		"""
		[Method]
		Update method

		parameter:
		- step_length : (int) how many seconds elapsed

		return:
		- (int) the remainder of the step_length that was not consumed by this action
		"""
		pass

	@property
	@abstractmethod
	def short_string(self):
		pass

	@property
	@abstractmethod
	def is_finished(self):
		"""
		[Property]
		Check if this action is finished or not

		return:
		- (bool) true if finished, false otherwise
		"""
		pass