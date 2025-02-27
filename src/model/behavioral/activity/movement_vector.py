import haversine as hs
from src.model.map.coordinate import Coordinate
import math
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

        leftOver = 0.0
        speed=0
        # print(step_length)
        for i in range(int(step_length)):
            speed, energy_flat_cost = self.GetSpeedAndCost(agent)
            # print(f"agent{agent.agent_id} speed: {speed}  energy: {agent.energy} ")

            if road is not None:
                speed *= road.modifier
            temp_distance=speed*1
            temp_untraveled_distance = self.distance - self.passed_through_distance
            temp_current_traveled_distance = min(temp_distance, temp_untraveled_distance)
            temp_passed_through_distance = self.passed_through_distance + temp_current_traveled_distance
            temp_progress = temp_passed_through_distance / self.distance


            step_lat = self.starting_node.coordinate.lat + (temp_progress * self.total_translation[0])
            step_lon = self.starting_node.coordinate.lon + (temp_progress * self.total_translation[1])
            agent.coordinate.calculate_elevation()
            current_height = agent.coordinate.elevation
            step_height = Coordinate(lat=step_lat, lon=step_lon).elevation
            base = temp_current_traveled_distance
            opposite = float(step_height - current_height)
            hypotenuse=math.sqrt(base ** 2 + opposite ** 2)
            if(hypotenuse==0):
                energy_cost=0
                slope_speed=0
            else:
                cos_theta = base / hypotenuse
                sin_theta = opposite / hypotenuse
                energy_cost = energy_flat_cost * (1 + sin_theta) / cos_theta
                minSlopeSpeed = float(agent.get_attribute("speedMin")) * (energy_flat_cost / energy_cost)

                if (energy_cost > agent.energy):

                    temp_speed = speed * (energy_flat_cost / energy_cost) * (agent.energy / energy_cost)
                    slope_speed = minSlopeSpeed if temp_speed < minSlopeSpeed else temp_speed
                else:
                    slope_speed = speed * energy_flat_cost / energy_cost


            agent.update_energy(-energy_cost)
            agent.used_energy += energy_cost
            if (agent.get_attribute("is_slope_on") == True):
                distance = slope_speed * 1
            else:
                distance = speed * 1
            untraveled_distance = self.distance - self.passed_through_distance
            current_traveled_distance = min(distance, untraveled_distance)

            if (agent.current_behavior.name == "evacuate"):
                agent.update_distance(current_traveled_distance)
            self.passed_through_distance += current_traveled_distance
            # print(agent.current_behavior.name)
            # print(f"agent{agent.agent_id} speed: {slope_speed},{speed}  energy: {agent.energy} energy cost:{energy_cost} h1 {current_height} h2 {step_height}")

            # if (agent.current_behavior.name == "evacuate"):
            #     print(f"agent{agent.agent_id} speed: {slope_speed},{speed}  energy: {agent.energy} energy cost:{energy_cost} h1 {current_height} h2 {step_height}")

            if (distance >= untraveled_distance):
                self.progress = 1.0
                self.finished = True
                self.current_position = self.destination_node.coordinate
                leftOver = (distance - current_traveled_distance)
                agent.set_attribute("last_node_id", agent.get_attribute("current_node_id"))
                agent.set_attribute("current_node_id", self.destination_node.id)
                agent.set_attribute("location", self.destination_node.type)
            else:
                self.progress = self.passed_through_distance / self.distance
                # print(f"agent{agent.agent_id} trans: {self.total_translation[0]}, {self.total_translation[1]} ")
                lat = self.starting_node.coordinate.lat + (self.progress * self.total_translation[0])
                lon = self.starting_node.coordinate.lon + (self.progress * self.total_translation[1])
                self.current_position = Coordinate(lat=lat, lon=lon)
            agent.coordinate = self.current_position




        if speed==0:
            return 0.0
        else:
            return leftOver/speed




    def GetSpeedAndCost(self,agent):
        running_speed = float(agent.get_attribute("running_speed"))
        if (agent.get_attribute("is_slope_on") == True):
            if (agent.current_behavior.name == "evacuate" and agent.get_attribute("can_run") == True):
                if (agent.energy >= 0.6 * agent.max_energy):
                    speed = running_speed
                elif (0.3 * agent.max_energy <= agent.energy < 0.6 * agent.max_energy):
                    speed = 0.8 * running_speed
                elif (0 < agent.energy < 0.3 * agent.max_energy):
                    speed = 0.6 * running_speed
                elif (agent.energy <= 0):
                    speed = float(agent.get_attribute("speedMin"))
                energy_flat_cost = int(agent.get_attribute(("walking_consume"))) * 1.75
                # print(f"should run speed{speed} ")
            else:
                if (agent.energy >= 0.6 * agent.max_energy):
                    speed = float(agent.get_attribute("speedA"))
                elif (0.3 * agent.max_energy <= agent.energy < 0.6 * agent.max_energy):
                    speed = float(agent.get_attribute("speedB"))
                elif (0 < agent.energy < 0.3 * agent.max_energy):
                    speed = float(agent.get_attribute("speedC"))
                elif (agent.energy <= 0):
                    speed = float(agent.get_attribute("speedMin"))
                energy_flat_cost = int(agent.get_attribute(("walking_consume")))
        else:
            speed = float(agent.get_attribute("walking_speed"))
            energy_flat_cost = int(agent.get_attribute(("walking_consume")))
        return speed,energy_flat_cost

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