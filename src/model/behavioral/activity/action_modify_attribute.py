from .action import Action

class ActionModifyAttribute(Action):    
    def __init__(self,agent,command):
        super(ActionModifyAttribute,self).__init__()
        temp = command.split("-")        
        self.attribute_name = temp[0]
        if (temp[1].lower() == "max"):
            self.value = "max"
        elif(temp[1].lower() == "min"):
            self.value = "min"
        else:
            self.value = temp[1]
        self.finished = False
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
        self.agent.update_attribute(self.attribute_name,self.value)
        self.finished = True
        return step_length #return the left over time 

    @property
    def short_string(self):
        return f"{self.attribute_name} = {self.value}\n"

    def __str__(self):
        tempstring = "[Action_Modify_attribute]\n"
        tempstring += f"{self.attribute_name} = {self.value}"
        return tempstring


    @property
    def is_finished(self):
        """
        [Property]
        Check if this action is finished or not

        return:
        - (bool) true if finished, false otherwise
        """
        return self.finished
