"""Module defining helper functions for order agents."""

import random


def assign_truck(order, truck) -> None:
    """Assigns an order to a truck and updates their attributes:

    This function performs the following actions:
    1. Assigns the truck to the order:
        - Sets the order's `truck` attribute to the specified `truck`.
        - Marks the order as placed (`order.placed = True`).
    2. Adds the order to the truck's load:
        - Appends the `order` to the `truck.load` list.
    3. Updates the load of existing `EB` (employed bee) order in the truck:
        - Iterates through existing orders in the `truck.load` list.
            - If an existing order has the `EB` attribute set to `True` ("Employed Bee"),
              it appends the `order` to that existing order's load (so that other orders don't access this information directly from the truck).
    4. Handles order request:
        - If the `order` has a `request` attribute that evaluates to `True`, it sets it to `False`
          (indicating the request is fulfilled).
    Args:
        order (OrderAgent): The order to be assigned to a truck.
        truck (TruckAgent): The truck to which the order will be assigned.
    Returns:
        None
    """  
    order.truck = truck
    order.placed = True
    truck.load.append(order)

    [o.load.append(order) for o in truck.load if o.EB]

    if order.request:
        order.request = False

def trucks_with_same_origin(order, all_trucks) -> list:
    """Finds trucks starting from the same origin as the given order.

    This function iterates through the provided list of `all_trucks` and returns a new list containing
    only the trucks whose `start_region` attribute matches the `origin` attribute of the specified `order`.

    Args:
        order (OrderAgent): The order whose origin is used to find matching trucks.
        all_trucks (list[TruckAgent]): A list containing all trucks to check.
    Returns:
        list[TruckAgent]: A new list containing trucks starting from the same region as the order.
    """        
    return [truck for truck in all_trucks if truck.start_region == order.origin]

def trucks_with_same_destination(order, truck_list) -> list:
    """Finds trucks with the same destination as the given order, considering available space.

    This function iterates through the provided `truck_list` and returns a new list containing only the trucks
    that meet two criteria:

    1. **Matching Destination:** The truck's destination (`truck.target_region` - assuming this attribute
       represents the destination) must match the `destination` attribute of the `order`.
    2. **Sufficient Space:** The truck must have at least some existing load (checked using `truck.load`),
       indicating it's not empty. No check for enough space to accommodate the new order is here necessary.

    Args:
        order (OrderAgent): The order whose destination is used to find matching trucks.
        truck_list (list[TruckAgent]): A list containing all trucks to check.

    Returns:
        list[TruckAgent]: A new list containing trucks with the same destination as the order,
                          potentially not considering available space (further checks might be needed).
    """
    possible_trucks = []
    for truck in truck_list:
        if truck.load:
            for o in truck.load:
                if o.destination == order.destination:
                    possible_trucks.append(truck)
                    break
    return possible_trucks

def empty_trucks_with_same_origin(truck_list) -> list:
    """Finds empty trucks from the provided list that share the same origin.

    This function assumes the `truck_list` contains trucks with a common origin. It iterates through the list
    and returns a new list containing only the trucks that have an empty load (checked by `not truck.load`).

    Args:
        truck_list (list[TruckAgent]): A list of trucks (assumed to have a common origin) to check.

    Returns:
        list[TruckAgent]: A new list containing empty trucks from the provided list.
    """   

    possible_trucks = []
    for truck in truck_list:
        if not truck.load:
            possible_trucks.append(truck)
    return possible_trucks


def fits(order, truck) -> bool:
    """Checks if an order can fit on a truck considering the current load.

    This function calculates the total volume of the truck's existing load (`truck.load`) and adds the volume
    of the specified `order`. It then compares the sum to the truck's capacity (`truck.capacity`).

    Returns:
        bool: True if the order's volume can be accommodated on the truck (considering existing load),
              False otherwise.
    """
    total_volume = sum(o.volume for o in truck.load)
    if total_volume + order.volume <= truck.capacity:
        return True                    
    else:
        return False

def send_request(order, truck) -> None:
    """Sends a request for a truck to pick up an order.

    This function updates the attributes of both the `order` and `truck` to indicate a request has been sent:

    - **Order:** Sets the `order.request` attribute to `True` (to signify a request is made).
    - **Truck:** Sets the `truck.requested` attribute to `True` (to indicate a truck is being requested).

    Additionally, the function sets the `truck.target_region` attribute to the `order.origin`,
    signaling that the truck is now targeting the order's origin as its destination.

    Args:
        order (OrderAgent): The order for which a truck is being requested.
        truck (TruckAgent): The truck that is being requested to pick up the order.

    Returns:
        None
    """
    order.request = True
    truck.requested = True
    truck.target_region = order.origin


def request_truck(order, available_trucks) -> None:   
    """Requests a truck from another region to pick up an order, prioritizing available trucks. 
        The function is called when no trucks are located in the region of the order.

        This function aims to efficiently assign a truck to an order (`order`) by considering only available trucks
        from the provided `available_trucks` list. An available truck is defined as one that meets the following criteria:

        - **Not Dispatched:** The truck is not currently on a delivery route (`not truck.dispatched`).
        - **Empty Load:** The truck has no existing orders in its load (`not truck.load`).
        - **Not Requested:** The truck hasn't been requested by another order yet (`not truck.requested`).

        If there are any available trucks identified, the function randomly selects one using `random.choice` and sends a
        request using the `send_request` function.

        Args:
            order (OrderAgent): The order that needs a truck for pickup.
            available_trucks (list[TruckAgent]): A list of available trucks to consider for the request.

        Returns:
            None
    """
    possible_trucks = [truck for truck in available_trucks if (not truck.dispatched and not truck.load and not truck.requested)]
    if possible_trucks:
        rnd_truck = random.choice(possible_trucks) 
        send_request(order, rnd_truck)






