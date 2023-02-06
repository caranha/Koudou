import json
import time
from src.model.map.road import Road
from .place import Place
from .residence import Residence
from .business import Business
from .render_info import Render_info
from .coordinate import Coordinate
from .way import Way
from .osm_handler import OSMHandler
from .map import Map
from .node import Node
import numpy as np
from typing import List
import math
import csv
#list of function here

#def connect_buildings

#def clean_up_road

def build_map(osm_file_path, bldg_tags, business_data, grid_size=10,evacuation_center=None):
	print("starting building Map")
	st = time.time()

	osm_map = OSMHandler()
	osm_map.apply_file(osm_file_path)
	osm_map.set_bounding_box(osm_file_path)

	nodes = []
	for n in osm_map.nodes:
		coord = Coordinate(n["location"]["lat"], n["location"]["lon"])
		tags = {t[0]: t[1] for t in n["tags"]}
		nodes.append(Node(n["id"], tags, coord))

	ways = []
	for w in osm_map.ways:
		tags = {t[0]: t[1] for t in w["tags"]}
		n = [n["ref"] for  n in w["nodes"]]
		ways.append(Way(w["id"], tags, n))

	kd_map = Map(osm_map.bounding_box, nodes, ways)

	print(f"Finished getting nodes and ways ({time.time() - st}s) ")
	st = time.time()

	build_node_connections(kd_map) #generate the connection between nodes

	road_nodes, non_road_nodes = separate_nodes(kd_map)	# separate road and other nodes
	main_road_graph, disconnected_nodes = clean_road(road_nodes,kd_map) # separate the road_graph and disconnected nodes
	kd_map.set_main_road(main_road_graph)

	print(f"Finished creating roads ({time.time() - st}s) ")
	st = time.time()

	places = create_places_osm(ways, kd_map, main_road_graph, grid_size)
	
	for p in places:
		kd_map.add_place(p)

	print(f"Finished creating places ({time.time() - st}s) ")
	st = time.time()

	bussinesses, residences = create_types_from_osm_tags(kd_map)
	bussinesses_csv, residences_csv = create_types_from_csv(kd_map, 10, bldg_tags)

	bussinesses.update(bussinesses_csv)
	residences.update(residences_csv)

	print(f"Finished creating businesses and residences ({time.time() - st}s) ")
	st = time.time()

	generate_businesses_hours(bussinesses, business_data)
	print(f"Finished setting work hours ({time.time() - st}s) ")

	kd_map.d_businesses = bussinesses
	kd_map.d_residences = residences
	# repair_places(places, businesses, households)

	if evacuation_center is not None:
		generate_evacuation_centers(kd_map,evacuation_center)

	kd_map.mark_nodes()
	
	return kd_map

def create_types_from_osm_tags(kd_map: Map):
	businesses = {}
	residences = {}

	for p in kd_map.d_places.values():
		centroid = kd_map.d_nodes[p.centroid]
		p_type = None
		
		if len(centroid.connections) == 0:
			print("Place without centroid: ", p.id)
			continue

		if "building" in centroid.tags:
			if centroid.tags["building"] != "yes" and centroid.tags["building"] != "+":
				p_type = centroid.tags["building"]
			elif "amenity" in centroid.tags:
				p_type = centroid.tags["amenity"]

		if p_type is not None:
			p.type = p_type
			
			centroid.tags["type"] = "place"
			centroid.tags["place_subtype"] = p_type

			if p_type == "apartments" or p_type == "house" or p_type == "residential":
				r = Residence(p.centroid, p.id, p.road_connection, 1)
				residences[r.id] = r
				centroid.tags["place_type"] = "residence"
			else:
				b = Business(p.centroid, p.id, p.road_connection, p_type)
				centroid.tags["place_type"] = "business"
				businesses[b.id] = b

	return businesses, residences

def create_places_osm(ways, kd_map, main_road_graph, grid_size):
	places = []
	road_grid = create_node_grid(kd_map, main_road_graph, grid_size)
	for w in ways:
		if 'building' not in w.tags:
			continue

		centroid = create_centroid(w, kd_map.d_nodes)
		kd_map.add_node(centroid)

		centroid_grid_coord = get_grid_coordinate(centroid.coordinate.lat, centroid.coordinate.lon, kd_map, grid_size)
		road_connection = create_road_connection(centroid, centroid_grid_coord, road_grid, kd_map)
	
		render_info = Render_info([kd_map.d_nodes[n_id].coordinate for n_id in w.nodes], centroid.coordinate, w.tags)
		p = Place(w.id, True, render_info, centroid.id, road_connection)
		places.append(p)
	return places

