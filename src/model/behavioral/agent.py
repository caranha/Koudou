from src.model.map.coordinate import Coordinate
from src.model.behavioral.activity.action_move import ActionMove
from src.util.simulation_element import SimulationElement
from src.util.cast import cast
from src.util.descriptors import LimitedAttribute, OptionsAttribute
from src.model.behavioral.attribute import attribute_updateable, attribute_option, attribute_schedule, attribute_grouped_schedule

class Agent(SimulationElement):
	def __init__(self):
		super().__init__()
		self.current_behavior = None
		self.behaviors = {}
		self.actions = []
		self.active_action = None
		self.curr_coordinate = Coordinate(0.0, 0.0)
		self.prev_coordinate = Coordinate(0.0,0.0)
		self.previous_activity = ""
		self.color = "#3333CC"

	def step(self):
		pass

	def add_attribute(self,attr):
		self.__dict__[attr.name] = attr.value
		self.__dict__["_"+attr.name] = attr.value

		if isinstance(attr, attribute_updateable.AttributeUpdateable):
			setattr(Agent, attr.name, LimitedAttribute(attr.min_val, attr.max_val))
			object.__getattribute__(Agent, attr.name).__set_name__(Agent, attr.name)
			Agent.update_attr[attr.name] = attr.step_change

		if isinstance(attr, attribute_option.AttributeOption):
			setattr(Agent, attr.name, OptionsAttribute([o['value'] for o in attr.options]))
			object.__getattribute__(Agent, attr.name).__set_name__(Agent, attr.name)

		if isinstance(attr, attribute_schedule.AttributeSchedule):
			pass

		if isinstance(attr, attribute_grouped_schedule.AttributeGroupedSchedule):
			pass



	def get_attribute(self,name):
		return self.__getattribute__(name)

#TODO: Remove after refactoring Infection Model
	def has_attribute(self,name):
		return name in self.__dict__.keys()
	
	def update_attribute(self,attribute_name,value):
		if value.lower() == "max":
			self.__setattr__(attribute_name, float("inf"))
		elif value.lower() == "min":
			self.__setattr__(attribute_name, float("-inf"))
		elif "(minus)" in value:
			temp = f"-{value.replace('(minus)','')}"
			self.update_attribute(attribute_name, value)
		elif type(self.__dict__[attribute_name]) is str or type(self.__dict__[attribute_name]) is bool:
			self.set_attribute(attribute_name, value)
		else:
			self.__dict__[attribute_name] += cast(value, type(self.__dict__[attribute_name]))

	def set_attribute(self,attribute_name,value):
		self.__setattr__(attribute_name, value)

	def add_behavior(self,behavior):
		self.behaviors[behavior.name] = behavior

	def force_reset(self):
		if len(self.actions) > 0 and isinstance(self.actions[0],ActionMove):
			self.actions[0].force_reset()
			self.actions = self.actions[:1]
		else:
			self.actions = []

	def change_behavior(self,behavior_name):
		self.current_behavior = self.behaviors[behavior_name]

	def __str__(self):
		tempstring = "[Agent]\n"
		tempstring += f" Agent ID           = {self.id}\n"
		tempstring += f" Current behavior   = {self.current_behavior.name}\n"
		tempstring += f" Current location   = (lat = {self.coordinate.lat}, lon {self.coordinate.lon})\n"
		tempstring += f" Current Actions    = {len(self.actions)}\n"
		tempstring += f" Current Activities = {self.previous_activity}\n"
		tempstring += f" Attributes:\n"
		for attr in list(self.__dict__.keys()):
			if not attr.startswith("_"):
				tempstring +=  f"  - {attr[1:]} = {self.__dict__[attr]}\n"
		return tempstring

	def attribute_step(self,kd_sim,kd_map,ts,step_length,rng,logger):
		self.__update__()

	def behavior_step(self,kd_sim,kd_map,ts,step_length,rng,logger):
		# if idle check action
		if len(self.actions) == 0:
			return self.current_behavior.step(kd_sim,kd_map,ts,step_length,rng,self,logger) #get actions
		return []

	def action_step(self,kd_sim,kd_map,ts,step_length,rng,logger):
		leftover = step_length
		while len(self.actions) > 0:
			act = self.actions[0]
			leftover = act.step(kd_sim,kd_map,ts,leftover,rng)
			if act.is_finished:
				self.actions.pop(0)
			else:
				break

	@property
	def coordinate(self):
		return self.curr_coordinate

	@coordinate.setter
	def coordinate(self, value):
		self.prev_coordinate = self.curr_coordinate
		self.curr_coordinate     = value
