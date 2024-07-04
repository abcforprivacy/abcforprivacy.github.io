"""Module defining agents (init) and their behavior (step)."""

import mesa
import numpy as np
import random

import source.helperOrder as ho
import source.helperTruck as ht
import source.abc as abc
import source.file as fl


class BackgroundAgent(mesa.Agent):
    def __init__(self, unique_id: int, model, pos) -> None:
        super().__init__(unique_id, model)
        self.pos = pos
        self.layer = 0
        self.size = model.space_size

        model.space.place_agent(self, pos)
        model.schedule.add(self)


class RegionAgent(mesa.Agent):
    position = [(17.0, 5.0), (29.0, 13.0), (39.0, 34.0), (3.0, 26.0)]
    KLF = position[0]
    GRZ = position[1]
    WIE = position[2]
    SLZ = position[3]

    def __init__(self, model, parsed_region) -> None:
        super().__init__(model.next_id(), model)    
        # parsed vars:
        self.name = parsed_region.name
        self.region_id = parsed_region.id
        self.pos = RegionAgent.get_position(self, self.region_id)

    def get_position(agent, region_id)  -> tuple:
        """returns coordinates of the region id, mainly for visualization

        Args:
            agent (TruckAgent, RegionAgent): instance requiring region coordinates
            region_id (int): id of the assigned region

        Returns:
            tuple: (x, y) coordinates
        """        
        pos = None
        if region_id == 1:
            pos = RegionAgent.KLF
        elif region_id == 2:
            pos = RegionAgent.GRZ
        elif region_id == 3:
            pos = RegionAgent.WIE
        elif region_id == 4:
            pos = RegionAgent.SLZ

        return pos
        


class FreighterAgent(mesa.Agent):
    def __init__(self, model, parsed_freighter) -> None:
        super().__init__(model.next_id(), model)
        # parsed vars:
        self.freighter_id = parsed_freighter.id
        self.name = parsed_freighter.name
        self.trucks = parsed_freighter.trucks

        model.schedule.add(self)

class OrderAgent(mesa.Agent):
        unsorted_Os = []

        def __init__(self, model, parsed_order) -> None:
            super().__init__(model.next_id(), model)
            # parsed vars:
            self.order_id = parsed_order.id
            self.origin = parsed_order.origin
            self.destination = parsed_order.destination
            self.volume = parsed_order.volume
            self.timer = 10

            # simu-related vars
            self.delivered = False
            self.placed = False
            self.truck = None
            self.request = False
            self.req_t = None

            # ABC related vars
            self.OB = self.SB = self.EB = False

            model.schedule.add(self)

            # simu-related funcs in helperOrder.py

            
        def step(self):
            trucks_with_same_origin = trucks_with_same_destination = empty_trucks_with_same_origin = []
            EBs_in_trucks = EBs_in_trucks_with_space = []
            max_fit_EB = None
            Pr_max_fit = rnd_num = 0
            if not self.placed:
                # prepare for the ABC loop:
                trucks_with_same_origin = ho.trucks_with_same_origin(self, self.model.trucks)
                if trucks_with_same_origin:                    
                    trucks_with_same_destination = ho.trucks_with_same_destination(self, trucks_with_same_origin)
                    if not trucks_with_same_destination:
                        empty_trucks_with_same_origin = ho.empty_trucks_with_same_origin(trucks_with_same_origin)

                # start the ABC loop
                if not trucks_with_same_origin:
                    if not self.request:          
                        available_trucks = [truck for truck in self.model.trucks if (truck.start_region != self.origin and truck.target_region != self.origin)]
                        if available_trucks:
                            ho.request_truck(self, available_trucks)

                    OrderAgent.unsorted_Os.append(self)


                elif trucks_with_same_destination:
                    # prepare for OB Phase
                    EBs_in_trucks = [order for truck in trucks_with_same_destination for order in truck.load if order.EB]

                    for eb in EBs_in_trucks:
                        if ho.fits(self, eb.truck):  # Check if truck has space for the EB
                            EBs_in_trucks_with_space.append(eb)
                    
                    if EBs_in_trucks_with_space:                       # EB in at least 1 truck (any), not in all of trucks
                        max_fit_EB = max(EBs_in_trucks_with_space, key=lambda EB: EB.fitness)
                        Pr_max_fit = abc.calculate_probability(max_fit_EB, EBs_in_trucks_with_space)
                        
                        # OB Phase
                        rnd_num = random.random()
                        if Pr_max_fit > rnd_num:
                            ho.assign_truck(self, max_fit_EB.truck)
                            abc.calculate_fitness(max_fit_EB) 
                         
                        else:
                            abc.SB_Phase(self, trucks_with_same_destination, OrderAgent.unsorted_Os)                            
                            
                    elif empty_trucks_with_same_origin:
                        # SB Phase
                        abc.SB_Phase(self, empty_trucks_with_same_origin, OrderAgent.unsorted_Os)
                       
                elif empty_trucks_with_same_origin:
                        # SB Phase
                        abc.SB_Phase(self, empty_trucks_with_same_origin, OrderAgent.unsorted_Os)

            self.timer -= 1
             


