"""
Copyright (c) 2024 Gojković, M.
This work is licensed under a Creative Commons Attribution 4.0 International License. 
License text can be found at https://creativecommons.org/licenses/by/4.0/deed.en
"""


"""
Transportation Model 

Applies modeled Artificial Bee Colony (ABC) swarm algorithm for task scheduling in logistics, while preserving freighter's privacy. 
The accompanying scientific paper: Gojković, M., and Schranz, M. (in press). Preserving Privacy in Logistics by using Swarm Intelligence from the Bottom-Up. 
                                   In Proceedings of the 12th IEEE International Conference on Intelligent Systems. 

"""


import mesa
import source.json_parser as jp
import performance_analysis.load_per_drive as an

from source.agents import BackgroundAgent


class TransportationModel(mesa.Model):

    description = (
        "A model for simulating task scheduling in logistics, while preserving freighter's privacy. The model is based on the Artificial Bee Colony swarm algorithm."
    )


    instance_number = input("Choose problem instance number 11, 139 or 180: ")
    
    def __init__(self,
        space_size = 50.,
        agent_radius = 1.,
        agent_velocity = 10,
        dt = 1e-3,
        curr_step = 0,
        simu_run = 0
    ) -> None:
        super().__init__()
        self.simu_run = simu_run
        self.space_size = space_size
        self.curr_step = curr_step
        self.space = mesa.space.ContinuousSpace(space_size, space_size, torus = False)
        self.schedule = mesa.time.BaseScheduler(self)

        self.agent_radius = agent_radius
        self.agent_velocity = agent_velocity
        self.dt = dt 

        self.trucks = []
        self.regions = []
        self.orders = []
        self.freighters = []

        json_file = f'./data_sets/problem_instance_{self.instance_number}.json'  
        jp.parse_data_set(self,json_file)
        
        pos = (space_size / 2, space_size / 2)
        background = BackgroundAgent(self.next_id(), self, pos)
        self.space.place_agent(background, pos)


    def step(self):

        self.schedule.step()
        self.curr_step += 1
                
        if all (o.delivered for o in self.orders):
            an.process_dispatched_trucks(self.instance_number, self.simu_run)
            print("Simulation done.")
            self.running = False

    def run_model(self):
        
        while self.running:            
            self.step()

            
       

    
