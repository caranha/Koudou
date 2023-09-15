import pickle
import threading
import numpy as np
import pandas as pd

from pathlib import Path
from os import path, mkdir
from src.model.map.map import Map#join, exists
from src.util.paths import fromRoot
from src.util import time_stamp as ts
from src.globals import Globals

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

        #todo: view need to be instantited before
        if self.d_param["MAP"] is None and self.d_param["USE_VIEW"]:
            self.d_param["MAP"] = self.view.ask_load_file()

        self.globals = Globals()
        self.globals.load_parameters(self.d_param)
        self.globals.init()

        self.logger: Logger = self.globals.logger
        self.view: View   = None
        self.map: Map    = self.globals.map
        self.sim: Simulation    = self.globals.simulation

        self.thread_finished = True
        self.rng = self.globals.rng
        self.step_length = self.globals.step_length
        
        '''
        if self.d_param["MAP_CACHE"] is not None and path.isfile(self.d_param["MAP_CACHE"]):
            self.logger.write_log("Found Map Cache")
            self.load_map(self.d_param["MAP_CACHE"])
        else:
            self.logger.write_log("Unable to find Map Cache")
            self.load_map(self.d_param["MAP"])
        '''

        # bindings
        if self.d_param["USE_VIEW"]:
            self.load_view()


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
            lambda: self.globals.load_map(),
            lambda: self.run_step(),
            lambda: self.cmd_auto() 
        )


    ## SIM
    def step(self):
        self.thread = threading.Thread(target=self.run_step, args=())
        self.thread.start()


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
        self.create_agentslocation_file()
        steps_in_a_minute =  (60)
        for d in range(0, self.d_param["MAX_STEPS"], self.d_param["STEP_LENGTH"]):
            self.run_step()
            if d%steps_in_a_minute == 0:
                minutes = d//steps_in_a_minute
                print(f"Running simulation... {minutes}/{self.d_param['MAX_STEPS']/steps_in_a_minute} minutes")

        print(f"{d+self.d_param['STEP_LENGTH']}/{self.d_param['MAX_STEPS']} steps done\n")
        time_log = f"{(d)} steps, {(d)/60} minutes"
        self.logger.write_log(data=time_log, filename="time.txt")
        
    def create_agentslocation_file(self):
        df=pd.DataFrame(data=[["id", "coordinate"]])
        df.to_csv("location.csv", index=False,header=False)

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
