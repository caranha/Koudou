import haversine as hs
from src.model.map.coordinate import Coordinate
class MovementVector:
    """
    [Class] MovementVector
    A class to represent the a star node
    
    Properties:
        - starting_node          : [Node] the starting node of this movementVector
        - destination_node       : [Node] the destination node of this movementVector
        - starting              : [Coordinate] the starting coordinate of this movementVector
        - destination           : [Coordinate] the destination coordinate of this movementVector
        - distance              : [Float] distance in meters
        - passed_through_distance : [Float] distance we traveled in this movementVector
        - current_position       : [Coordinate] current position
        - finished              : [Bool] is the whole vector traveled?
        - progress              : [Float] passed_through_distance divided by totalTranslation
    """
    def __init__(self,starting_node, destination_node):
        """
        [Constructor]    
        Generate Unused MovementVector.
        
        Parameter:
            - starting_node    : [Node] the starting node of this movementVector
            - destination_node : [Node] the destination node of this movementVector
        """
        self.starting_node = starting_node
        self.destination_node = destination_node
        self.distance = hs.haversine(self.starting_node.coordinate.get_lat_lon(), self.destination_node.coordinate.get_lat_lon(), unit=hs.Unit.METERS)
        self.passed_through_distance = 0
        self.current_position = self.starting_node
        self.finished = False
        self.progress = 0.0
        self.total_translation = (self.destination_node.coordinate.lat- self.starting_node.coordinate.lat, self.destination_node.coordinate.lon- self.starting_node.coordinate.lon)
        
    def calculateTranslation(self, current_position):
        """
        [Method] calculateTranslation    
        Calculate the translation required from a coordinate to the calculated position in this movement vector. 
        
        Parameter:
            - current_position : [Coordinate]current position
            
        return :
            - (lat,lon) the translation vector in latitude and longitude
            
        """
        return (self.current_position[0] - current_position.lat, self.current_position[1] - current_position.lon)
        
    def step(self,agent,step_length,kd_map):
        """
        [Method] step    
        Travel a certain number of distances in this vector, if the distance is higher than our remaining distance in this vector, the leftover will be returned.
        
        Parameter:
            - agent       : [Agent] the agent
            - step_length : [Float] step_length
            
        return :
            - [float] the leftover of the distance            
        """
        # calculate is there any left over translation
        first = min(self.starting_node.id, self.destination_node.id)
        second = max(self.starting_node.id, self.destination_node.id)
        t = (first, second)
        road = kd_map.d_roads[t]
        speed = float(agent.get_attribute("walking_speed")) 
        if road is not None:
            speed *= road.modifier
        route_nodes = kd_map.route_nodes
        modified = False
        for s in route_nodes:
            if not modified and self.starting_node.id in s and self.destination_node.id in s:
                modified = True
                # modify the agent speed when on a route
                speed *= 5
        distance =  speed*step_length 
        untraveled_distance = self.distance - self.passed_through_distance
        current_traveled_distance = min(distance,untraveled_distance)
        self.passed_through_distance += current_traveled_distance
        leftOver = 0.0
        if (distance >= untraveled_distance):
            self.progress = 1.0
            self.finished = True
            self.current_position =  self.destination_node.coordinate
            leftOver = (distance - current_traveled_distance)
            agent.set_attribute("last_node_id",agent.get_attribute("current_node_id"))
            agent.set_attribute("current_node_id",self.destination_node.id)
            agent.set_attribute("location",self.destination_node.type)
        else:
            self.progress = self.passed_through_distance/self.distance
            lat = self.starting_node.coordinate.lat +(self.progress * self.total_translation[0])
            lon = self.starting_node.coordinate.lon +(self.progress * self.total_translation[1])
            self.current_position = Coordinate(lat=lat, lon=lon)
        agent.coordinate = self.current_position
        return leftOver/speed
    
    def extract(self):
        """
        [Method] extract  
        return the osmId of the origin and destination node
            
        return :
            - [(string,string)] : (starting_node.osmId, destination_node.osmId)            
        """
        return (self.starting_node.osmId, self.destination_node.osmId)
    
    @property 
    def is_finished(self):
        return self.finished