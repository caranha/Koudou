import random
import matplotlib.pyplot as plt

class EvacuationCenter:
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        self.current_occupancy = 0

    @property
    def crowding_factor(self):
        return self.current_occupancy / self.max_capacity

class Agent:
    def __init__(self):
        self.state = "indifferent"
        self._concern_level = 1
        # initial SEIR state is susceptible
        self.SEIR_state = "S"
        self.infected_substate = None
        self.evacuation_center = None
        # choices: "none", "surgical", "N95"
        self.mask = "none"

    @property
    def family_infected(self):
        # change this property to depend on the SEIR state of family members
        return random.choices([True, False], weights=[0.05, 0.95])[0]

    @property
    def is_infected(self):
        # dependent on the SEIR state of the agent to determine if infected
        return self.SEIR_state == "I"

    def update_mask(self):
        # to determine the probability of changing mask type based on the emotion state
        if self.state == "indifferent":
            self.mask = random.choices(["none", "surgical", "N95"], weights=[0.2, 0.8, 0.02])[0]
        elif self.state == "worried":
            self.mask = random.choices(["surgical", "N95"], weights=[0.5, 0.5])[0]
        elif self.state == "afraid":
            self.mask = random.choices(["surgical", "N95"], weights=[0.7, 0.3])[0]
        elif self.state == "numb":
            self.mask = random.choices(["none", "surgical"], weights=[0.5, 0.5])[0]

    def update_SEIR(self, beta, alpha, sym_rate, sev_rate, gamma):
        # consider the effect of mask on infection rate
        mask_effect = {
            "none": 1.0,
            "surgical": 0.34,  # 66% reduction
            "N95": 0.18  # 82% reduction
        }
        adjusted_beta = beta * mask_effect[self.mask]

        if self.SEIR_state == "S":
            if random.random() < adjusted_beta:
                self.SEIR_state = "E"

        elif self.SEIR_state == "E":
            if random.random() < alpha:
                self.SEIR_state = "I"
                self.infected_substate = "asymptomatic"

        elif self.SEIR_state == "I":
            if self.infected_substate == "asymptomatic":
                if random.random() < sym_rate:
                    self.infected_substate = "symptomatic"
            elif self.infected_substate == "symptomatic":
                if random.random() < sev_rate:
                    self.infected_substate = "severe"

            if random.random() < gamma:
                self.SEIR_state = "R"
                self.infected_substate = None

    def update_emotion(self, transfer_rates):
        if self.state not in transfer_rates:
            return

        next_state, rate = transfer_rates[self.state]
        if random.random() < rate:
            self.state = next_state

    def get_concern_level(self, i, infection_increase_rate):
        concern = self._concern_level
        if self.SEIR_state == "I":
            if self.infected_substate == "symptomatic":
                concern += 0.2
            elif self.infected_substate == "severe":
                concern += 0.3

        if self.family_infected:
            concern += 0.1
        # to consider the effect of community infection rate on concern level in a more sensitive way
        concern += infection_increase_rate * 3

        if self.evacuation_center:
            concern += self.evacuation_center.crowding_factor / 3

        return concern

    def decay_concern(self):
        self._concern_level = max(0.5, self._concern_level - 0.005)


