import json
from typing import Dict, List
from src.model.behavioral.attribute.attribute import Attribute
from .infection import Infection
from src.model.behavioral.agent import Agent
from src.model.map.map import Map

from .disease import Disease


def initialize_infection(disease_files, population: List[Agent], rng, logger):
    diseases = []

    for file_name in disease_files:
        with open(file_name) as file:
            d_config = json.load(file)
        
        d = Disease(
            d_config["name"],
            d_config["symptoms"],
            d_config["attributes"],
            d_config["transition_states"],
            d_config["infection_file"],
            d_config["infectious_states"],
            d_config["infected_starting_state"],
            d_config["precautionary_measures"]
        )
        logger.write_log(str(d))
        diseases.append(d)
        initializate_disease_on_population(d, d_config["initialization"], population, rng, logger)

    return Infection(diseases)


def initializate_disease_on_population(disease: Disease, initialization: Dict, population: List[Agent], rng, logger):
    for ag in population:
        new_attr = Attribute(disease.name, "susceptible")
        ag.add_attribute(new_attr)

    if initialization["type"] == "absolute":
        qtd = initialization["value"]
    elif initialization["type"] == "percentage":
        qtd = len(population) * initialization["value"]
    infected_ags = rng.choice(population, qtd, replace = False)

    for agent in infected_ags:
        data = {}
        data["time"] = '00'
        data["time_stamp"] = '00'
        data["type"] = 'None'
        data["disease_name"] = 'disease'
        data["agent_id"] = agent.agent_id
        data["agent_profession"] = agent.get_attribute("profession")
        data["agent_location"] = agent.get_attribute("location")
        data["agent_node_id"] = agent.get_attribute("current_node_id")
        data["source_id"] = 'admin'
        data["source_profession"] = 'admin'
        data["source_location"] = 'admin'
        data["source_node_id"] = 'admin'
        data["current_mask"] = 'None'
        data["next_mask"] = agent.get_attribute("mask_wearing_type")
        logger.write_csv_data("new_infection.csv", data)

    for ag in infected_ags:
        ag.set_attribute(disease.name, initialization["state"])
        logger.write_log("Agent" + str(ag.agent_id) + " changed to state " + initialization["state"] + " of " + disease.name)
    

def infection_step(step_size: int, kd_map: Map, population: List[Agent], infection_module: Infection, rng,logger,ts):
    # next state of the infected agents
    for disease in infection_module.diseases.values():
        infected_agents = [ag for ag in population if ag.get_attribute(disease.name) != "susceptible"]
        for ag in infected_agents:
            infected_next_stage(step_size, ag, disease, rng, logger,ts)

    # infection to healthy agents
    for disease in infection_module.diseases.values():
        disease_transmission_verbose(step_size, kd_map, population, disease, rng, logger,ts)

def create_symptoms(step_size, ag: Agent, disease: Disease, rng, logger,ts):
    for symptom, sympt_attr in disease.symptoms.items():
        if (not ag.has_attribute(symptom)):
            symptom_chance = apply_time_scale(step_size, sympt_attr["scale"], sympt_attr["probability"])
            rand_value = rng.uniform(0.0,1.0,1)[0]
            if rand_value < symptom_chance:
                new_attr = Attribute(symptom, "symptomatic")
                ag.add_attribute(new_attr)
                data = {}
                data["time_stamp"] = ts.step_count
                data["disease_name"] = disease.name
                data["agent_id"] = ag.agent_id
                data["agent_profession"] = ag.get_attribute("profession")
                data["agent_location"] = ag.get_attribute("location")
                data["agent_node_id"] = ag.get_attribute("current_node_id")
                data["symptom"] = symptom
                data["state"] = "symptomatic"
                data['mask_state'] = ag.get_attribute('mask_wearing_type')
                logger.write_csv_data("symptom.csv", data)

