import argparse

from src.utils.parser import load_parameters
from src.view.btn_funcs import on_zoom_in, on_zoom_out
from src.view.view import View
from PIL import Image
import tkcap
from os import path, mkdir, remove
from pathlib import Path
from src.model.map.map_manager import build_map
import pickle

file_path = "parameters/default.py"
file_name = "temp"
zoom_level = .2


def save_as_png(canvas,fileName):
    # save postscipt image 
    canvas.postscript(file = fileName + '.eps') 
    # use PIL to convert to PNG 
    img = Image.open(fileName + '.eps') 
    img.save(fileName + '.png', 'png') 
    remove(fileName + '.eps')

def load_map(d_param, osm_file=None):

    filename = Path(osm_file).stem
    fileext  = Path(osm_file).suffix

    if fileext==".osm":
        map = build_map(osm_file,
            bldg_tags    = d_param["BUILDING_TAGS"],
            business_data= d_param["BUSINESS"],
            grid_size    = d_param["GRID_SIZE"],
            evacuation_center = d_param["EVAC_CENTER"]
        )

        ## temp pickling it here since loading takes time
        if not path.exists("cache"):
            mkdir("cache")

        with open(path.join("cache",f"{filename}.pkl"), "wb") as file:
            pickle.dump(map, file)
    elif fileext==".pkl":
        with open(osm_file, "rb") as file:
            map = pickle.load(file)
    else:
        map = None
    
    return map

def main():
    parameters = load_parameters(file_path)

    if parameters["MAP_CACHE"] is not None and path.isfile(parameters["MAP_CACHE"]):
        osm_file = parameters["MAP_CACHE"]
    else:
        osm_file = parameters["MAP"]

    map = load_map(parameters, osm_file)

    view = View()
    view.init_viewport(map.min_coord.get_lon_lat(), map.max_coord.get_lon_lat())
    view.draw_initial_osm_map(map)
    on_zoom_out(zoom_level, view.view_port, view.draw.canvas)

    cap = tkcap.CAP(view.root)     # master is an instance of tkinter.Tk
    cap.capture(f"{file_name}.png", True, True) 

    save_as_png(view.draw.canvas, file_name)


if __name__ == "__main__":
    main()