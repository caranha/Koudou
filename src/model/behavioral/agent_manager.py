import csv
from .attribute.generator_attribute import GeneratorAttribute
from src.util.csv_reader import read_csv_as_dict
from src.model.behavioral.activity.condition import Condition
from src.model.behavioral.activity.activity import Activity
from src.model.behavioral.activity.action_move import ActionMove
from src.model.behavioral.activity.action_wait import ActionWait
from .agent import Agent
#from src.model.behavioral.activity.reward import Reward
def load_attributes_generator(file_names,rng):
	return GeneratorAttribute(file_names,rng)

def load_conditions(condition_file):
	data = read_csv_as_dict(condition_file)
	conditions = {}
	for x in data:
		if x["value"] == "$random":
			conditions[x["name"]] = Condition(x["name"],x["attribute"],x["value"],x["operator"])
		else:
			conditions[x["name"]] = Condition(x["name"],x["attribute"],x["value"],x["operator"])
	return conditions
	
def generate_agents(attribute_generator,count):
	agents = []
	for x in range(0,count):
		agent = Agent(x)
		attribute_generator.generate_attribute(agent)
		agents.append(agent)
	return agents

def load_activities(activity_file,conditions_dict, rng):
	data = read_csv_as_dict(activity_file)
	activities = []
	for x in data:
		act = Activity(x["name"])
		for y in x["conditions"].split(","):
			act.add_condition(conditions_dict[y])
		for y in x["actions"].split(","):
			temp = y.split(":")
			if (temp[0].lower() == "wait"):
				act.add_action(ActionWait(f"Wait-{x['name']}",temp[1]))
			elif (temp[0].lower()=="move"):
				act.add_action(ActionMove(f"Move-{temp[1]}",temp[1]))
			elif (temp[0].lower()=="modify_attribute"):
				act.add_action(ActionMove(f"Move-{temp[1]}",temp[1]))
		activities.append(act)
	return activities

def test():
	print("test")
