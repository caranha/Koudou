from src.model.behavioral.activity.action_move import ActionMove
from src.model.behavioral.activity.action_wait import ActionWait
from src.model.behavioral.activity.action_modify_attribute import ActionModifyAttribute
from src.model.behavioral.activity.action_change_behavior import ActionChangeBehavior

class Activity:
	def __init__(self,name, command = "and"):
		self.name = name
		self.condition = []
		self.rewards = []
		self.actions = []
		self.actions_arr = []
		self.command = command.lower()

	def add_condition(self,condition):
		self.condition.append(condition)

	def add_reward(self,reward):
		self.rewards.append(reward)

	def add_action(self,action):

		action_arr = action.replace(" ", "").split(":")
		action_arr[0] = action_arr[0].lower()
		if action_arr[0] =="move" and "id)" not in action_arr[1] and "!" not in action_arr[1]:
			action_arr[1] = action_arr[1].replace("(building_type)", "")
			action_arr[1] = action_arr[1].replace("(type)", "")

		self.actions.append(action)
		self.actions_arr.append(action_arr)

	def check_conditions(self,agent,kd_sim, kd_map, step_count, rng):
		result = True
		command = self.command.lower()

		if (command == "and" or command == "none" ):
			for cond in self.condition:
				result = result and cond.check_value(agent, kd_sim)
				if not result:
					break
		elif (command == "or"):
			for cond in self.condition:
				result = result or cond.check_value(agent, kd_sim)
				if result:
					break

		if not result:
			return False

		for action in self.actions_arr:
			if action[0]=="move" and "id)" not in action[1] and "!" not in action[1]:
				destination = kd_map.get_random_business(action[1], 1, rng, step_count= step_count, only_open = True)
				if len(destination) == 0:
					return False
		return True

	def generate_actions(self,agent,kd_map,step_count,rng):
		actions = []
		for x in self.actions:
			temp = x.split(":")
			temp[0] = temp[0].replace(" ","")
			if (temp[0].lower() == "wait"):
				actions.append(ActionWait(agent,temp[1],rng))
			elif (temp[0].lower()=="move"):
				actions.append(ActionMove(agent,kd_map,temp[1],rng,step_count))
			elif (temp[0].lower()=="modify_attribute"):
				actions.append(ActionModifyAttribute(agent,temp[1]))
			elif (temp[0].lower()=="change_behavior"):
				actions.append(ActionChangeBehavior(agent,temp[1]))
		return actions

	def __str__(self):
		tempstring = "[Activity]\n"
		tempstring += f"   name = {self.name}\n"
		tempstring += f" Condition:\n"
		for x in self.condition:
			tempstring += f"   {x.short_string}\n"
		tempstring += f" Action:\n"
		for x in self.actions:
			tempstring += f"   {x.short_string}\n"
		tempstring += f" Reward:\n"
		for x in self.rewards:
			tempstring += f"   {x.short_string}\n"
		return tempstring