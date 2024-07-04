"""Module defining the UI of the simu in a web browser."""

import mesa
from source.model import TransportationModel, BackgroundAgent
from source.agents import TruckAgent
from source.ContinuousCanvasModule import ContinuousCanvasModule

SPACE_SIZE = 50.
CANVAS_SIZE = 600

def portrayal_method(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is TruckAgent:
        portrayal['Shape'] = agent.shape
        portrayal['size'] = agent.model.agent_radius
        portrayal['text'] = '{}'.format(agent.freighter)
        portrayal['Layer'] = agent.layer
        
    elif type(agent) is BackgroundAgent:
        portrayal['Shape'] = 'img/map.jpg'
        portrayal['Layer'] = agent.layer
        portrayal['size'] = agent.size

    return portrayal

canvas_element = ContinuousCanvasModule(portrayal_method, SPACE_SIZE, SPACE_SIZE, CANVAS_SIZE, CANVAS_SIZE)

model_params = {
    'space_size': SPACE_SIZE,
    'curr_step' : 0,
    'agent_radius': 3.,
    'agent_velocity': 10.,
    'dt': 6e-2
}

server = mesa.visualization.ModularServer(TransportationModel, [canvas_element] , 'ABC-based task scheduling in logistics', model_params)
server.port = 8521