def remove_symptoms(ag: Agent, disease: Disease, rng, logger, ts):
    for symptom in disease.symptoms:
        if (ag.has_attribute(symptom)):
            ag.update_attribute(symptom, "asymptomatic")
            data = {}
            data["time_stamp"] = ts.step_count
            data["disease_name"] = disease.name
            data["agent_id"] = ag.agent_id
            data["agent_profession"] = ag.get_attribute("profession")
            data["agent_location"] = ag.get_attribute("location")
            data["agent_node_id"] = ag.get_attribute("current_node_id")
            data["symptom"] = symptom
            data["state"] = "asymptomatic"
            data['mask_state'] = ag.get_attribute('mask_wearing_type')
            logger.write_csv_data("symptom.csv", data)

# To reduce the rate of infection
def mask_infection_chance(ag: Agent, disease: Disease):
    if disease.precautionary_measures.get('mask', 'measure_not_found') is 'measure_not_found':
        return 1
    mask_type = ag.get_attribute('mask_wearing_type')
    return disease.precautionary_measures.get('mask').get('infection_rate').get(mask_type)

# To determine agent's mask wearing behavior when disease state changed
def mask_behavior_determine(ag: Agent, disease: Disease, rng):
    if disease.precautionary_measures.get('mask', 'measure_not_found') is 'measure_not_found':
        return ag
    if_wear_mask = ag.get_attribute('if_wear_mask')
    mask_wearing_type = ag.get_attribute('mask_wearing_type')
    if if_wear_mask and mask_wearing_type == 'surgical_mask':  # wear mask has two option if it is surgical mask: surgical to n95
        rnd = rng.uniform(0.0, 1.0, 1)[0]
        stn95_chance = disease.precautionary_measures.get('mask').get('self_infected_masked').get('surgical_to_n95')
        if rnd < stn95_chance:  # true for chance behavior, false for no chance
            ag.set_attribute('mask_wearing_type', 'n95_mask')
    elif not if_wear_mask:  # not wear mask has three options: no change / no to n95 / no to surgical
        rnd = rng.uniform(0.0, 1.0, 1)[0]
        nts_chance = disease.precautionary_measures.get('mask').get('self_infected_unmasked').get('no_to_surgical')
        ntn95_chance = nts_chance + disease.precautionary_measures.get('mask').get('self_infected_unmasked').get('no_to_n95')
        if rnd < nts_chance:  # from no masking to surgical mask
            ag.set_attribute('if_wear_mask', True)
            ag.set_attribute('mask_wearing_type', 'surgical_mask')
        elif rnd < ntn95_chance:  # from no masking to n95 mask
            ag.set_attribute('if_wear_mask', True)
            ag.set_attribute('mask_wearing_type', 'n95_mask')
    else:  # already wear n95 mask
        return ag
    return ag

# To add false testing results of PCR
def false_PCR_test():
    pass

def infected_next_stage(step_size, ag: Agent, disease: Disease, rng, logger,ts):
    current_state = ag.get_attribute(disease.name)
    if (current_state == "symptomatic"):
        create_symptoms(step_size, ag, disease, rng, logger, ts)
    elif (current_state == "recovered"):
        remove_symptoms(ag, disease, rng, logger, ts)
    next_state = current_state
    if current_state in disease.transitions:
        rand_value = rng.uniform(0.0,1.0,1)[0]
        previous_chances = 0
        # mask_measure_chance = mask_infection_chance(ag, disease)
        for compartiment, attr in disease.transitions[current_state].items():
            chance = apply_time_scale(step_size, attr["scale"], attr["probability"])
            if rand_value < previous_chances + chance:
                next_state = compartiment
                data = {}
                data["time"] = ts.get_hour_min_str()
                data["time_stamp"] = ts.step_count
                data["disease_name"] = disease.name
                data["agent_id"] = ag.agent_id
                data["agent_profession"] = ag.get_attribute("profession")
                data["agent_location"] = ag.get_attribute("location")
                data["agent_node_id"] = ag.get_attribute("current_node_id")
                data["current_state"] = current_state
                data["next_state"] = next_state
                data["mask_behavior"] = ag.get_attribute("mask_wearing_type")
                logger.write_csv_data("disease_transition.csv", data, id=True)
                break
            previous_chances += chance

    else:
        print(f"Could not find transition for state {current_state} of disease {disease.name}")

    ag.set_attribute(disease.name, next_state)