def create_centroid(way, n_dict):
	lat, lon = 0, 0

#	size = len(way.nodes)
#	if way.nodes[0] == way.nodes[-1] and size != 1:
#		size -= 1

	size = len(way.nodes)-1
	tags = {"centroid": True,  "type": "place"}


	for i in range(size):
		n_id = way.nodes[i]
		lat += n_dict[n_id].coordinate.lat
		lon += n_dict[n_id].coordinate.lon
		for k, v in n_dict[n_id].tags.items():
			tags[k] = v

	coord = Coordinate(lat/size, lon/size)
	new_id = n_dict[way.nodes[0]].id + "_centroid"
	n = Node(new_id, tags, coord)
	return n


def get_grid_coordinate(lat, lon, kd_map, grid_size):
	cell_height = (kd_map.max_coord.lat - kd_map.min_coord.lat)/grid_size
	cell_width = (kd_map.max_coord.lon - kd_map.min_coord.lon)/grid_size

	x = int((lon - kd_map.min_coord.lon) / cell_width)
	y = int((lat - kd_map.min_coord.lat) / cell_height)

	if x >= grid_size:
		x = grid_size-1
	elif x < 0:
		x = 0
	if y >= grid_size:
		y = grid_size-1
	elif y < 0:
		y = 0
	return (x, y)


def get_closest_road(centroid: Node, centroid_grid_coord, road_grid, kd_map: Map):
	x = centroid_grid_coord[0]
	y = centroid_grid_coord[1]

	visited_roads = {}
	road_start = None
	road_destination = None
	closest_coord = None
	road_dist = math.inf

	for node1 in road_grid[x][y]:
		n_1 = kd_map.d_nodes[node1]
		for node2 in n_1.connections:
			index = (node1, node2)
			if node2 < node1:
				index = (node2, node1)

			if index in visited_roads:
				continue
			visited_roads[index] = True

			n_2 = kd_map.d_nodes[node2]

			if n_1 == n_2:
				continue

			dist, c = get_dist_and_closest_coord(n_1, n_2, centroid)
			if dist < road_dist:
				road_dist = dist
				road_start = n_1
				road_destination = n_2
				closest_coord = c

	return road_start, road_destination, closest_coord

def create_road_connection(centroid: Node, centroid_grid_coord, road_grid, kd_map:Map):

	road_start, road_destination, closest_coord = get_closest_road(centroid, centroid_grid_coord, road_grid, kd_map)

	if road_start is None or road_destination is None:
		return None

	# Checking if the closest coordinate is one of the nodes of the roades
	if closest_coord.get_lat_lon() == road_start.coordinate.get_lat_lon():
		centroid.add_connection(road_start.id)
		road_start.add_connection(centroid.id)
		create_road_sorted(kd_map, centroid, road_start)
		return road_start.id
	if closest_coord.get_lat_lon() == road_destination.coordinate.get_lat_lon():
		centroid.add_connection(road_destination.id)
		road_destination.add_connection(centroid.id)
		create_road_sorted(kd_map, centroid, road_destination)
		return road_destination.id	

	road_connection = connect_centroid_to_road(centroid, road_start, road_destination, closest_coord, kd_map)
	return road_connection.id

def create_types_from_csv (kd_map: Map, grid_size, csv_file_name):
	businesses = {}
	residences = {}

	places = [p for p in kd_map.d_places.values() if p.type is None]
	grid = create_places_grid(kd_map, places, grid_size)

	with open(csv_file_name) as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		for row in csv_reader:
			x, y, number, p_type = int(row["x"]), int(row["y"]), row["number"], row["type"]

			to_create = []
			if number == "All":
				to_create = grid[x][y]
			else:
				n = int(number)
				to_create = [grid[x][y].pop() for _ in range(n) if len(grid[x][y]) > 0]

			for place_id in to_create:
				place = kd_map.d_places[place_id]
				place_node = kd_map.d_nodes[place.centroid]
				if len(place_node.connections) == 0:
					continue

				place.type = p_type
				place_node.tags["type"] = "place"
				place_node.tags["place_subtype"] = p_type
				if p_type == "residential" or p_type == "apartments":
					r = Residence(place.centroid, place.id, place.road_connection, 1)
					residences[r.id] = r
					place_node.tags["place_type"] = "residence"
				else:
					b = Business(place.centroid, place.id, place.road_connection, p_type)
					businesses[b.id] = b
					place_node.tags["place_type"] = "business"

	return businesses, residences

def repair_places():
	pass

