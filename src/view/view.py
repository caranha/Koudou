import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tk_fdialog
from typing import List
from src.model.behavioral.agent import Agent
from src.model.behavioral.simulation import Simulation
from src.model.map.map import Map
from src.view.btn_funcs import focus_random_agent, on_mouse_hold, on_mouse_release, on_zoom_in, on_zoom_out, scroll_linux, scroll_mouse_wheel

from src.view.draw import Draw
import src.view.util as util
from src.view.viewport import ViewPort

class View():
    def __init__(self, window_size=(1024, 768)):
        ### todo: move widget styles to style_config file ###
        style = {"bg_btn": "white",
                    "font_btn": "sans 10 bold",
                    "bg_log": "white",
                    "font_log": "sans 10 bold"}
        ### ###


        # root
        self.root = tk.Tk()
        geometry_str = util.make_geometry_string(self.root, window_size)

        #self.root.configure(background="black")
        self.root.title("Community Simulator")
        self.root.geometry(geometry_str)
        self.root.resizable(False, False)

        self.window_size = util.get_window_resolution(self.root, window_size[0], window_size[1])

        ## main bar and notebooks
        self.frame_bar = ttk.Frame(self.root)
        self.frame_nb = ttk.Notebook(self.root)


        self.buttons = {}
        self.set_main_bar()
        self.set_buttons_main_bar(style)

        ##### notebook tabs #####
        self.tab1 = ttk.Frame(self.frame_nb)
        self.tab2 = ttk.Frame(self.frame_nb)
        self.frame_nb.add(self.tab1, text='Main')
        self.frame_nb.add(self.tab2, text ='Settings')

        self.set_map_tab(style)

        self.view_port: ViewPort = None
        self.mouse_prev_position = None

    def init_viewport(self, min_coord, max_coord):
        self.view_port = ViewPort(
            height=self.canvas.winfo_height(),
            width=self.canvas.winfo_width(),
            wmin=min_coord,
            wmax=max_coord
        )


    def set_main_bar(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=39)

        self.frame_bar.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.frame_nb.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    def set_buttons_main_bar(self, style):
        self.buttons["map_load"] = tk.Button(self.frame_bar, bg=style["bg_btn"], font=style["font_btn"], text="Load Map")
        self.buttons["sim_run"] = tk.Button(self.frame_bar, bg=style["bg_btn"], font=style["font_btn"], text="Run")
        self.buttons["sim_step"] = tk.Button(self.frame_bar, bg=style["bg_btn"], font=style["font_btn"], text="Step")
        self.buttons["rnd_ag"] = tk.Button(self.frame_bar, bg=style["bg_btn"], font=style["font_btn"], text=f"Random Agent")

        for i, (key,val) in enumerate(self.buttons.items()):
            self.frame_bar.columnconfigure(i, weight=1)
            self.buttons[key].grid(row=0, column=i, sticky=(tk.N, tk.S, tk.E, tk.W))

    def set_map_tab(self, style):
        self.canvas_frame = tk.Frame(self.tab1)
        self.canvas = tk.Canvas(self.canvas_frame)

        self.zoom_in_btn = tk.Button(self.canvas, text='+', bg=style["bg_btn"], font=style["font_btn"])
        self.zoom_in_btn.place(relx= .95, rely=.01)
        self.zoom_out_btn = tk.Button(self.canvas, text='-', bg=style["bg_btn"], font=style["font_btn"])
        self.zoom_out_btn.place(relx= .95, rely=.01, y=self.zoom_in_btn.winfo_height()+20)
        # self.coord_label = tk.Label(self.canvas, text="", fg="Red", font=("Helvetica", 12), background="White")
        # self.coord_label.place(relx=.01, rely=.95)

        self.clock = tk.Label(self.canvas, text="", fg="Green", font=("Helvetica", 18), background="White")
        self.clock.place(relx=.01, rely=.01)

        self.canvas.pack(expand=True)
        self.canvas.config(width=self.window_size[0], height=self.window_size[1])

        self.canvas_frame.pack(expand=True)
        self.draw = Draw(canvas=self.canvas)

    ## main methods ##
    def main_loop(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()

    ## dialog methods
    def ask_load_file(self):
        filename = tk_fdialog.askopenfilename()
        return filename

    def btn_start_change_method(self, text, method):
        self.buttons["sim_run"]["text"]    = text
        self.buttons["sim_run"]["command"] = method


        self.buttons["sim_step"]["state"] = tk.NORMAL
        if text == "Pause": # auto-running
            self.buttons["sim_step"]["state"] = tk.DISABLED

    def draw_initial_osm_map(self, osm_map: Map):
        self.draw.draw_places(d_places=osm_map.d_places, viewport=self.view_port)
        self.draw.draw_roads(roads=osm_map.main_road, d_nodes=osm_map.d_nodes, route_nodes=osm_map.route_nodes, viewport=self.view_port)

    def draw_initial_agents(self, agents: List[Agent]):
        self.draw.draw_agents(agent_list=agents, viewport=self.view_port)

    def move_agents(self, agents: List[Agent]):
        self.draw.move_agents(agent_list=agents, viewport=self.view_port)

    def update_clock(self, new_time):
        self.clock.configure(text=new_time)

    def set_btn_funcs(self, rng, agents,  zoom_in, zoom_out, os, load_map, run_step, cmd_auto):
        if os == "Linux":
            self.canvas.bind("<Button>", lambda event: scroll_linux(event, zoom_in, zoom_out, self.view_port, self.canvas))
        else:
            self.canvas.bind("<MouseWheel>", lambda event: scroll_mouse_wheel(event, zoom_in, zoom_out, self.view_port, self.canvas))

        # window
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close())

        # buttons
        self.buttons["map_load"]["command"] = load_map
        self.buttons["sim_step"]["command"] = run_step
        self.buttons["sim_run"]["command"]  = cmd_auto
        self.buttons["rnd_ag"]["command"] = lambda: focus_random_agent(rng, self.view_port, agents, self.canvas)
        self.zoom_in_btn["command"] = lambda: on_zoom_in(zoom_in, self.view_port, self.canvas)
        self.zoom_out_btn["command"] = lambda: on_zoom_out(zoom_out, self.view_port, self.canvas)


        # canvas
        self.canvas.bind("<B1-Motion>"      , lambda event: on_mouse_hold(event, self))
        self.canvas.bind("<ButtonRelease-1>", lambda event: on_mouse_release(self))


if __name__ == "__main__":
    view = View()
    view.main_loop()
