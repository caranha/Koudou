from .action import Action

class ActionChangeBehavior(Action):    

    def __init__(self,agent,behavior_name):
        super(ActionChangeBehavior,self).__init__()
        self.behavior_name = behavior_name
        self.agent = agent

    def step(self, kd_sim, kd_map, step_length, rng):
        """
        [Method]
        Update method

        parameter:
        - step_length : (int) how many seconds elapsed

        return:
        - (int) the remainder of the step_length that was not consumed by this action
        """
        self.agent.change_behavior(self.behavior_name)
        self.finished = True
        return step_length #return the left over time 

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
        return f"Change agent {self.agent.agent_id} behavior into {self.behavior_name}\n"

    def __str__(self):
        tempstring = "[ActionChangeBehavior]\n"
        tempstring += f"{self.agent.agent_id} = {self.behavior_name}"
        return tempstring