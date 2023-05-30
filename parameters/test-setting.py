parameters = {
    "EXP_NAME":       "test_config_file",     # Name of the experiment, used for saving ther logs (logger not implemented yet) 
    "MAP":            "osm_files/test.osm", # Path for the osm file used for building the map
    "MAP_CACHE":      "cache/TX-To-TU.pkl", # Where to save the map cache
    "PATHFIND_CACHE": "cache/TX-pathfind.pkl", # where to save the pathfind cache


    "SEED":            101512, # Seed used for reproducing experiments
    "N_AGENTS":        100, # Number of agents in the simulation, the more agents, the longer it will take to execute
    "THREADS":         8, # How many CPUs should be used for pathfinding

    "BUILDING_TAGS":  "config/map/tsukuba-tu-building-data.csv", # Path to the file that describes the tags to be created for untagged buildings
    "BUSINESS":       "config/map/business.csv", # Path for the file that describes the open-hours for business
    "GRID_SIZE":      10, # Grid size used when calculating the centroid for buildings, NOT recommended to change
    "EVAC_CENTER" :   "config/map/evacuation_center.json", # Path for the file that describes where the evac centers should be
    "STEP_LENGTH" :   5, #Each step is one second,
    "MAX_STEPS"    :   60*60*24*7, # This is simulating for 7 weeks (49 days 24 hours, 60 minutes, 60 seconds),
    "LOG_LEVEL"     : "debug",

    "DISEASES": ["config/infection/covid.json"], # Path to the diseases that will be simualted, it will use this path and the config/infection/covid-infection.json

    "EVACUATION": {"DISTANCE":10, "SHARE_INFO_CHANCE": 0.8}, # Agents have 80% cahnce of sharing infor if they have a distance less than 10

    "SIM_CONFIG":{
        "condition" : ["config/behavioral/condition.csv",
                       "config/evacuation/condition_evac.csv",
                       "config/infection/condition_infection.csv"],

        "start_behavior" : "normal",

        "attributes" : {
            "basic"      : ["config/behavioral/attributes/attribute_basic.csv",
                            "config/evacuation/attributes/attribute_basic_evac.csv"],
            "option"     : ["config/behavioral/attributes/attribute_option.csv",
                            "config/evacuation/attributes/attribute_option_evac.csv"],
            "updateable" : ["config/evacuation/attributes/attribute_updateable.csv"],
            "schedule"   : ["config/behavioral/attributes/attribute_schedule.csv"],
            "profession" : ["config/behavioral/profession.csv"]
        },
        "behaviors" :{
            "normal"         : "config/behavioral/behavior/behavior_normal.csv",
            "evacuate"       : "config/evacuation/behavior/behavior_evacuate.csv",
            "evacuated"       : "config/evacuation/behavior/behavior_evacuated.csv",
            "self_isolation" : "config/infection/behavior/behavior_symptomatic.csv",
            "severe"         : "config/infection/behavior/behavior_severe.csv"
        }
    }
}