def create_road_sorted(kd_map, node1, node2):
	start_id = min(node1.id, node2.id)
	goal_id = max(node1.id, node2.id)

	dist = node1.distance_to_coordinate(*node2.coordinate.get_lat_lon())
	road = Road(start_id, goal_id, dist)

	kd_map.add_road(road)

def build_node_connections(kd_map):
	for key in kd_map.d_ways:
		way = kd_map.d_ways[key]
		# working_node = None
		for current_node_id, next_node_id in zip(way.nodes, way.nodes[1:]):
			current_node = kd_map.d_nodes[current_node_id]

			connectingNode = kd_map.d_nodes[next_node_id]
			current_node.add_connection(next_node_id) #add the connection from current_node to the connecting_node
			connectingNode.add_connection(current_node.id) #add the connection from the connecting_node to the current_node

			create_road_sorted(kd_map, current_node, connectingNode)

			for k, v in way.tags.items():
				connectingNode.tags[k] = v
				current_node.tags[k] = v

def separate_nodes(kd_map):
	road_nodes = []
	other_nodes = []
	for key in kd_map.d_nodes:
		node = kd_map.d_nodes[key]
		if (node.is_road):
			road_nodes.append(node)
			node.tags["type"] = "road"
		else:
			other_nodes.append(node)
	return road_nodes, other_nodes

def clean_road(road_nodes, kd_map):
	working_node = None
	results = []
	while len(road_nodes)>0: #loop until road_nodes empty
		queue = [road_nodes[0]] #put 1 starting nodes to the queue
		visited = []
		while len(queue) > 0: #loop until queue is empty
			working_node = queue.pop(0) #pop the queue
			if (working_node in road_nodes): road_nodes.remove(working_node) #remove the working_node from road_nodes
			visited.append(working_node) #add the node to the visited
			for node_id in working_node.connections:
				node = kd_map.d_nodes[node_id] #get the node
				if (node not in visited and node not in queue):
					queue.append(node) #if the node never visited, put it on queue
		results.append(visited) #append all of the visited road as 1 graph

	main_road = []
	disconnected_nodes = []
	largest = 0
	for result in results:
		if (len(result)>largest):
			disconnected_nodes.extend(main_road)
			largest = len(result)
			main_road = result
		else:
			disconnected_nodes.extend(result)
	return main_road, disconnected_nodes


def create_node_grid(kd_map, nodes, grid_size: int):
	grid = []
	for i in range(grid_size):
		grid.append([])
		for _ in range(grid_size):
			grid[i].append([])

	for n in nodes:
		x, y = get_grid_coordinate(n.coordinate.lat, n.coordinate.lon, kd_map, grid_size)
		if x > grid_size or y > grid_size:
			continue
		grid[x][y].append(n.id)

	return grid


def create_places_grid(kd_map, places, grid_size: int):
	grid = []
	for i in range(grid_size):
		grid.append([])
		for _ in range(grid_size):
			grid[i].append([])

	for p in places:
		n = kd_map.d_nodes[p.centroid]
		x, y = get_grid_coordinate(n.coordinate.lat, n.coordinate.lon, kd_map, grid_size)
		if x > grid_size or y > grid_size:
			continue
		grid[x][y].append(p.id)

	return grid


def connect_centroid_to_road(centroid, road_start, road_destination, closest_coord, kd_map:Map):
	new_id = centroid.id + "_entry"
	new_node = Node(new_id, {"entry_point": True}, closest_coord)

	if road_destination.id in road_start.connections:
		road_start.connections.remove(road_destination.id)

	if road_start.id in road_destination.connections:
		road_destination.connections.remove(road_start.id)

	if road_start.id < road_destination.id:
		kd_map.remove_road(road_start.id, road_destination.id)
	else:
		kd_map.remove_road(road_destination.id, road_start.id)

	# I am assuming all connections are 2 ways
	centroid.add_connection(new_id)
	road_start.add_connection(new_id)
	road_destination.add_connection(new_id)
	new_node.add_connection(road_start.id)
	new_node.add_connection(road_destination.id)
	new_node.add_connection(centroid.id)

	create_road_sorted(kd_map, new_node, road_start)
	create_road_sorted(kd_map, new_node, road_destination)
	create_road_sorted(kd_map, new_node, centroid)

	kd_map.add_node(new_node)
	kd_map.main_road.append(new_node)

	return new_node

