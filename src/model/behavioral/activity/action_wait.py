from .action import Action

class ActionWait(Action):
    """
    [Class] ActionWait
    A class that represent agents actions on a building. 
    When this action is processed, the agents will wait for several duration in their last position. 
    
    Properties:
        - name      : (string-inherited)
        - duration  : (int) duration of wait in seconds
        - current   : (int) time spent waiting
    """   
    def __init__(self,agent,command_string,rng):
        """
        [Constructor]
        Initialize a wait action

        parameter:
        - agent : (Agent) the agent used for getting attributes 
        - command_string : (string) the command string - check wiki for explanation
        - rng : (numpy_random_generator) the RNGesus
        """
        super(ActionWait,self).__init__()
        min_duration = 0
        max_duration = 0

        # try to get max and min value in string format
        if "-" in command_string:
            # we detect "-" which for example "30:min-50:min"
            # This means the action will have duration between 30 minutes to 50 minutes
            temp = command_string.split("-")
            min_duration = temp[0]
            max_duration = temp[1]
        else:
            # input example = "30:min"
            # this means self.min and self.max are the same
            min_duration = command_string
            max_duration = command_string

        # process min 
        min_duration = _process_time(min_duration,agent)
        max_duration = _process_time(max_duration,agent)+1 #plus 1 second for rng later

        self.duration = rng.integers(min_duration,max_duration,1)[0]
        self.current = 0


    def step(self, kd_sim, kd_map, step_length, rng):
        """
        [Method]
        Update method

        parameter:
        - step_length : (int) how many seconds elapsed

        return:
        - (int) the remainder of the step_length that was not consumed by this action
        """
        self.current += step_length #add step length to the executable
        self.remainder = max(0,self.current - self.duration) #check is time passed is bigger than the wait duration 
        self.current = min(self.current, self.duration) #if current is bigger than duration set the value of current to duration
        return self.remainder #return the left over time 

    @property
    def short_string(self):
        return f"Wait for {self.min}-{self.max}minutes"

    def __str__(self):
        tempstring = "[Action-Wait]\n"
        tempstring += f"   Duration = {self.min}-{self.max}minutes"


    @property
    def is_finished(self):
        """
        [Property]
        Check if this action is finished or not

        return:
        - (bool) true if finished, false otherwise
        """
        return self.current >= self.duration

def _process_time(variable_string, agent):
    # Example = "$workhour:hour"
    modifier = 1 
    value = variable_string

    if "(" in variable_string:
        # if have ":" means that the duration might not in seconds
        temp = variable_string.replace(")","")
        temp = temp.split("(")
        modifier = _fetch_time_modifier(temp[1])
        value = temp[0]

    if "$" in value:
        # if value equals "$workhour"
        # this means load from agent's attribute called "workhour"
        attribute_name = value[1:] 
        value = int(agent.get_attribute(attribute_name))
    else:
        value = int(value)

    return value *modifier


def _fetch_time_modifier(modifier):
    seconds = ["s","sec","secs","second","seconds"]
    minutes = ["m","min","mins","minute","minutes"]
    hours = ["h","hou","hour","hours"]
    days = ["d","day","days"]
    weeks = ["w","week","weeks"]
    if modifier is None or modifier == "" or modifier.lower() in seconds:
        return 1
    elif modifier.lower() in minutes:
        return 60
    elif (modifier.lower() in hours):
        return 3600
    elif (modifier.lower() in days):
        return 24*3600
    elif (modifier.lower() in weeks):
        return 7*24*3600
    else:
        return 0

def _fetch_operator(operator_string):
    if(operator_string == "*"):
        return operator.mul
    elif(operator_string == "/"):
        return operator.div
    elif(operator_string == "%"):
        return operator.modulo
    elif(operator_string == "+"):
        return operator.add
    elif(operator_string == "-"):
        return operator.add