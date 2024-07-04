"""Module defining helper functions for generating files with agent status or information."""


def add_header(file_path, header) -> None:
    """Adds a header to a file if it's empty, or creates the file with the header if it doesn't exist.
    Args:
        file_path (str): The path to the file where the header will be added.
        header (str): The header string to be written to the file.

    Returns:
        None
    """  
    try:
        with open(file_path, 'r') as file:
            if file.read().strip() == "":
                with open(file_path, 'a') as file:
                    file.write(header + '\n')
    except FileNotFoundError:
        with open(file_path, 'a') as file:
            file.write(header + '\n')


def write_delivered_O_to_file(order) -> None:
    """Writes information about a delivered order to a text file.

        The header includes columns for:
            - Current simulation step ("curr_step")
            - Order ID ("order_id")
            - Origin region
            - Destination region
            - Truck ID that delivered the order ("truck_id")
            - Order volume
    Args:
        order (OrderAgent): The delivered order object for which information will be written.
        filename_format (str, optional): The format string used to construct the filename.
                                            Defaults to "delivered_Os.txt".
    Returns:
        None
    """

    filename = f'generated_files/{order.model.instance_number}_{order.model.simu_run}_delivered_Os.txt'
    add_header(filename, "curr_step order_id origin destination truck_id volume")  
    with open(filename, 'a') as file:
        file.write(
            str(order.model.curr_step) + " " +
            str(order.order_id) + " " +
            str(order.origin) + " " +
            str(order.destination) + " " +
            str(order.truck.truck_id) + " " +
            str(order.volume) + '\n'
        )

def dispatched_truck_status(truck) -> None:
    """Writes dispatched truck status information to a text file.

        Writes a formatted string to the file, including information about the truck:
            - Current simulation step (using `truck.model.curr_step`)
            - Truck ID (using `truck.truck_id`)
            - Starting region (using `truck.start_region`)
            - Target region (using `truck.target_region`)
            - Order IDs in the truck's load:
                - Uses list comprehension (`[o.order_id for o in truck.load]` if `truck.load` exists,
                    otherwise writes an empty list "[]" as a string.
            - Total volume of orders in the truck's load:
                - Uses a conditional expression (`sum(o.volume for o in truck.load) if truck.load else 0`)
                    to calculate the total volume, handling cases where `truck.load` might be empty.

    **Note:** This function assumes the `TruckAgent` object represents a dispatched truck.
    Args:
        truck (TruckAgent): The dispatched truck object for which status information will be written.
    Returns:
        None
    """
    filename = f'generated_files/{truck.model.instance_number}_{truck.model.simu_run}_dispatched_truck_status.txt'
    header = "curr_step truck_id t_start_region t_destination_region order_ids tot_volume "
    add_header(filename, header)
    
    # Append the required information for each step
    with open(filename, 'a') as file:
        file.write(
            str(truck.model.curr_step) + " " +
            str(truck.truck_id) + " " +
            str(truck.start_region) + " " +
            str(truck.target_region) + " " +
            str([o.order_id for o in truck.load] if truck.load else "[]") + " " +
            str(sum(o.volume for o in truck.load) if truck.load else 0) + '\n'
        )
