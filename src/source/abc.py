"""Module defining functions specific to the ABC algorithm implementation."""

import random
import source.helperOrder as hp


def calculate_objective(O_EB, truck) -> float:
    """Calculates an objective function value for assigning an Eastbound (EB) order to a truck.

    This function takes an employed bee order (`O_EB`) and a truck (`truck`) as input. It calculates a
    weighted objective function value that considers three factors:

    1. **Objective Load:** (higher weight `w_1`)
        - Calculated as the remaining capacity of the truck (capacity - total load on the truck).

    2. **Objective Position (Currently Unused):** (weight `w_2`)
        - Calculated as the absolute distance between the truck's starting region and the order's origin
        - A smaller distance is generally preferred.

    3. **Objective Availability (Currently Unused):** (weight `w_3`)
        - It's intended to represent a measure of truck availability, i.e., in what time (steps) will the truck become available deliver orders
        - This part of the function is currently assuming only imediately available trucks (`objective_availability = 0`)

    Args:
        O_EB (OrderAgent): order employed (loaded) at this truck
        truck (TruckAgent): truck which needs its objective value calculated

    **Note:** The weights `w_1`, `w_2`, and `w_3` can be adjusted to prioritize different factors based on the specific problem requirements.
    Returns:
        float: The calculated objective function value.
    """    
    total_load = sum(order.volume for order in truck.load)
    w_1 = 1
    w_2 = 0
    w_3 = 0

    objective_load = truck.capacity - total_load
    objective_position = abs(truck.start_region - O_EB.origin)
    if O_EB.origin == truck.start_region:                  
        objective_availability = 0

    objective_func = round((w_1 * objective_load  + w_2 * objective_position + w_3 * objective_availability), 4)

    return objective_func

def calculate_fitness(O_EB):
    """calculates fitness according to the formula in the ABC description

    Args:
        O_EB (OrderAgent): order with EB flag, this order needs to calculate fitness of an assigned truck 
    """    
    truck = O_EB.truck
    truck.objective = calculate_objective(O_EB, truck)
    if truck.objective > 0:
        truck.fitness =  round(1 / (1 + truck.objective), 4)
    else:
        truck.fitness = 0

def calculate_probability(max_fit_EB, EBs_in_trucks_with_space) -> float:
    """Calculates the probability of a truck being selected based on its fitness value.

    Args:
        max_fit_EB (OrderAgent): order with EB flag that's loaded to a truck with highest fitness value
        EBs_in_trucks_with_space (list[OrderAgents]): other EB orders loaded to other trucks that still have space for other orders

    Returns:
        float: Probability with which will onlooker bee (OB) order choose the best (fitness) advertized truck
    """    
    Pr = None
    Pr = max_fit_EB.fitness / sum(EB.fitness for EB in EBs_in_trucks_with_space)
    return Pr

def become_EB(order) -> None:
    """Assumes order came from SB phase (with SB status) and therefore upon truck selection becomes employed by this truck (food source),
      i.e., changes its status to order.EB = True (employed bee).
      This order will hold all truck information, so that other orders (bees) access the information from employed bee (EB) order:
      truck's fitness, load, and capacity

    Args:
        order (OrderAgent): order that becomes employed by this truck (order.EB = True)
    """    
    calculate_fitness(order)
    order.EB = True
    order.fitness = order.truck.fitness     
    order.load = order.truck.load.copy() if order.truck.load else []
    order.capacity = order.truck.capacity   

    
def SB_Phase(order, possible_trucks, unsorted_Os) -> None:
    """Implements Scout Bee (SB) Phase of the ABC algorithm to assign a truck to an order.

    This function takes an `OrderAgent` object, a list of possible trucks, and a list of unsorted orders
    as input. It attempts to assign a truck to the order based on the SB phase logic.

    1. **Check for Possible Trucks:**
        - If the `possible_trucks` list is empty, it means there are no available trucks for the order's
          destination, at this simulation step. In this case, the order is appended to the `unsorted_Os` list, to try at the next simu step.

    2. **Iterate Through Possible Trucks:**
        - If `possible_trucks` is not empty, a random truck is chosen
        - The total volume of orders currently loaded on the chosen truck is calculated

    3. **Check Truck Capacity:**
        - If the total volume plus the order's volume is less than or equal to the truck's capacity:
            - The `hp.assign_truck` function is called to assign the truck to the order.
            - If none of the existing orders on the truck have the "EB" (Employed Bee) order, the `become_EB`
              function is called, to label this order as the new employed bee (order.EB = True) of this truck (food source)
            - The loop is broken since a truck has been assigned.

    4. **Remove Truck Without Capacity:**
        - If the total volume exceeds the truck's capacity, the chosen truck is removed from the `possible_trucks` list
          to avoid considering it again. The loop continues to the next truck.

    5. **Empty Trucks from Same Origin (if an order came from OB phase in agents.py):**
        - If there were no possible trucks initially (no possible trucks of same origin and destination)
        - There might be trucks with the same origin that are empty.
        - It retrieves all trucks with the same origin as the order using `hp.trucks_with_same_origin`
        - It then filters those trucks to find empty ones using `hp.empty_trucks_with_same_origin`
        - If there are empty trucks with the same origin:
            - A random empty truck is chosen from the list.
            - The `hp.assign_truck` function is called to assign this empty truck to the order.
        - If there are no empty trucks with the same origin, the order is appended to the `unsorted_Os` list.

    6. **Unsorted Orders:**
        - If no suitable truck is found in either scenario (trucks with same origin and destination or empty trucks from same origin),
          the order is appended to the `unsorted_Os` list, indicating it couldn't be assigned during this simulation step 
          (e.g. no space in truck load or no trucks at order.region).

    Args:
        order (OrderAgent): The order for which a truck needs to be assigned.
        possible_trucks (list[TruckAgent]): A list of possible trucks with the same destination as the order.
        unsorted_Os (list[OrderAgent]): A list to store unsorted or unassigned orders.

    Returns:
        None
    """
    
    if possible_trucks:
        while possible_trucks:
            rnd_truck = random.choice(possible_trucks)
            total_volume = sum(o.volume for o in rnd_truck.load)

            if total_volume + order.volume <= rnd_truck.capacity:
                hp.assign_truck(order, rnd_truck)
                if not any(o.EB for o in rnd_truck.load):
                    become_EB(order)                            
                break
            else:
                possible_trucks.remove(rnd_truck)
        else:
            trucks_with_same_origin = hp.trucks_with_same_origin(order, order.model.trucks)
            empty_trucks_with_same_origin = hp.empty_trucks_with_same_origin(trucks_with_same_origin)
            if empty_trucks_with_same_origin:
                rnd_truck = random.choice(empty_trucks_with_same_origin)
                hp.assign_truck(order, rnd_truck)
            else:
                unsorted_Os.append(order)

    else:
        unsorted_Os.append(order)


