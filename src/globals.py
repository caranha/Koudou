import pickle
import numpy as np

from src.logger import Logger
from pathlib import Path
from os import path, mkdir
from src.util.paths import fromRoot
from src.model.map.map_manager import build_map
from src.model.behavioral.simulation import Simulation
from src.model.infection.infection_module import InfectionModule
from src.model.evacuation.evacuation_module import EvacuationModule


class Globals:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(Globals)
            cls.instance.__init__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        self.params = None

        self.simulation = None
        self.map = None
        self.step_length = None
        self.rng = None
        self.logger = None

    def load_parameters(self, params):
        self.params = params

    def init(self):
        self.rng = np.random.default_rng(seed=self.params["SEED"])

        self.step_length = self.params["STEP_LENGTH"]

        self.init_logger()
        self.logger.write_log("List of Parameters")
        self.logger.write_log("--------------------START--------------------")
        for key in self.params:
            self.logger.write_log(key)
        self.logger.write_log("--------------------END---------------------")

        self.load_map(self.params["MAP"])

        if self.params["SIM_CONFIG"]:
            self.logger.write_log("--------------------Loading Simulation--------------------")
            self.load_sim()
            self.logger.write_log("--------------------Finished Loading Simulation--------------------")



    def init_test(self):
        pass


## LOGGER
    def init_logger(self):
        self.logger = Logger(exp_name=self.params["EXP_NAME"], level=self.params["LOG_LEVEL"])

        # mask
        header = ["time", "time_stamp", "no_mask", "surgical_mask", "n95_mask"]
        self.logger.add_csv_file("mask_summary.csv", header)

        # health
        header = ["time", "time_stamp","susceptible","exposed",
                  "asymptomatic","symptomatic","severe","recovered"]
        self.logger.add_csv_file("infection_summary.csv", header)

        # position
        header = ["time_stamp","location","count"]
        self.logger.add_csv_file("agent_position_summary.csv", header)

        # activity
        header = ["time", "time_stamp","agent_id","profession","location",
                  "current_node_id","household_id","home_node_id","activy_name", "mask_behavior", "event_id"]
        self.logger.add_csv_file("activity_history.csv", header)

        # new infections
        header = ["time", "time_stamp","type","disease_name","agent_id",
                  "agent_profession","agent_location","agent_node_id",
                  "source_id","source_profession","source_location","source_node_id",
                  "current_mask", "next_mask"]
        self.logger.add_csv_file("new_infection.csv", header)

        # infection transition
        header = ["time", "time_stamp","disease_name","agent_id","agent_profession",
                  "agent_location","agent_node_id","current_state","next_state", "mask_behavior", "event_id"]
        self.logger.add_csv_file("disease_transition.csv", header)

        header = ["time_stamp","disease_name","agent_id","agent_profession",
                  "agent_location","agent_node_id","symptom", "state", "mask_state"]
        self.logger.add_csv_file("symptom.csv", header)

        # evacuation
        header = ["time_stamp", "ag_id","evac_point_id","evac_occupation","evac_capacity", "total_evacuated"]
        self.logger.add_csv_file("evacuation.csv", header)

        # time stamp?
        header = ["time", "time_stamp","","",""]
        self.logger.add_csv_file("infection_transition.csv", header)

        # logs
        self.logger.add_file("log.txt")

        # logs
        self.logger.add_file("time.txt")


    ## load map
    def load_map(self, osm_file=None):
        if osm_file is None:
            raise Exception(f"Map file not specified!")

        filename = Path(osm_file).stem
        fileext  = Path(osm_file).suffix

        if fileext == ".osm":
            print(f"Loading map: {filename}{fileext}")
            # todo: evac center should be in a module
            self.map = build_map(osm_file,
                                 bldg_tags    = self.params["BUILDING_TAGS"],
                                 business_data= self.params["BUSINESS"],
                                 grid_size    = self.params["GRID_SIZE"],
                                 evacuation_center = self.params["EVAC_CENTER"])

            ## temp pickling it here since loading takes time
            if not path.exists("cache"):
                mkdir("cache")

            with open(fromRoot(path.join("cache",f"{filename}.pkl")), "wb") as file:
                pickle.dump(self.map, file)
        elif fileext==".pkl":
            print(f"Loading cached map: {filename}{fileext}")
            with open(fromRoot(osm_file), "rb") as file:
                self.map = pickle.load(file)
        else:
            print(f"Not a valid map file")

    ## load sim
    def load_sim(self):
        self.simulation = Simulation(config=self.params["SIM_CONFIG"],
                                     kd_map=self.map,
                                     rng=self.rng,
                                     logger=self.logger,
                                     agents_count=self.params["N_AGENTS"],
                                     threads=self.params["THREADS"],
                                     report=None
                                     )

        if self.params["DISEASES"]:
            # todo: we shouldnt pass thw whole simulator, just the necessary things
            # i guess just agents, but Im not changing this to avoid bugs
            self.logger.write_log("--------------------Loading Disease Module--------------------")
            infec_model = InfectionModule(
                parameters=self.params["DISEASES"],
                kd_sim=self.simulation,
                rng=self.rng,
                logger=self.logger
            )
            self.simulation.modules.append(infec_model)
            self.logger.write_log("--------------------Finished Loading Disease Module--------------------")

        if self.params["EVACUATION"]:
            self.logger.write_log("--------------------Loading Evacuation Module--------------------")
            evac_module = EvacuationModule(
                distance=self.params["EVACUATION"]["DISTANCE"],
                share_information_chance=self.params["EVACUATION"]["SHARE_INFO_CHANCE"],
                logger=self.logger,
            )
            self.simulation.modules.append(evac_module)
            self.logger.write_log("--------------------Finished Loading Disease Module--------------------")