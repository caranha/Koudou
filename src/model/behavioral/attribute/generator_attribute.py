import src.util.csv_reader as csv_reader
import numpy as np
from .attribute import Attribute,cast
from .attribute_updateable import AttributeUpdateable
from .attribute_option import AttributeOption
from .attribute_grouped_schedule import AttributeGroupedSchedule
from .attribute_schedule import AttributeSchedule


class GeneratorAttribute:
	def __init__(self,attribute_files,rng, logger):
		self.attributes = []		
		self.rng = rng
		self.basic = {}
		self.basic_sim = {}
		self.basic_household = {}
		self.option = {}	
		self.option_sim = {}
		self.option_household = {}
		self.updateable = {}
		self.updateable_sim = {}
		self.updateable_household = {}
		self.schedules = {}
		self.schedules_sim = {}
		self.schedules_household = {}
		self.professions = []
		self.counter = 0
		self.max_weight = 0
		for filepath in attribute_files["basic"]:
			self.load_basic_attribute(filepath, logger)

		for filepath in attribute_files["option"]:
			self.load_option_based_attribute(filepath, logger)
		
		#self.option = csv_reader.read_csv_as_dict(attribute_files["option"])
		for filepath in attribute_files["updateable"]:
			self.load_updatable_attribute(filepath, logger)

		for filepath in attribute_files["profession"]:
			self.load_profession(filepath, logger)

		for filepath in attribute_files["schedule"]:
			self.load_schedule_based_attribute(filepath, logger)

	def load_basic_attribute(self,file, logger):
		basic_attributes  = csv_reader.read_csv_as_dict(file)
		for attr in basic_attributes:
			temp = {}
			temp["value"] = attr["value"]
			temp["type"] = attr["type"]
			if (temp["value"] == "!random"):
				temp["max"] = cast(attr["max"],attr["type"])
				temp["min"] = cast(attr["min"],attr["type"])
			if (attr["target"] == "agent"):
				self.basic[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.basic")
			elif(attr["target"] == "simulation"):
				self.basic_sim[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.basic_sim")
			elif(attr["target"] == "household"):
				self.basic_household[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.basic_household")
			else:
				tempstring = f"Unknown target : {attr['target']} for attribute {attr['name']}\n"
				tempstring += f"available target: agent or simulation"
				raise ValueError(tempstring)

	def load_option_based_attribute(self,file, logger):
		option_based_attributes  = csv_reader.read_csv_as_dict(file)
		for attr in option_based_attributes:
			if (self.option.get(attr["name"]) is None):
				self.option[attr["name"]] = {}
				self.option[attr["name"]]["weights"] = []
				self.option[attr["name"]]["value"] = []
				self.option[attr["name"]]["options"] = []
				self.option[attr["name"]]["type"] = []
			self.option[attr["name"]]["weights"].append(float(attr["weight"]))
			self.option[attr["name"]]["value"].append(attr["value"])
			self.option[attr["name"]]["type"] = attr["type"]
			option = {}
			option["value"]= attr["value"]
			option["weight"]= float(attr["weight"])
			if (attr["target"] == "agent"):
				self.option[attr["name"]]["options"].append(option)
				logger.write_log(attr["name"] + " : " + attr["value"] + " added to generator_attribute.option")
			elif(attr["target"] == "simulation"):
				self.option_sim[attr["name"]]["options"].append(option)
				logger.write_log(attr["name"] + " : " + attr["value"] + " added to generator_attribute.option_sim")
			elif(attr["target"] == "household"):
				self.option_household[attr["name"]]["options"].append(option)
				logger.write_log(attr["name"] + " : " + attr["value"] + " added to generator_attribute.option_household")
			else:
				tempstring = f"Unknown target : {attr['target']} for attribute {attr['name']}\n"
				tempstring += f"available target: agent or simulation"
				raise ValueError(tempstring)

	def load_schedule_based_attribute(self,file, logger):
		schedule_based_attributes  = csv_reader.read_csv_as_dict(file)
		for attr in schedule_based_attributes:
			temp = {}
			temp["name"] = attr["name"]
			temp["start_time"] = int(attr["start_day"]) #days
			temp["start_time"] = (temp["start_time"]*24) + int(attr["start_hour"]) #convert to hours
			temp["start_time"] = (temp["start_time"]*60) + int(attr["start_minute"]) #convert to minutes
			temp["start_time"] = (temp["start_time"]*60) + int(attr["start_second"]) #convert to seconds
			temp["end_time"] = int(attr["end_day"]) #days
			temp["end_time"] = (temp["end_time"]*24) + int(attr["end_hour"]) #convert to hours
			temp["end_time"] = (temp["end_time"]*60) + int(attr["end_minute"]) #convert to minutes
			temp["end_time"] = (temp["end_time"]*60) + int(attr["end_second"]) #convert to seconds
			start = attr["start_day"] + ":" + attr["start_hour"] +  ":" + attr["start_minute"] +  ":" + attr["start_second"]
			end = attr["end_day"] + ":" +  attr["end_hour"] +  ":" + attr["end_minute"] +  ":" + attr["end_second"]
			if (attr["target"] == "agent"):
				self.schedules[attr["name"]] = temp
				logger.write_log(attr["name"] + " with start time " + start + " and end time " + end + " added to generator_attribute.schedules")
			elif(attr["target"] == "simulation"):
				self.schedules_sim[attr["name"]] = temp
				logger.write_log(attr["name"] + " with start time " + start + " and end time " + end +  " added to generator_attribute.schedules_sim")
			elif(attr["target"] == "household"):
				self.schedules_household[attr["name"]] = temp
				logger.write_log(attr["name"] + " with start time " + start + " and end time " + end +  " added to generator_attribute.schedules_household")
			else:
				tempstring = f"Unknown target : {attr['target']} for attribute {attr['name']}\n"
				tempstring += f"available target: agent or simulation"
				raise ValueError(tempstring)

	def load_updatable_attribute(self,file, logger):
		updateable_attributes  = csv_reader.read_csv_as_dict(file)
		for attr in updateable_attributes:
			temp  = {}
			temp["name"] = attr["name"]
			temp["type"] = attr["type"]
			temp["max"] = cast(attr["max"],attr["type"])
			temp["min"] = cast(attr["min"],attr["type"])
			temp["default_max"] = cast(attr["default_max"],attr["type"])
			temp["default_min"] = cast(attr["default_min"],attr["type"])
			temp["step_update"] = cast(attr["step_update"],attr["type"])
			if (attr["target"] == "agent"):
				self.updateable[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.updateable")
			elif(attr["target"] == "simulation"):
				self.updateable_sim[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.updateable_sim")
			elif(attr["target"] == "household"):
				self.updateable_household[attr["name"]] = temp
				logger.write_log(attr["name"] + " added to generator_attribute.updateable_household")
			else:
				tempstring = f"Unknown target : {attr['target']} for attribute {attr['name']}\n"
				tempstring += f"available target: agent or simulation"
				raise ValueError(tempstring)

	def load_profession(self,file, logger):
		professions  = csv_reader.read_csv_as_dict(file)
		for attr in professions:
			profession = {}
			profession["name"] = attr["name"]
			profession["place"] = attr["place"]
			profession["min_workhour"] = int(attr["min_workhour"])
			profession["max_workhour"] = int(attr["max_workhour"])
			profession["min_workday"] = int(attr["min_workday"])
			profession["max_workday"] = int(attr["max_workday"])
			profession["min_start_hour"] = int(attr["min_start_hour"])
			profession["max_start_hour"] = int(attr["max_start_hour"])
			profession["weight"] = int(attr["weight"])
			profession['no_mask'] = float(attr['no_mask'])
			profession['surgical_mask'] = float(attr['surgical_mask'])
			profession['n95_mask'] = float(attr['n95_mask'])
			self.max_weight += profession["weight"]
			profession["off_map"] = attr["off_map"]
			profession["schedule"] = []
			if attr["schedule"] == "weekday": 
				profession["schedule"] = ["Mon","Tue","Wed","Thu","Fri"]
			elif attr["schedule"] == "weekend": 
				profession["schedule"] = ["Sat","Sun"]
			elif attr["schedule"] == "everyday": 
				profession["schedule"] = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
			else: 
				profession["schedule"] = attr["schedule"].split(",")
			profession["schedule"]= np.array(profession["schedule"])
			self.professions.append(profession)
			logger.write_log(attr["name"] + " schedule ("+ attr["schedule"] + ") added to generator_attribute.profession[schedule]")

	def generate_household_attribute(self,agents,kd_map, logger):
		temp_agents = agents.copy()
		self.rng.shuffle(temp_agents,axis = 0)
		agent_by_household = []
		household_id = 0
		while len(temp_agents) > 0:

			family_size = self.rng.integers(1,4,1)[0]
			# get random residence (need to develop household)
			residence = kd_map.get_random_residence(self.rng)

			# setup initial coordinate
			home_node = kd_map.get_node(residence.node_id)
			temp = []
			for i in range(0,family_size):
				if len(temp_agents) <= 0:
					break
				agent = temp_agents.pop(0)
				agent.coordinate =  home_node.coordinate.clone()

				# add home node id
				agent.add_attribute(Attribute("location","home","string"))
				agent.add_attribute(Attribute("home_id",residence.id,"string"))
				agent.add_attribute(Attribute("home_node_id",residence.node_id,"string"))
				agent.add_attribute(Attribute("last_node_id",residence.node_id,"string"))
				agent.add_attribute(Attribute("current_node_id",residence.node_id,"string"))
				agent.add_attribute(Attribute("household_id",household_id,"int"))
				temp.append(agent)

			household_id += 1
			agent_by_household.append(temp)
		logger.write_log("Added " + str(household_id) + " households")

		logging = 1
		for household in agent_by_household:
			
			# add basic attribute
			for attr in self.basic_household:
				shared_attr = None
				if (self.basic_household[attr]["value"] == "!random"):
					shared_attr = Attribute(attr,self.rng.uniform(self.basic_household[attr]["min"],self.basic_household[attr]["max"]),self.basic_household[attr]["type"])
				else:
					shared_attr = Attribute(attr,self.basic_household[attr]["value"],self.basic_household[attr]["type"])
				for agent in household:
					agent.add_attribute(shared_attr)
				if logging:
					logger.write_log("Added " + shared_attr.name + " to agents")
				

			# add updateable attribute
			for key in self.updateable_household:
				attr = self.updateable_household[key]
				shared_attr = AttributeUpdateable(key, self.rng.uniform(attr["default_min"],attr["default_max"],1)[0], attr["min"], attr["max"], attr["step_update"], attr["type"])
				for agent in household:
					agent.add_attribute(shared_attr)
				if logging:
					logger.write_log("Added " + shared_attr.name + " to agents")

			# add option based attribute
			for key in self.option_household:
				value = self.rng.choice(self.option_household[key]["value"],1,p=self.option_household[key]["weights"])[0]
				shared_attr = AttributeOption(key,value,self.option_household[key]["options"],self.option_household[key]["type"])
				for agent in household:
					agent.add_attribute(shared_attr)
				if logging:
					logger.write_log("Added " + shared_attr.name + " to agents")

			for key in self.schedules_household:
				shared_attr = AttributeSchedule(key, self.schedules_household[key]["start_time"],self.schedules_household[key]["end_time"])
				for agent in household:
					agent.add_attribute(shared_attr)
				if logging:
					logger.write_log("Added " + shared_attr.name + " to agents")
			logging = 0

	def generate_attribute(self,agent,kd_map, rng, logger, logging):
		# add basic attribute
		for attr in self.basic:
			if (self.basic[attr]["value"] == "!random"):
				agent.add_attribute(Attribute(attr,self.rng.uniform(self.basic[attr]["min"],self.basic[attr]["max"]),self.basic[attr]["type"]))
			else:
				agent.add_attribute(Attribute(attr,self.basic[attr]["value"],self.basic[attr]["type"]))
			if logging: logger.write_log("Added " + attr + " to agents")

		# add updateable attribute
		for key in self.updateable:
			attr = self.updateable[key]
			agent.add_attribute(AttributeUpdateable(key, self.rng.uniform(attr["default_min"],attr["default_max"],1)[0], attr["min"], attr["max"], attr["step_update"], attr["type"]))
			if logging:
					logger.write_log("Added " + key + " to agents")

		# add option based attribute
		for key in self.option:
			value = self.rng.choice(self.option[key]["value"],1,p=self.option[key]["weights"])[0]
			agent.add_attribute(AttributeOption(key,value,self.option[key]["options"],self.option[key]["type"]))
			if logging:
					logger.write_log("Added " + key + " to agents")

		for key in self.schedules:
			agent.add_attribute(AttributeSchedule(key, self.schedules[key]["start_time"],self.schedules[key]["end_time"]))
			if logging:
					logger.write_log("Added " + key + " to agents")

		# get profession for this agent (not random but iteratively)
		temp = None
		rnd = rng.integers(self.max_weight)
		cumulative = 0
		for prof in self.professions:
			cumulative += prof["weight"]
			if rnd < cumulative:
				temp = prof
				break

		# add mask_wearing attribute (random)
		no_mask_level = temp['no_mask']
		surgical_mask_level = no_mask_level + temp['surgical_mask']
		# n95_mask_level = surgical_mask_level + temp['n95_mask']
		rnd = rng.uniform(0.0, 1.0, 1)[0]
		if rnd < no_mask_level:
			agent.add_attribute(Attribute('if_wear_mask', False, 'bool'))
			agent.add_attribute(Attribute('mask_wearing_type', 'no_mask', 'string'))
		elif rnd < surgical_mask_level:
			agent.add_attribute(Attribute('if_wear_mask', True, 'bool'))
			agent.add_attribute(Attribute('mask_wearing_type', 'surgical_mask', 'string'))
		else:
			agent.add_attribute(Attribute('if_wear_mask', True, 'bool'))
			agent.add_attribute(Attribute('mask_wearing_type', 'n95_mask', 'string'))

		# assign concern level to 1 for all agents
		agent.add_attribute(Attribute('concern_level', 1, 'float'))

		#calculate start time, end time, etc
		start_time = self.rng.integers(temp["min_start_hour"],temp["max_start_hour"]+1,1)[0]
		workhour = self.rng.integers(temp["min_workhour"],temp["max_workhour"]+1,1)[0]
		end_time = (start_time + workhour)%24
		workday = self.rng.integers(temp["min_workday"],temp["max_workday"]+1,1)[0]

		# randomize day
		workdays = temp["schedule"]
		self.rng.shuffle(workdays,axis = 0)
		workdays = workdays[:workday]
		#------just for sorting from mon to sun (cosmetic for printing)------
		temp2 = []
		for x in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]:
			if x in workdays:
				temp2.append(x)
		workdays = temp2		
		#---------------------------sorting done-----------------------------

		#get random workplace
		business = kd_map.get_random_business(temp["place"], 1, self.rng)[0]
		
		# generate profession related attribute
		agent.add_attribute(Attribute("profession",temp["name"],"string"))
		agent.add_attribute(Attribute("workplace_type",temp["place"],"string"))
		agent.add_attribute(Attribute("start_time",start_time,"int"))
		agent.add_attribute(Attribute("end_time",end_time,"int"))
		agent.add_attribute(Attribute("workhour",workhour,"int"))
		agent.add_attribute(Attribute("workday",workday,"int"))
		agent.add_attribute(Attribute("schedule", ",".join(workdays),"string"))
		agent.add_attribute(Attribute("off_map", temp["off_map"],"bool"))
		agent.add_attribute(Attribute("workplace_id",business.id,"string"))
		agent.add_attribute(Attribute("workplace_node_id",business.node_id,"string"))
		if logging:
			logger.write_log("Added the following profession related attributes to agents")
			logger.write_log("workplace type, start time, end time, workhour, workday, schedule, off_map, workplace_id, workplace_node_id")

		# generate and add schedule attribute
		profession = AttributeGroupedSchedule("is_working_hour")
		for day in workdays:
			profession.add_schedule(AttributeSchedule(f"work-{day}", start_time*3600,end_time*3600, day_str = day,repeat = True))
		agent.add_attribute(profession)
		if logging:
			logger.write_log("Added profession to agents")

		return agent

	def generate_attribute_for_simulation(self, kd_sim, logger):
		# add basic attribute
		for attr in self.basic_sim:
			kd_sim.add_attribute(Attribute(attr,self.basic_sim[attr]["value"],self.basic_sim[attr]["type"]))
			logger.write_log(attr + " added to simulation.attributes")

		# add updateable attribute
		for key in self.updateable_sim:
			attr = self.updateable_sim[key]
			kd_sim.add_attribute(AttributeUpdateable(key, self.rng.uniform(attr["default_min"],attr["default_max"],1)[0], attr["min"], attr["max"], attr["step_update"], attr["type"]))
			logger.write_log(key + " added to simulation.attributes")

		# add option based attribute
		for key in self.option_sim:
			value = self.rng.choice(self.option_sim[key]["value"],1,p=self.option_sim[key]["weights"])[0]
			kd_sim.add_attribute(AttributeOption(key,value,self.option_sim[key]["options"],self.option_sim[key]["type"]))
			logger.write_log(key + " added to simulation.attributes")

		for key in self.schedules_sim:
			kd_sim.add_attribute(AttributeSchedule(key, self.schedules_sim[key]["start_time"],self.schedules_sim[key]["end_time"]))
			logger.write_log(key + " added to simulation.attributes")
		
	def __str__(self):
		tempstring = "[Attribute Generator]\n\n"
		tempstring += "-----------------------------------------------\n"
		tempstring += "| Agent's attributes                          |\n"
		tempstring += "-----------------------------------------------\n"
		tempstring += f" Basic attributes = {len(self.basic)}\n"
		for x in self.basic:
			if (self.basic[x]['value']!= "!random"):
				tempstring+= f"   + {x} : {self.basic[x]['value']}({self.basic[x]['type']})\n"
			else:
				tempstring+= f"   + {x} : random({self.basic[x]['min']}-{self.basic[x]['max']})({self.basic[x]['type']})\n"
		tempstring += f"\n"
		tempstring += f" Option based attributes = {len(self.option)}\n"
		for x in self.option:
			tempstring+= f"   + {x} ({self.option[x]['type']}):\n"
			if self.option[x].get("default") is not None:
				tempstring+= f"     - Default Value = {self.option[x]['default']}\n"
			for option in self.option[x]["options"]:
				tempstring+= f"     - {option['value']} : {option['weight']}\n"
		tempstring += f"\n"
		tempstring += f" Updateable attributes = {len(self.updateable)}\n"
		for key in self.updateable:
			x = self.updateable[key]
			tempstring+= f"   + {key} ({x['type']}): \n"
			tempstring+= f"     - range            : {x['min']} - {x['max']} \n"
			tempstring+= f"     - initialization   : {x['default_min']} - {x['default_max']}\n"
			tempstring+= f"     - update (seconds) : {x['step_update']}\n"
			if (x.get("notes") is not None):
				tempstring+= f"     - notes            : {x['notes']}\n"
		tempstring += f"\n"
		tempstring += f" Scheduled attributes = {len(self.schedules)}\n"
		for key in self.schedules:
			x = self.schedules[key]
			tempstring+= f"   + {key}: \n"
			tempstring+= f"     - start          : {x['start_time']}\n"
			tempstring+= f"     - end            : {x['end_time']}\n"
		tempstring += f"\n"
		tempstring += f" Professions = {len(self.professions)}\n"
		for profession in self.professions:
			tempstring += f"   + {profession['name']} :\n"
			tempstring += f"     - place         : {profession['place']}\n"
			tempstring += f"     - working days  : {profession['min_workday']} - {profession['max_workday']} days\n"
			tempstring += f"     - duration      : {profession['min_workhour']} - {profession['max_workhour']} hours\n"
			tempstring += f"     - starting hour : {profession['min_start_hour']} - {profession['max_start_hour']} o'clock\n"
			tempstring += f"     - weight        : {profession['weight']}\n"
			if profession["off_map"].lower() == "true":
				tempstring += f"     - off_map        : True\n"
			else:
				tempstring += f"     - off_map        : False\n"
			tempstring += f"     - schedule      : {','.join(profession['schedule'])}\n"
		tempstring += "-----------------------------------------------\n"
		tempstring += "| simulator's attributes                      |\n"
		tempstring += "-----------------------------------------------\n"
		tempstring += f" Basic attributes = {len(self.basic_sim)}\n"
		for x in self.basic_sim:
			tempstring+= f"   + {x} : {self.basic_sim[x]['value']}({self.basic_sim[x]['type']})\n"
		tempstring += f"\n"
		tempstring += f" Option based attributes = {len(self.option_sim)}\n"
		for x in self.option_sim:
			tempstring+= f"   + {x} ({self.option_sim[x]['type']}):\n"
			if self.option_sim[x].get("default") is not None:
				tempstring+= f"     - Default Value = {self.option_sim[x]['default']}\n"
			for option in self.option_sim[x]["options"]:
				tempstring+= f"     - {self.option_sim['value']} : {option['weight']}\n"
		tempstring += f"\n"
		tempstring += f" Updateable attributes = {len(self.updateable_sim)}\n"
		for key in self.updateable_sim:
			x = self.updateable_sim[key]
			tempstring+= f"   + {key} ({x['type']}): \n"
			tempstring+= f"     - range            : {x['min']} - {x['max']} \n"
			tempstring+= f"     - initialization   : {x['default_min']} - {x['default_max']}\n"
			tempstring+= f"     - update (seconds) : {x['step_update']}\n"
			if (x.get("notes") is not None):
				tempstring+= f"     - notes            : {x['notes']}\n"
		tempstring += f" Scheduled attributes = {len(self.schedules_sim)}\n"
		for key in self.schedules_sim:
			x = self.schedules_sim[key]
			tempstring+= f"   + {key}: \n"
			tempstring+= f"     - start          : {x['start_time']}\n"
			tempstring+= f"     - end            : {x['end_time']}\n"
		tempstring += f"\n"
		return tempstring
