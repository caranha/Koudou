from .action import Action

#modify_energy:restore-500
class ActionModifyEnergy(Action):

    def __init__(self, agent, command):
        super(ActionModifyEnergy, self).__init__()
        temp = command.split("-")
        self.energy_action = temp[0]
        self.energy_value=temp[1]
        self.finished = False
        self.agent = agent

    def step(self,kd_sim,kd_map,ts,step_length,rng):
        try:
            if(self.energy_action=="restore"):
                self.agent.update_energy(int(self.energy_value))

            elif(self.energy_action=="consume"):
                self.agent.update_energy(-int(self.energy_value))
            else:
                raise RuntimeError("undefined energy action")
            self.finished = True
            return step_length
        except:
            raise RuntimeError("energy value should be integer")

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
        return f"Change agent {self.agent.agent_id} energy with value: {self.energy_value} ({self.energy_action})\n"

    def __str__(self):
        tempstring = "[ActionModifyEnergy]\n"
        tempstring += f"Change agent {self.agent.agent_id} energy with value: {self.energy_value} ({self.energy_action})"
        return tempstring
