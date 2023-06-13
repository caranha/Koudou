from src.model.behavioral.activity.action_move import ActionMove

class Behavior:
	def __init__(self,name):
		self.name = name
		self.activities = []

	def add_activity(self,activity):
		self.activities.append(activity)

	def step(self,kd_sim,kd_map,ts,step_length,rng,agent,logger):
		move_action_pool = []
		for act in self.activities:
			if act.check_conditions(agent,kd_sim, kd_map, ts,rng):
				if agent.previous_activity != act.name:
					temp_activity = {}
					temp_activity["time"] = ts.get_hour_min_str()
					temp_activity["time_stamp"] = ts.step_count
					temp_activity["agent_id"] = agent.id
					temp_activity["profession"] = agent.get_attribute("profession")
					temp_activity["location"] = agent.get_attribute("location")
					temp_activity["current_node_id"] = agent.get_attribute("current_node_id")
					temp_activity["household_id"] = agent.get_attribute("household_id")
					temp_activity["home_node_id"] = agent.get_attribute("home_node_id")
					temp_activity["activy_name"] = act.name
					temp_activity["mask_behavior"] = agent.get_attribute("mask_wearing_type")
					logger.write_csv_data("activity_history.csv", temp_activity, id=True)
					agent.previous_activity = act.name
				actions = act.generate_actions(agent,kd_map,ts,rng)
				agent.actions.extend(actions)
				for action in actions:
					if action.__class__ is ActionMove:
						move_action_pool.append(action)
				break
		return move_action_pool


	def __str__(self):
		tempstring = "[Behavior]\n"
		tempstring += f"   Name = {self.name}"
		return tempstring