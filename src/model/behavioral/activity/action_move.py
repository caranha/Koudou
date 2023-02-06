from .action import Action
from .movement_vector import MovementVector
class ActionMove(Action):
    """
    [Class] ActionMove
    A class that represent agents move command.
    
    Properties:
        - name      : (string-inherited)
    """
    def __init__(self,agent,kd_map,destination_string,rng,ts):
        """
        [Constructor]
        Initialize a wait action

        parameter:
        - name     : (string) the name of action (e.g : Eating, Sleeping)
        - duration : (int) the duration of the action in seconds
        """
        super(ActionMove,self).__init__()
        self.destination = ""
        self.destination_string = destination_string
        dest_str = destination_string.replace(")", "")
        self.ts = ts
        self.sequence = []
        self.agent = agent
        self.finished = False
        self.origin = agent.get_attribute("current_node_id")
        self.target = None
        self.typing = ""
        self.target_type = None
        # todo: this evac logic should be part of a separate plugin
        if destination_string == "!evac":
            # print(f"agent {self.agent.agent_id}'s' go to evac")
            node = kd_map.d_nodes[self.origin]
            self.target = kd_map.get_closest_evacuation_center(
                node.coordinate,
                agent.get_attribute("explored_evac"),
                agent.get_attribute("home_node_id")
            )
            agent.set_attribute("target_evac",self.target.centroid)
            self.destination = self.target.centroid
            self.target_type = "Evacuation Point"
        elif destination_string == "!random":
            self.destination = kd_map.get_random_connected_nodes(self.origin,agent.get_attribute("last_node_id"),rng)
        else:
            self.typing = "destination_type"
            if ("(" in dest_str):
                split_destination = dest_str.split("(")
                dest_str = split_destination[0]
                if (split_destination[1].lower() == "destination_id") or (split_destination[1].lower() == "id"):
                    self.typing = "destination_id"
                elif (split_destination[1].lower() == "destination_type") or (split_destination[1].lower() == "type"):
                    self.typing = "destination_type"
                else:
                    raise ValueError(f"Unknown destination type : {split_destination[1].lower()}")
    
            if ("$" in dest_str):
                dest_str = agent.get_attribute(dest_str.replace("$",""))

            if self.typing == "destination_type":
                # self.target_type = dest_str
                self.destination = kd_map.get_random_business(dest_str, 1, rng,time_stamp = ts, only_open = True)[0].node_id
            elif self.typing == "destination_id":
                self.destination = dest_str
            target_place = kd_map.d_places_by_centroid[self.destination]
            self.target_type = target_place.type
        self.reseted = False

    def force_reset(self):
        self.sequence = self.sequence[:1]
        self.reseted = True

    def step(self,kd_sim,kd_map,ts,step_length,rng):
        # if have action do it
        leftover = step_length
        while len(self.sequence) > 0:
            mov_vec = self.sequence[0]
            leftover = mov_vec.step(self.agent,leftover,kd_map) 
            if not mov_vec.is_finished:
                break
            else:
                self.sequence.pop(0)
        if len(self.sequence) == 0:
            self.finished = True
            if (not self.reseted):
                if self.target_type is not None:
                    self.agent.set_attribute("location",self.target_type)
            self.reseted = False
            # if (self.destination_string == "!evac"):
            #     print(f"agent {self.agent.agent_id}'s' Evac Finished")
        return leftover

    @property
    def is_finished(self):
        """
        [Property]
        Check if this action is finished or not

        return:
        - (bool) true if finished, false otherwise
        """
        return self.finished

    @property
    def short_string(self):
        return f"Move to {self.destination_string}"

    def __str__(self):
        tempString = f"[ActionMove]\n"
        tempString += f"   Origin = {self.origin}\n"
        tempString += f"   Destination = {self.destination}\n"
        tempString += f"   Destination String = {self.destination_string}"
        return tempString

    def generate_vector(self,kd_map,path):
        working = kd_map.get_node(path[0])
        for x in path[1:]:
            temp = kd_map.get_node(x)
            self.sequence.append(MovementVector(working,temp))
            working = temp


