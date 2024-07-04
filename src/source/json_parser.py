"""Parser for the arxiv problem instances. Initializes parent classes of all agents, and then creates agent instances."""


import json
from source.parent import Truck, Order, Region 
from source.agents import TruckAgent, OrderAgent, RegionAgent


def manual_create_regions() -> list[Region]:
  """Manually creates a list of Region objects.

  This function explicitly defines a list of regions and creates corresponding `Region` objects
  with the following attributes:

  - **region_id (int):** Unique identifier for the region.
  - **name (str):** Name of the region (e.g., 'klagenfurt').

  The function then returns the list of created `Region` objects.

  **Note:** This function serves for demonstration or visualization purposes. For further testing and development,
            loading region data from a data_sets or other configuration file is recommended.

  Returns:
      list[Region]: A list containing the manually created Region objects.
  """ 
  regions = []
  regions = [Region(1, 'klagenfurt'), Region(2, 'graz'), Region(3, 'wien'), Region(4, 'salzburg')]

  return regions

def create_agents(model, parsed_trucks, parsed_orders) -> None:
  """Creates and assigns agents (regions, trucks, orders) to the provided model.

  This function takes a model object, parsed truck data, and parsed order data as input
  and performs the following actions:

  1. **Create Regions:**
      - Calls `manual_create_regions` to obtain a list of `Region` objects.
      - Assigns the list of `RegionAgent` objects (`RegionAgent` is a subclass of `Region`)
        to the `model.regions` attribute.

  2. **Create TruckAgent:**
      - Iterates through the `parsed_trucks` list, afor each element, creates a `TruckAgent` object (`TruckAgent` is a subclass of `Truck`)
        using the model and the truck data.
      - Appends the created `TruckAgent` object to the `model.trucks` attribute, resulting in a list of truck agents.

  3. **Create OrderAgent:**
      - Iterates through the `parsed_orders` list, for each element, creates an `OrderAgent` object (`OrderAgent` is a subclass of `Order`).
        using the model and the order data.
      - Appends the created `OrderAgent` object to the `model.orders` attribute, resulting in a list of order agents (`OrderAgent`).

  Args:
      model (Model): The model object to which the agents will be assigned.
      parsed_trucks (list[Truck]): A list of Truck instances containing parsed truck data.
      parsed_orders (list[Order]): A list of Order instances containing parsed order data.

  Returns:
      None
  """
  regions = manual_create_regions()
  model.regions = [RegionAgent(model, region) for region in regions]
  model.trucks = [TruckAgent(model, truck) for truck in parsed_trucks]
  model.orders = [OrderAgent(model, order) for order in parsed_orders]

def parse_data_set(model, json_file) -> None:
  """Parses truck and order data from a JSON file and creates parents of corresponding agents.

  This function takes a model object and the path to a JSON data file as input. It performs the following actions:

  1. **Read JSON Data:**
      - Opens the specified `json_file` in read mode (`'r'`).
      - Uses `json.load(f)` to load the JSON data from the file and store it in the `data` variable.

  2. **Extract Data from JSON:**
      - Initializes empty lists `parsed_trucks` and `parsed_orders` to store parsed data.
      - Iterates through the `trucks` list in the JSON data:
          - For each truck entry, extracts attributes like `truckId`, `position`, `capacity`, and `freighter`
            (assuming these keys exist in the JSON structure).
          - Creates a `Truck` object (parent of `TruckAgent`) using the extracted attributes and appends
            it to the `parsed_trucks` list.
      - Iterates through the `orders` list in the JSON data:
          - For each order entry, extracts attributes like `orderId`, `origin`, `destination`, and `volume`
            (assuming these keys exist in the JSON structure).
          - Creates an `Order` (parent of `OrderAgent`) object using the extracted attributes and appends
            it to the `parsed_orders` list.

  3. **Create Agents:**
      - Calls the `create_agents` function to create agent objects from the parents
        (regions[`Region`], trucks[`Truck`], orders[`Order`]) to the provided model using the parsed data.

  Args:
      model (Model): The model object to which the agents will be assigned.
      json_file (str): The path to the JSON file containing truck and order data.

  Returns:
      None
  """

  with open(json_file, 'r') as f:
    data = json.load(f)

  # Extract data from the JSON structure
  parsed_trucks = []
  parsed_orders = []

  for truck in data["trucks"]:
    parsed_trucks.append(Truck(truck['truckId'], truck['position'], truck['capacity'], truck['freighter']))
  for order in data["orders"]:
    parsed_orders.append(Order(order['orderId'], order['origin'], order['destination'], order['volume']))


  create_agents(model, parsed_trucks, parsed_orders)