def apply_time_scale(step_size, time_scale, chance):
    if time_scale == "per_second":
        return chance*step_size
    elif time_scale == "per_minute":
        return chance*step_size/60
    elif time_scale == "per_hour":
        return chance*step_size/(60*60)
    elif time_scale == "per_day":
        return chance*step_size/(60*60*24)


def log(infection_type,disease,infector,infectee,logger,ts, old_mask_behavior):
    data = {}
    data["time"] = ts.get_hour_min_str()
    data["time_stamp"] = ts.step_count
    data["type"] = infection_type
    data["disease_name"] = disease.name
    data["agent_id"] = infectee.agent_id
    data["agent_profession"] = infectee.get_attribute("profession")
    data["agent_location"] = infectee.get_attribute("location")
    data["agent_node_id"] = infectee.get_attribute("current_node_id")
    data["agent_lat"] = infectee.coordinate.lat
    data["agent_lon"] = infectee.coordinate.lon
    data["agent_home_node_id"] = infectee.get_attribute("home_node_id")
    data["agent_workplace_node_id"] = infectee.get_attribute("workplace_node_id")
    data["agent_workplace_type"] = infectee.get_attribute("workplace_type")
    data["agent_workplace_id"] = infectee.get_attribute("workplace_id")
    data["agent_current_activity"] = infectee.previous_activity
    data["current_mask"] = old_mask_behavior
    data["next_mask"] = infectee.get_attribute("mask_wearing_type")
    if(infector is None):
        data["source_id"] = "None"
        data["source_profession"] = "None"
        data["source_location"] = "None"
        data["source_node_id"] = "None"
        data["source_lat"] = "None"
        data["source_lon"] = "None"
        data["source_home_node_id"] = "None"
        data["source_workplace_node_id"] = "None"
        data["source_workplace_type"] = "None"
        data["source_workplace_id"] = "None"
        data["source_health"] = "None"
        data["source_current_activity"] = "None"
    else:   
        data["source_id"] = infector.agent_id
        data["source_profession"] = infector.get_attribute("profession")
        data["source_location"] = infector.get_attribute("location")
        data["source_node_id"] = infector.get_attribute("current_node_id")
        data["source_lat"] = infector.coordinate.lat
        data["source_lon"] = infector.coordinate.lon
        data["source_home_node_id"] = infector.get_attribute("home_node_id")
        data["source_workplace_node_id"] = infector.get_attribute("workplace_node_id")
        data["source_workplace_type"] = infector.get_attribute("workplace_type")
        data["source_workplace_id"] = infector.get_attribute("workplace_id")
        data["source_health"] = infector.get_attribute("covid")
        data["source_current_activity"] = infector.previous_activity
    logger.write_csv_data("new_infection.csv", data)

def disease_transmission(step_size: int, kd_map: Map, population: List[Agent], disease: Disease, rng, logger, ts):
    infected_ags = [ag for ag in population if ag.get_attribute(disease.name) in disease.infectious_states]
    #ags_by_location = {ag.get_attribute("current_node_id"): [] for ag in population}
    ags_by_location = {}
    for ag in population:
        if ag.get_attribute("current_node_id") not in ags_by_location.keys():
            ags_by_location[ag.get_attribute("current_node_id")] = []
        ags_by_location[ag.get_attribute("current_node_id")].append(ag)
    for ag in infected_ags:
        loc = ag.get_attribute("current_node_id")
        if kd_map.is_businesses_node(loc):
            business_infection(step_size, ag, ags_by_location[loc], disease, rng, logger, ts)
        elif kd_map.is_residences_node(loc):
            residence_infection(step_size, ag, ags_by_location[loc], disease, rng, logger, ts)
        elif kd_map.is_roads_node(loc):
            road_infection(step_size, kd_map, ag, ags_by_location, disease, rng, logger, ts)
        else:
            other_infection(step_size,ag, ags_by_location[loc], disease, rng, logger, ts)

