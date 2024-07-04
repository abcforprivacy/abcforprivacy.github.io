"""Parent class definitions initialized with json parser, that reads in the problem instance. Meant for corresponding agent classes to inherit."""

class Truck():
    def __init__(self, truck_id, position, capacity, freighter):
        self.id = truck_id
        self.capacity = capacity
        self.start_region = position
        self.freighter = freighter

class Order():
    def __init__(self, order_id, origin, destination, volume):
        self.id = order_id
        self.origin = origin
        self.destination = destination
        self.volume = volume

class Region():
    def __init__(self, region_id, name):
        self.id = region_id
        self.name = name