# Gets the distance from a road to a node and the closest point on the road
def get_dist_and_closest_coord(road_start, road_destination, target_node):
	start_dist = road_start.coordinate.calculate_distance(*target_node.coordinate.get_lat_lon())
	destination_dist = road_destination.coordinate.calculate_distance(*target_node.coordinate.get_lat_lon())

	a = max(start_dist, destination_dist)
	b = min(start_dist, destination_dist)
	c = road_start.coordinate.calculate_distance(*road_destination.coordinate.get_lat_lon())
	s = (a+b+c)/2

	area =s*(s-a)*(s-b)*(s-c)
	if (area < 0):
		# Maybe in this case we should set area = 0, want to test this once we have vizualization
		print("Warning, Heron's formula is not working due to very small angle")
		return math.inf, None
	area = math.sqrt(area)

	height = 2*area/c

	sinq = height/a
	q = math.asin(sinq)
	e = a * math.cos(q)

	closest_coord = None
	if (e > c or q > math.pi):
		height = min(a, b)
		if (a < b):
			closest_coord = road_start.coordinate
		else:
			closest_coord = road_destination.coordinate

	if start_dist < destination_dist:
		dist_vector = road_start.coordinate.get_vector_distance(road_destination.coordinate)
		dist_vector = dist_vector.new_coordinate_with_scale(e/c)
		closest_coord = Coordinate(road_destination.coordinate.lat + dist_vector.lat, road_destination.coordinate.lon + dist_vector.lon)
	else:
		dist_vector = road_destination.coordinate.get_vector_distance(road_start.coordinate)
		dist_vector = dist_vector.new_coordinate_with_scale(e/c)
		closest_coord = Coordinate(road_start.coordinate.lat + dist_vector.lat, road_start.coordinate.lon + dist_vector.lon)

	return height, closest_coord


def generate_businesses_hours(businesses_dict, csv_file_name):
	csv_info = {}
	with open(csv_file_name) as csv_file:
		csv_reader = csv.DictReader(csv_file, delimiter=',')
		for row in csv_reader:
			csv_info[row["building_type"]] = row

	days_of_the_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

	for business in businesses_dict.values():
		if business.type not in csv_info:
			# Default is opening everyday every hour
			for day in days_of_the_week:
				business.add_working_hour(day, "00:00", "00:00")
			continue
		b_info = csv_info[business.type]
		min_workhour = int(b_info["min_workhour"])
		max_workhour = int(b_info["max_workhour"])
		min_start_hour = int(b_info["min_start_hour"])
		max_start_hour = int(b_info["max_start_hour"])
		min_activity_per_week = int(b_info["min_activity_per_week"])
		max_activity_per_week = int(b_info["max_activity_per_week"])
		open_24h_chance = float(b_info["open_24_hours_chance"])

		start_hour = np.random.randint(min_workhour, max_workhour+1)
		workHours = np.random.randint(min_start_hour, max_start_hour+1)
		finish_hour = (start_hour + workHours) % 24

		if np.random.random() < open_24h_chance:
			start_hour = 0
			finish_hour = 0

		workdays =  days_of_the_week
		if b_info["day"] == "weekday":
			workdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]
		elif b_info["day"] == "weekend":
			workdays = ["Sat", "Sun"]

		activity = np.random.randint(min_activity_per_week, max_activity_per_week+1)

		activity = np.min([activity, len(workdays)])
		workdays = np.random.choice(workdays, activity, replace=False)

		for day in workdays:
			business.add_working_hour(day, f"{start_hour}:00", f"{finish_hour}:00")


def generate_evacuation_centers(kd_map, file_path):
	evacuation_dict = {}
	with open(file_path) as file:
		evacuation_dict = json.load(file)["evacuation_centers"]
	evacuation_center_dict = {}
	for location in evacuation_dict:
		try:
			rules = location["rules"]
			attr = location["attributes"]
			selection = location["selection"]
			places = []
			if selection == "by_id":
				p = kd_map.d_places[rules["place_id"]]
				places.append(p)
			else:
				qtd = rules["qtd"]
				allowed_places = [p for p in kd_map.d_places.values()]
				if "place_types" in rules:
					allowed_places = [p for p in kd_map.d_places.values() if p.type in rules["place_types"]]

				if selection == "by_type" and len(allowed_places) >= qtd:
					places = np.random.choice(allowed_places, qtd, replace=False)
				elif selection == "by_grid":
					grid = create_places_grid(kd_map, allowed_places, rules["grid_size"])
					x, y = rules["cell"]
					places = np.random.choice(grid[x][y], min(qtd, len(grid[x][y])), replace=False)

			if len(places) > 0:
				for place in places:
					place.evacuation_center = True
					place.evacuation_attr = attr
					evacuation_center_dict[place.centroid] = place		
		except KeyError as e:
			print("Warning: Key error when processing evacuation center file ", file_path)
			print("Error on entry: ", location)
			print("Tried to access key ", e, " but it does not exist")
	kd_map.d_evacuation_centers = evacuation_center_dict