def disease_transmission_verbose(step_size: int, kd_map: Map, population: List[Agent], disease: Disease, rng, logger, ts):

    # collect susceptible agents and group by location- print out purpose
    infected_ags_by_location = {}
    susceptible_ags_by_location = {}
    off_map = []
    for ag in population:        
        if (ag.get_attribute(disease.name) in disease.infectious_states):
            if ag.get_attribute("off_map") == True and ag.get_attribute("is_working_hour") == True and ag.get_attribute("current_node_id") == ag.get_attribute("workplace_node_id") : #don't include off map
                continue 
            else:
                if ag.get_attribute("current_node_id") not in infected_ags_by_location.keys():
                    infected_ags_by_location[ag.get_attribute("current_node_id")] = []
                infected_ags_by_location[ag.get_attribute("current_node_id")].append(ag)
        elif (ag.get_attribute(disease.name) == "susceptible"):
            if ag.get_attribute("off_map") == True and ag.get_attribute("is_working_hour") == True and ag.get_attribute("current_node_id") == ag.get_attribute("workplace_node_id") :
                off_map.append(ag) # separate off_map agent 
                continue
            if ag.get_attribute("current_node_id") not in susceptible_ags_by_location.keys():
                susceptible_ags_by_location[ag.get_attribute("current_node_id")] = []
            susceptible_ags_by_location[ag.get_attribute("current_node_id")].append(ag)

    off_map_infection(step_size, off_map, disease, rng, logger,ts)

    # loop by location so we could see
    for loc in infected_ags_by_location:
        infected_ag = infected_ags_by_location[loc]
        susceptible_ags = []
        if loc in susceptible_ags_by_location.keys():
            susceptible_ags = susceptible_ags_by_location[loc]
        # infect susceptible agents when they stay with infected agents at the same node
        for infector in infected_ag:
            if kd_map.is_businesses_node(loc):
                business_infection(step_size, infector, susceptible_ags, disease, rng, logger, ts)
            elif kd_map.is_residences_node(loc):
                residence_infection(step_size, infector, susceptible_ags, disease, rng, logger, ts)
            elif kd_map.is_roads_node(loc):
                road_infection(step_size, kd_map, infector, susceptible_ags_by_location, disease, rng, logger, ts)
            else:
                other_infection(step_size,infector, susceptible_ags, disease, rng, logger, ts)

def business_infection(step_size, infector:Agent, ag_same_location: List[Agent], disease, rng, logger,ts):
    infection_attr = disease.infection_method["businesses"]
    scale = infection_attr["scale"]
    prob = infection_attr["probability"]
    chance = apply_time_scale(step_size, scale, prob)
    for ag in ag_same_location:
        if ag.get_attribute(disease.name) != "susceptible": #Already infected
            continue
        mask_measure_chance = mask_infection_chance(ag, disease)
        if rng.uniform(0.0,1.0,1)[0] < chance * mask_measure_chance: # infect agent
            old_mask_behavior = ag.get_attribute("mask_wearing_type")
            ag = mask_behavior_determine(ag, disease, rng)
            ag.set_attribute(disease.name, disease.starting_state)
            log("business",disease,infector,ag,logger,ts, old_mask_behavior)

