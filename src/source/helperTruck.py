"""Module defining helper functions for truck agents."""

import numpy as np
import source.file as fl

def adjust_target_region(truck, target_pos) -> None:    
    """sets new target coordinates (from target region) and corresponding heading and angle towards the region
    Args:
        truck (TruckAgent)
        target_pos (tuple): (x,y) coordinates of the targeted region
    Returns:
        None
    """         
    truck.heading = truck.model.space.get_heading(truck.pos, truck.target_pos)
    truck.angle = np.arctan2(truck.heading[1], truck.heading[0])


def one_order_due(truck) -> bool:
    """Checks if there is at least one order in the truck's load that is due (has a timer of 0).
    Args:
        truck (TruckAgent): The truck object whose load needs to be checked.
    Returns:
        bool: True if at least one order is due, False otherwise.
    """    
    if any(order.timer == 0 for order in truck.load):
        return True
    else:
        return False
    

def ready_to_dispatch(truck) -> bool:
    """Checks if a truck is ready to be dispatched, considering two factors:

    1. **Unplaced Orders with Matching Origin-Destination:**
        - Identifies unplaced orders (not yet assigned to a truck) that share the
            same origin and destination as at least one order already loaded on the truck.
    2. **Truck Capacity and Due Orders:**
        - If there are any unplaced orders with matching origin-destination:
            - Calculates the minimum volume required among them.
            - Checks if there's enough free space on the truck (capacity - current load)
                to accommodate the minimum volume.
            - Additionally, checks if there's at least one due order (`one_order_due(truck)`)
                already on the truck.
    Returns:
        bool: True if the truck is ready to dispatch (no matching unplaced orders
                or enough space for them, and no due orders), False otherwise.
    """

    same_orig_dest_Os = []
    for o in truck.model.orders:
        if not o.placed and any(
            l.origin == o.origin and l.destination == o.destination for l in truck.load
            ):
            same_orig_dest_Os.append(o)

        if same_orig_dest_Os:
            min_available_volume = min(o.volume for o in same_orig_dest_Os)
            total_load = sum(o.volume for o in truck.load)
            free_space = truck.capacity - total_load
            if free_space < min_available_volume or one_order_due(truck):
                return True
        else:
            return True
    

    
def empty_truck_load(truck) -> None:
    """Empties the load of the specified truck.
    This function removes all orders currently assigned to the truck.
    Args:
        truck (TruckAgent): The truck whose load needs to be emptied.
    Returns:
        None
    """ 
    truck.load = []    

def deliver_orders(truck) -> None:
    """Marks all orders in the truck's load as delivered and writes them to a file.

    This function iterates through each order in the truck's load, sets its `delivered` attribute to `True`,
    and calls the `fl.write_delivered_O_to_file(o)` function to write information about the delivered order to a file. 
    Finally, it calls `empty_truck_load(truck)` to remove all orders from the truck.
    Args:
        truck (TruckAgent): The truck that has reached its destination and whose orders need to be marked as delivered and written to a file.
    Returns:
        None
    """
    for o in truck.load:
        o.delivered = True
        fl.write_delivered_O_to_file(o)
    empty_truck_load(truck)
    

def adjust_curr_region(truck) -> None:
    """Updates the truck's current region based on its target region.
    This function sets the truck's `start_region` attribute to its current `target_region`,
    effectively marking the target region as the new current region. It then clears the `target_region`
    attribute, indicating that the truck has reached its previous target.
    Args:
        truck (TruckAgent): The truck whose current and target regions need to be adjusted.
    Returns:
        None
    """
    
    truck.start_region = truck.target_region
    truck.target_region = None