class TruckAgent(mesa.Agent):
    layer = 1
    truck_shapes = ['img/F1_truck.png','img/F2_truck.png','img/F2_truck.png']
    limit = 10               # ABC-related parameter - decreased in every instance step when self.collecting_orders

    Ts_in_R1 = []
    Ts_in_R2 = []
    Ts_in_R3 = []
    Ts_in_R4 = []
    
    
    def __init__(self, model, parsed_truck) -> None:
        super().__init__(model.next_id(), model)
        # parsed vars:
        self.truck_id = parsed_truck.id
        self.capacity = parsed_truck.capacity
        self.start_region = parsed_truck.start_region
        self.freighter = parsed_truck.freighter

        # simu-related vars
        self.target_region = None
        self.vector = None
        self.shape = self.truck_shapes[self.freighter]
        self.next_pos = None
        self.pos = RegionAgent.get_position(self, self.start_region)
        self.dispatched = False
        self.requested = False
        self.req_o = None
        #movement vars
        self.target_pos = None
        self.heading = None
        self.angle = 0.0

        #analysis vars
        self.total_volume = 0

        # abc-related vars
        self.objective = None
        self.fitness = None
        self.timer = self.limit
        self.collect_orders = True                                              # initially at the starting region, trucks collect, then depart
        self.load = []                                                          # list of all collected orders

        getattr(TruckAgent, f'Ts_in_R{self.start_region}', []).append(self)     #adds truck to a list of all trucks in the same region 

        model.space.place_agent(self, self.pos)
        model.schedule.add(self)
        
        # simu-related funcs in helperTruck.py    

    def step(self):

        if self.dispatched:
            
            distance = np.round(np.linalg.norm(np.array(self.pos) - np.array(self.target_pos)), 2)
            self.pos = self.pos + self.model.dt * self.model.agent_velocity * np.array([np.cos(self.angle), np.sin(self.angle)])

            if distance < 1:
                if self.requested:
                    self.requested = False

                else:
                    ht.deliver_orders(self)
                    self.total_volume = 0

                ht.adjust_curr_region(self)                   
                self.dispatched = False
                self.collect_orders = True

        elif self.load:
            if ht.ready_to_dispatch(self):
                order = random.choice(self.load)                     # any order bcs all have same dest
                self.target_region = order.destination 
                self.target_pos = RegionAgent.get_position(self, self.target_region)
                ht.adjust_target_region(self, self.target_pos) 
                self.collect_orders = False

                self.total_volume = sum(o.volume for o in self.load)
                self.dispatched = True
                fl.dispatched_truck_status(self)
        
        elif self.requested:
            self.target_pos = RegionAgent.get_position(self, self.target_region)
            ht.adjust_target_region(self, self.target_pos)  
            self.collect_orders = False
            self.total_volume = 0

            self.dispatched = True
            fl.dispatched_truck_status(self)