def residence_infection(step_size,infector:Agent, ag_same_location: List[Agent], disease, rng, logger,ts):
    infection_attr = disease.infection_method["residences"]
    scale = infection_attr["scale"]
    prob = infection_attr["probability"]
    chance = apply_time_scale(step_size, scale, prob)
    for ag in ag_same_location:
        # print(f"inf household {infector.get_attribute('household_id')} vs target household {ag.get_attribute('household_id')}")
        # print(f"scale = {scale}")
        # print(f"prob = {prob}")
        # print(f"chance = {chance}")
        if ag.get_attribute(disease.name) != "susceptible":  # Already infected
            continue
        if ag.get_attribute("household_id") != infector.get_attribute("household_id"): #needs to be in the same household
            continue
        mask_measure_chance = mask_infection_chance(ag, disease)
        if rng.uniform(0.0,1.0,1)[0] < chance * mask_measure_chance:  # infect agent
            old_mask_behavior = ag.get_attribute("mask_wearing_type")
            ag = mask_behavior_determine(ag, disease, rng)
            ag.set_attribute(disease.name, disease.starting_state)
            log("residential",disease, infector,ag,logger,ts, old_mask_behavior)

def off_map_infection(step_size, ag_same_location: List[Agent], disease, rng, logger,ts):
    infection_attr = disease.infection_method["off_map"]
    scale = infection_attr["scale"]
    prob = infection_attr["probability"]
    chance = apply_time_scale(step_size, scale, prob)
    for ag in ag_same_location:
        mask_measure_chance = mask_infection_chance(ag, disease)
        if rng.uniform(0.0,1.0,1)[0] < chance * mask_measure_chance:  # infect agent
            old_mask_behavior = ag.get_attribute("mask_wearing_type")
            ag = mask_behavior_determine(ag, disease, rng)
            ag.set_attribute(disease.name, disease.starting_state)
            log("off_map",disease, None,ag,logger,ts, old_mask_behavior)

def other_infection(step_size, infector:Agent, ag_same_location: List[Agent], disease, rng, logger,ts):
    infection_attr = disease.infection_method["other"]
    scale = infection_attr["scale"]
    prob = infection_attr["probability"]
    chance = apply_time_scale(step_size, scale, prob)

    for ag in ag_same_location:
        if ag.get_attribute(disease.name) != "susceptible":  # Already infected
            continue
        mask_measure_chance = mask_infection_chance(ag, disease)
        if rng.uniform(0.0,1.0,1)[0] < chance * mask_measure_chance:  # infect agent
            old_mask_behavior = ag.get_attribute("mask_wearing_type")
            ag = mask_behavior_determine(ag, disease, rng)
            ag.set_attribute(disease.name, disease.starting_state)
            log("other",disease, infector,ag,logger,ts, old_mask_behavior)
  
def road_infection(step_size, kd_map: Map, infected_ag, ags_by_location, disease, rng, logger,ts):
    infection_attr = disease.infection_method["roads"]
    scale = infection_attr["scale"]
    gradient = infection_attr["gradient_by_distance"]
    cc_prob = infection_attr["close_contact_probability"] 

    loc = infected_ag.get_attribute("current_node_id")
    coor = infected_ag.coordinate
    susceptible_ags = []
    if loc in ags_by_location.keys():
        susceptible_ags.extend(ags_by_location[loc])
    for conn in kd_map.d_nodes[loc].connections:        
        if (conn in ags_by_location.keys() and kd_map.is_roads_node(conn)):
            susceptible_ags.extend(ags_by_location[conn])

    for ag in susceptible_ags:
        if ag.get_attribute(disease.name) != "susceptible":  # Already infected
            continue
        dist = ag.coordinate.calculate_distance(coor.lat,coor.lon)
        prob = cc_prob + gradient*dist
        mask_measure_chance = mask_infection_chance(ag, disease)
        chance = apply_time_scale(step_size, scale, prob)
        if rng.uniform(0.0,1.0,1)[0] < chance * mask_measure_chance:  # infect agent
            old_mask_behavior = ag.get_attribute("mask_wearing_type")
            ag = mask_behavior_determine(ag, disease, rng)
            ag.set_attribute(disease.name, disease.starting_state)
            log("on_the_road",disease, infected_ag,ag,logger,ts, old_mask_behavior)

