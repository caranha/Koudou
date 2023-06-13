import numpy as np

class Draw():
    def __init__(self, canvas):
        self.canvas = canvas


    ## drawing methods
    def draw_places(self, d_places, viewport):
        for id, place in d_places.items():
            place = place.render_info

            path_trans = [viewport.apply(*c.get_lon_lat()) for c in place.coords]
            path_flat = [e for c in path_trans for e in c]
            clon, clat = viewport.apply(*place.center.get_lon_lat())

            w=viewport.s*0.000015
            if "building" in place.tags.keys():
                if len(path_flat)>=6:
                    #print(f"drawing {id} {path_flat[:4]}")
                    self.canvas.create_polygon(path_flat, outline=place.outline, fill=place.fill, width=w)
                    r=viewport.s*0.000015
                    self.canvas.create_oval(clon-r, clat-r, clon+r, clat+r, fill="black")
                else:
                    1#print("not renderable")
            elif "natural" in place.tags.keys():
                self.canvas.create_polygon(path_flat, outline=place.outline, fill=place.fill, width=w)
            elif "leisure" in place.tags.keys():
                self.canvas.create_polygon(path_flat, outline=place.outline, fill=place.fill, width=w)
            elif "amenity" in place.tags.keys():
                self.canvas.create_polygon(path_flat, outline=place.outline, fill=place.fill, width=w)
            # elif 'highway' in place.tags.keys():
            #     for (lon_a, lat_a), (lon_b, lat_b) in zip(path[:-1], path[1:]):
            #         self.canvas.create_line(lon_a, lat_a, lon_b, lat_b, fill="grey", width=3)
            else:#note: equivalent to "others" in epidemicon
                #self.canvas.create_polygon(path_flat, outline=place.outline, fill="pink", width=2)
                pass
    def draw_roads(self, roads, d_nodes, viewport):
        for road in roads:
            lon_a, lat_a = viewport.apply(*road.coordinate.get_lon_lat())

            conn_tmp = np.array(road.connections) #maybe refactor all lists to numpy array?
            conn_filtered = conn_tmp[conn_tmp<road.id] #dont draw twice
            for conn_id in conn_filtered:
                conn = d_nodes[conn_id]
                lon_b, lat_b = viewport.apply(*conn.coordinate.get_lon_lat())
                if "centroid" in conn.tags:
                    self.canvas.create_line(lon_a, lat_a, lon_b, lat_b, fill="black", width=1)
                else:
                    self.canvas.create_line(lon_a, lat_a, lon_b, lat_b, fill="grey", width=3)

    def draw_agents(self, agent_list, viewport):
        for agent in agent_list:
            lon, lat = viewport.apply(*agent.coordinate.get_lon_lat())
            r=viewport.s*0.00005
            oval = self.canvas.create_oval(lon - r, lat - r, lon + r, lat + r, fill=agent.color, tag=agent.id)
            agent.oval = oval

    def move_agents(self, agent_list, viewport):
        i=0
        for agent in agent_list:
            # world coordinate to view coordinate
            lon, lat = viewport.apply(*agent.coordinate.get_lon_lat())
            # currlon, currlat = viewport.apply(*agent.coordinate.get_lon_lat())
            # prevlon, prevlat = viewport.apply(*agent.prev_coordinate.get_lon_lat())


            # get distance
            x1,y1,x2,y2 = self.canvas.coords(agent.oval)
            x = x1 + ((x2-x1)/2)
            y = y1 + ((y2-y1)/2)

            # move
            self.canvas.move(agent.oval, (lon-x), (lat-y))
            # self.canvas.move(agent.oval, (currlon-prevlon), (currlat-prevlat))

            # update color
            self.canvas.itemconfig(agent.oval, fill=agent.color)