if __name__ == '__main__':
    # parameter setting ========================================
    transfer_rates_dict = {
        'i-w': 0.1,
        'w-a': 0.01,
        'a-n': 0.005,
        'w-i': 0.1,
        'a-w': 0.04,
    }
    agent_num = 5000
    simulation_step = 120

    # SEIR parameters
    beta = 0.01  # S -> E
    alpha = 0.01  # E -> I (asymptomatic)
    sym_rate = 0.01  # asymptomatic -> symptomatic
    sev_rate = 0.005  # symptomatic -> severe
    gamma = 0.015  # I (any stage) -> R

    # simulation ===============================================

    agents = [Agent() for _ in range(agent_num)]

    result_collection = []
    last_community_infection_rate = 0.0
    mean_concern_level = []

    # statistics for SEIR
    exposed_list = []
    asymptomatic_list = []
    symptomatic_list = []
    severe_list = []
    recovered_list = []

    # initialize the list to store the mask states count for each step
    mask_states_list = {
        "none": [],
        "surgical": [],
        "N95": []
    }

    infection_increase_rates = []

    # set 5 evacuation centers, each with max capacity of 1000
    evacuation_centers = [EvacuationCenter(max_capacity=1000) for _ in range(5)]

    for i in range(simulation_step):
        # start evacuation
        if 40 <= i <= 50:
            for agent in agents:
                # 90% chance to evacuate
                if random.random() < 0.9 and not agent.evacuation_center:
                    chosen_center = random.choice(evacuation_centers)
                    if chosen_center.current_occupancy < chosen_center.max_capacity:
                        agent.evacuation_center = chosen_center
                        chosen_center.current_occupancy += 1

        # adjust beta and alpha according to the simulation step
        if i > 60:
            beta = 0.001
            alpha = 0.001
            gamma = 0.05

        # summarize each step
        states_count = {"indifferent": 0, "worried": 0, "afraid": 0, "numb": 0}
        for agent in agents:
            states_count[agent.state] += 1
        print(f'step {i}: ', states_count)
        result_collection.append(states_count)

        # Compute the community infection rate
        community_infection_rate = sum([1 for agent in agents if agent.is_infected]) / agent_num
        # increase rate change
        if last_community_infection_rate != 0:
            infection_rate_change = (community_infection_rate - last_community_infection_rate) / last_community_infection_rate
        else:
            infection_rate_change = 0

        # calculate the infection_increase_rate in the for loop
        if i > 3:
            infection_increase_rates.append(infection_rate_change)
        last_community_infection_rate = community_infection_rate

        print(f'step {i}, community infection rate\'s change rate: ', infection_rate_change)

        concern_level_list = []

        # initialize the states count
        exposed_count = 0
        asymptomatic_count = 0
        symptomatic_count = 0
        severe_count = 0
        recovered_count = 0

        for agent in agents:
            agent.update_mask()  # update mask type
            agent.update_SEIR(beta, alpha, sym_rate, sev_rate, gamma)  # update SEIR state
            concern_level = agent.get_concern_level(i, infection_rate_change)

            concern_level = min(1.5, max(0.5, concern_level))  # Limit the concern level between 0.5 and 1.5

            adjusted_transfer_rates = {}
            concern_level_diff = concern_level - 1
            increase_list = ['i-w', 'w-a', 'a-n']
            decrease_list = ['w-i', 'a-w']
            for key, value in transfer_rates_dict.items():
                if key in increase_list:
                    adjusted_value = value * (1 + concern_level_diff)
                else:
                    adjusted_value = value * (1 - concern_level_diff)
                adjusted_transfer_rates[key] = adjusted_value

            transfer_rates = {
                "indifferent": ("worried", adjusted_transfer_rates['i-w']),
                "worried": ("afraid", adjusted_transfer_rates['w-a']) if random.random() < 0.5 else ("indifferent", adjusted_transfer_rates['w-i']),
                "afraid": ("numb", adjusted_transfer_rates['a-n']) if random.random() < 0.5 else ("worried", adjusted_transfer_rates['a-w'])
            }
            transfer_rates = {
                "indifferent": ("worried", adjusted_transfer_rates['i-w']),
                # adjust the transfer rate from worried to afraid according to the community infection rate
                "worried": ("afraid", adjusted_transfer_rates['w-a']) if random.random() < 0.5 else ("indifferent", adjusted_transfer_rates['w-i'] * (2 - concern_level)),
                "afraid": ("numb", adjusted_transfer_rates['a-n']) if random.random() < 0.5 else ("worried", adjusted_transfer_rates['a-w'])
            }

            agent.update_emotion(transfer_rates)
            concern_level_list.append(concern_level)
            agent.decay_concern()

            # update states count
            if agent.SEIR_state == "E":
                exposed_count += 1
            elif agent.SEIR_state == "I":
                if agent.infected_substate == "asymptomatic":
                    asymptomatic_count += 1
                elif agent.infected_substate == "symptomatic":
                    symptomatic_count += 1
                elif agent.infected_substate == "severe":
                    severe_count += 1
            elif agent.SEIR_state == "R":
                recovered_count += 1

        print(f'step {i}, mean concern level is: ', sum(concern_level_list) / len(concern_level_list), f"max: {max(concern_level_list)}", f"min: {min(concern_level_list)}")
        mean_concern_level.append(sum(concern_level_list) / len(concern_level_list))

        # add states count to the list
        exposed_list.append(exposed_count)
        asymptomatic_list.append(asymptomatic_count)
        symptomatic_list.append(symptomatic_count)
        severe_list.append(severe_count)
        recovered_list.append(recovered_count)

        mask_counts = {"none": 0, "surgical": 0, "N95": 0}
        for agent in agents:
            mask_counts[agent.mask] += 1
        for mask_type, count in mask_counts.items():
            mask_states_list[mask_type].append(count)

    indifferent_list = [result['indifferent'] for result in result_collection]
    worried_list = [result['worried'] for result in result_collection]
    afraid_list = [result['afraid'] for result in result_collection]
    numb_list = [result['numb'] for result in result_collection]
    plt.axvline(x=60, color='g', linestyle='--')
    plt.axvline(x=40, color='r', linestyle='--')
    plt.axvline(x=50, color='r', linestyle='--')
    plt.plot(indifferent_list, label='indifferent')
    plt.plot(worried_list, label='worried')
    plt.plot(afraid_list, label='afraid')
    plt.plot(numb_list, label='numb')
    plt.title('Emotion State Change over Time')
    plt.xlabel('Days')
    plt.ylabel('Number of Agents')
    plt.legend()
    plt.show()
    plt.close()

    # draw concern level line chart
    plt.plot(mean_concern_level)
    plt.title('Mean Concern Level')
    plt.xlabel('Days')
    plt.ylabel('Concern Level')
    plt.show()
    plt.close()

    # draw SEIR line chart
    plt.plot(exposed_list, label='Exposed')
    plt.plot(asymptomatic_list, label='Asymptomatic')
    plt.plot(symptomatic_list, label='Symptomatic')
    plt.plot(severe_list, label='Severe')
    plt.plot(recovered_list, label='Recovered')
    plt.plot([agent_num - sum([exposed_list[i], asymptomatic_list[i], symptomatic_list[i], severe_list[i], recovered_list[i]]) for i in range(len(exposed_list))], label='Susceptible')
    plt.legend()
    plt.title('SEIR Model with Detailed Infected States')
    plt.xlabel('Days')
    plt.ylabel('Population')
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(infection_increase_rates, label='Infection Increase Rate')
    plt.xlabel('Simulation Step')
    plt.ylabel('Increase Rate')
    plt.title('Community Infection Increase Rate over Time')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.close()

    # depict the mask states change over time
    plt.figure(figsize=(10, 6))
    for mask_type, counts in mask_states_list.items():
        plt.plot(counts, label=mask_type)

    plt.title("Mask State Over Time")
    plt.xlabel("Simulation Step")
    plt.ylabel("Number of Agents")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.close()
