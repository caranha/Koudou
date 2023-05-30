from src.model.behavioral.module import Module
class EvacuationModule(Module):

    def __init__(self, distance, share_information_chance, logger):
        self.distance = distance
        self.share_information_chance = share_information_chance
        self.triggered = False
        self.total_evac = 0
        self.logger_file = "evac_log.txt"
        self.init_loger(logger)


    def init_loger(self, logger):
        # evacuation
        header = ["time_stamp", "ag_id", "evac_point_id", "evac_occupation", "evac_capacity", "total_evacuated"]
        logger.add_csv_file("evacuation.csv", header)


        # evacuation capacity
        header = ["time_stamp", "ag_id", "refused_evac_id", "new_evac"]
        logger.add_csv_file("evac_refused_entry.csv", header)

        logger.add_file(self.logger_file)
        # evacuation knownledge
        # header = ["time_stamp", "from_ag_id", "to_ag_id"]
        # logger.add_csv_file("evac_knowledge.csv", header)


    # def setup_default_knowledge(kd_map,kd_sim,value,rng):
    #     agent_that_know_evacuation_center = value * len(kd_sim.agents)
    #     temp = kd_sim.agents.copy()
    #     rng.shuffle(temp)
    #     for i in range(0,agent_that_know_evacuation_center):
    #         temp[i].set_attribute("target_evac",kd_map.get_closest_evacuation_center)

    # triggered once when the evacuation begin
    def reset_agents_actions(self,kd_sim):
        self.triggered = True
        for agent in kd_sim.agents:
            agent.force_reset()

    #Share ERI (Evacuation Route Information)
    def share_info(self,kd_sim,kd_map,ts,step_length,rng,logger):
        sources = {}
        recipients = {}
        for agent in kd_sim.agents: 
            node_id = agent.get_attribute("current_node_id")
            if agent.get_attribute("know_evac") == True:
                if node_id not in sources.keys():
                    sources[node_id] = []
                sources[node_id].append(agent)
            else:
                if node_id not in recipients.keys():
                    recipients[node_id] = []
                recipients[node_id].append(agent)

        for node_id in sources:
            current_sources = sources[node_id]
            current_recipients = []
            if node_id in recipients.keys():
                current_recipients.extend(recipients[node_id])
            node = kd_map.d_nodes[node_id]
            for conn in node.connections:
                if conn in recipients.keys():
                    current_recipients.extend(recipients[conn])
            for source in current_sources:
                for recipient in current_recipients:
                    if rng.uniform(0.0,1.0,1)[0] > self.share_information_chance:
                        recipient.set_attribute("target_evac",source.get_attribute("target_evac"))
                        recipient.set_attribute("explored_evac",source.get_attribute("explored_evac"))
                        recipient.set_attribute("know_evac",True)

    # mark agents that arrived at evacuation point as evacuated
    def evacuate(self,kd_sim,kd_map,ts,step_length,rng,logger):
        for evac_center_id in kd_map.d_evacuation_centers:
            evac_center =  kd_map.d_evacuation_centers[evac_center_id]
            capacity = int(evac_center.evacuation_attr["capacity"])

            if evac_center.centroid not in kd_sim.d_agents_by_location.keys():
                continue #check if there are some agents in the evacuation point
            
            unevacuated = []
            occupation = 0
            for agent in kd_sim.d_agents_by_location[evac_center.centroid]:
                if agent.get_attribute("evacuated"):  
                    occupation += 1
                else:
                    unevacuated.append(agent)

            for agent in unevacuated:
                # add this evacuation center to agent's visit history
                temp = agent.get_attribute("explored_evac").lower()
                if (temp == "none"):
                    temp = ""
                else:
                    temp += ","                        
                temp += f"{evac_center_id}"
                agent.set_attribute("explored_evac", temp) 
                agent.set_attribute("know_evac",True)

                if (occupation < capacity):        
                    agent.set_attribute("evacuated",True)
                    agent.set_attribute("location","Evacuation_Point")
                    occupation += 1
                    self.total_evac += 1

                    self.log_ag_evacuating(
                        ts, 
                        agent.agent_id, 
                        evac_center_id, 
                        occupation, 
                        capacity, 
                        logger
                    )


                else:
                    new_target = kd_map.get_closest_evacuation_center(
                        agent.coordinate,
                        agent.get_attribute("explored_evac"),
                        agent.get_attribute("home_node_id")    
                    )

                    agent.set_attribute("target_evac", new_target)
                    self.log_ag_refused_evac(
                        ts,
                        agent.agent_id,
                        evac_center_id,
                        new_target,
                        logger
                    )

    def log_ag_evacuating(self, ts, ag_id, evac_id, occupation, capacity, logger):
        log_txt = f"{ts.get_hour_min_str()}: ag {ag_id} evacuated at {evac_id}"
        logger.write_log(log_txt, filename=self.logger_file)

        data = {
            "time_stamp": ts.step_count,
            "ag_id": ag_id,
            "evac_point_id": evac_id,
            "evac_occupation": occupation,
            "evac_capacity": capacity,
            "total_evacuated": self.total_evac
        }

        logger.write_csv_data("evacuation.csv", data)

    def log_ag_refused_evac(self, ts, ag_id, refused_evac_id, new_evac, logger):
        log_txt = f"{ts.get_hour_min_str()}: ag {ag_id} refused entry at {refused_evac_id}, now going to {new_evac}"
        logger.write_log(log_txt, filename=self.logger_file)

        data = {
            "time_stamp": ts.step_count, 
            "ag_id": ag_id, 
            "refused_evac_id": refused_evac_id,
            "new_evac": new_evac
        }

        logger.write_csv_data("evac_refused_entry.csv", data)


    # triggered once when the evacuation begin
    def step(self,kd_sim,kd_map,ts,step_length,rng,logger):
        if (kd_sim.get_attribute("evacuation")):
            if not self.triggered:
                print("Evacuation started!")
                #reset agent activities
                self.reset_agents_actions(kd_sim)
            self.share_info(kd_sim,kd_map,ts,step_length,rng,logger)
            self.evacuate(kd_sim,kd_map,ts,step_length,rng,logger)
        else:
            if self.triggered:
                print("Evacuation Finished!")
                self.triggered = False
