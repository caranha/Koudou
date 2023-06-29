import pickle
import threading
import numpy as np

from pathlib import Path
from os import path, mkdir
from src.model.map.map import Map#join, exists
from src.util.paths import fromRoot
from src.util import time_stamp as ts

from src.view.view import View
from src.view.viewport import ViewPort

from src.logger import Logger

from src.model.map.map_manager import build_map

from src.model.behavioral.simulation import Simulation
from src.model.infection.infection_module import InfectionModule
from src.model.evacuation.evacuation_module import EvacuationModule

from src.model.behavioral.agent import Agent

class Controller():
    def __init__(self, parameters):
        self.d_param = parameters
        self.OS = self.d_param["OS"]

        self.logger: Logger = None
        self.view: View   = None
        self.map: Map    = None
        self.sim: Simulation    = None

        self.thread_finished = True
        self.rng = np.random.default_rng(seed=self.d_param["SEED"])
        self.step_length = self.d_param["STEP_LENGTH"]

        self.init_logger()
        self.logger.write_log("List of Parameters")
        self.logger.write_log("--------------------START--------------------")
        for key in self.d_param:
            self.logger.write_log(key)
        self.logger.write_log("--------------------END---------------------")
        
        '''
        if self.d_param["MAP_CACHE"] is not None and path.isfile(self.d_param["MAP_CACHE"]):
            self.logger.write_log("Found Map Cache")
            self.load_map(self.d_param["MAP_CACHE"])
        else:
            self.logger.write_log("Unable to find Map Cache")
            self.load_map(self.d_param["MAP"])
        '''

        self.load_map(self.d_param["MAP"])
        
        if self.d_param["SIM_CONFIG"]:
            self.logger.write_log("--------------------Loading Simulation--------------------")
            self.load_sim()
            self.logger.write_log("--------------------Finished Loading Simulation--------------------")

        # bindings
        if self.d_param["USE_VIEW"]:
            self.load_view()

    def print_map(self):
        self.print_msg(self.map)

    ## open and close ##
    def main_loop(self):
        if self.d_param["USE_VIEW"]:
            # self.step()
            self.view.main_loop()

        else:
            self.run_simulation()
            self.on_closing()

    def on_closing(self):
        if self.d_param["USE_VIEW"]:
            self.view.close()

        self.logger.close_files()
  
    ## load map
    def load_map(self, osm_file=None):
        if osm_file is None and  self.d_param["USE_VIEW"]:
            osm_file = self.view.ask_load_file()
        elif osm_file is None:
            raise Exception(f"Map file not specified!")

        filename = Path(osm_file).stem
        fileext  = Path(osm_file).suffix

        if fileext==".osm":
            self.print_msg(f"Loading map: {filename}{fileext}")
            # todo: evac center should be in a module
            self.map = build_map(osm_file,
                                 bldg_tags    = self.d_param["BUILDING_TAGS"],
                                 business_data= self.d_param["BUSINESS"],
                                 grid_size    = self.d_param["GRID_SIZE"],
                                 evacuation_center = self.d_param["EVAC_CENTER"])

            ## temp pickling it here since loading takes time
            if not path.exists("cache"):
                mkdir("cache")

            with open(fromRoot(path.join("cache",f"{filename}.pkl")), "wb") as file:
                pickle.dump(self.map, file)
        elif fileext==".pkl":
            self.print_msg(f"Loading cached map: {filename}{fileext}")
            with open(fromRoot(osm_file), "rb") as file:
                self.map = pickle.load(file)
        else:
            self.print_msg(f"Not a valid map file")
            return

    def load_view(self):
        self.view = View()
        self.view.init_viewport(self.map.min_coord.get_lon_lat(), self.map.max_coord.get_lon_lat())
        self.view.draw_initial_osm_map(self.map)
        self.view.draw_initial_agents(self.sim.agents)
        
        self.view.update_clock(ts.get_hour_min_str(self.sim.step_count))
        self.view.set_btn_funcs(
            self.rng,
            self.sim.agents,
            self.d_param["ZOOM_IN"],
            self.d_param["ZOOM_OUT"],
            self.d_param["OS"],
            lambda: self.load_map(),
            lambda: self.run_step(),
            lambda: self.cmd_auto() 
        )

    ## load sim
    def load_sim(self):
        self.sim = Simulation(config       = self.d_param["SIM_CONFIG"],
                              kd_map       = self.map,
                              rng          = self.rng,
                              logger       = self.logger,
                              agents_count = self.d_param["N_AGENTS"],
                              threads      = self.d_param["THREADS"],
                              report       = None
        )

        if self.d_param["DISEASES"]:
            # todo: we shouldnt pass thw whole simulator, just the necessary things
            # i guess just agents, but Im not changing this to avoid bugs
            self.logger.write_log("--------------------Loading Disease Module--------------------")
            infec_model = InfectionModule(
                parameters = self.d_param["DISEASES"],
                kd_sim     = self.sim,
                rng        = self.rng,
                logger     = self.logger
            )
            self.sim.modules.append(infec_model)
            self.logger.write_log("--------------------Finished Loading Disease Module--------------------")
                                

        if self.d_param["EVACUATION"]:
            self.logger.write_log("--------------------Loading Evacuation Module--------------------")
            evac_module = EvacuationModule(
                distance=self.d_param["EVACUATION"]["DISTANCE"],
                share_information_chance=self.d_param["EVACUATION"]["SHARE_INFO_CHANCE"], 
                logger = self.logger,
            )
            self.sim.modules.append(evac_module)
            self.logger.write_log("--------------------Finished Loading Disease Module--------------------")

    ## LOGGER
    def init_logger(self):
        self.logger = Logger(exp_name=self.d_param["EXP_NAME"], level=self.d_param["LOG_LEVEL"])

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

    ## SIM
    def step(self):
        self.thread = threading.Thread(target=self.run_step, args=())
        self.thread.start()

    def print_msg(self, msg):
        print(msg)

    def run_step(self):
        self.thread_finished = False
        # print("Processing... ", end="", flush=True)

        # LOGGING
        # infection summary
        ########################### LOGGING ###########################################
        summarized_attr = self.sim.summarized_attribute("covid")
        log_data = {}
        health_header = ["time_stamp","susceptible","exposed",
                  "asymptomatic","symptomatic","severe","recovered"]
        for h in health_header:
            log_data[h] = summarized_attr[h] if h in summarized_attr else 0
        
        log_data["time"] = ts.get_hour_min_str(self.sim.step_count)
        log_data["time_stamp"] = self.sim.step_count
        self.logger.write_csv_data("infection_summary.csv", log_data)

        # mask summary
        summarized_mask_attr = self.sim.summarized_attribute("mask_wearing_type")
        mask_log_data = {}
        mask_header = ["time", "time_stamp", "no_mask", "surgical_mask", "n95_mask"]
        for h in mask_header:
            mask_log_data[h] = summarized_mask_attr[h] if h in summarized_mask_attr else 0
        mask_log_data["time"] = ts.get_hour_min_str(self.sim.step_count)
        mask_log_data["time_stamp"] = self.sim.step_count
        self.logger.write_csv_data("mask_summary.csv", mask_log_data)

        # agent position
        summarized_attr = self.sim.summarized_attribute("location")
        log_data = {}
        log_data["time"] = ts.get_hour_min_str(self.sim.step_count)
        log_data["time_stamp"] = self.sim.step_count
        
        for k in summarized_attr.keys():
            log_data[k]   = summarized_attr[k]

        self.logger.write_csv_data("agent_position_summary.csv", log_data)

        ###########################################################################
        # STEP
        self.sim.step(step_length = self.step_length,
                      logger      = self.logger)

        # self.update_view() #todo: create an update loop, where we add move methods
        if self.d_param["USE_VIEW"]:
            self.view.move_agents(self.sim.agents)
            self.view.update_clock(ts.get_hour_min_str(self.sim.step_count))

        # print("Done!", flush=True)
        self.thread_finished = True


    def run_simulation(self):
        steps_in_a_minute =  (60)
        for d in range(0, self.d_param["MAX_STEPS"], self.d_param["STEP_LENGTH"]):
            self.run_step()
            if d%steps_in_a_minute == 0:
                minutes =  d//steps_in_a_minute
                self.print_msg(f"Running simulation... {minutes}/{self.d_param['MAX_STEPS']/steps_in_a_minute} minutes")

        self.print_msg(f"{d+self.d_param['STEP_LENGTH']}/{self.d_param['MAX_STEPS']} steps done")
        self.print_msg("")
        time_log = f"{(d)} steps, {(d)/60} minutes"
        self.logger.write_log(data=time_log, filename="time.txt")
        

    def run_auto(self):
        self.thread_finished = False
        while not self.thread_ask_stop:
            self.run_step()
        self.thread_finished = True

    def cmd_auto(self):
        self.view.btn_start_change_method(text="Pause", method=self.cmd_pause)
        self.thread = threading.Thread(target=self.run_auto, args=())
        self.thread_ask_stop = False
        
        
        self.thread.start()

    def cmd_pause(self):
        self.view.btn_start_change_method(text="Play ", method=self.cmd_auto)
        self.thread_ask_stop = True


if __name__ == "__main__":
    crtl = Controller()
    crtl.use_view()
    crtl.main_loop()
