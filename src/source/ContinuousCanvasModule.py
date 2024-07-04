from mesa.visualization.ModularVisualization import VisualizationElement
from collections import defaultdict

class ContinuousCanvasModule(VisualizationElement):
    """
    Possible elements to visualize and their properties:
        portrayal = { # rectangle
            'Shape': 'rect',
            'Layer': int number,
            'w': width,
            'h': hight,
            'Color': color | list of colors for gradient,
            'Filled': boolean True or False,
            'stroke_color': color, # NOT NECESSARY
            'xAlign': 0 means centered horizontally, # NOT NECESSARY
            'yAlign': 0 means centered vertically, # NOT NECESSARY
            'text': inscribed text, # NOT NECESSARY
            'text_color': color # NOT NECESSARY
            }
        portrayal = { # circle
            'Shape': 'circle',
            'Layer': int number,
            'r': radius,
            'Color': color | list of colors for gradient,
            'Filled': boolean True or False,
            'stroke_color': color, # NOT NECESSARY
            'xAlign': 0 means centered horizontally, # NOT NECESSARY
            'yAlign': 0 means centered vertically, # NOT NECESSARY
            'text': inscribed text, # NOT NECESSARY
            'text_color': color # NOT NECESSARY
            }
        portrayal = { # arrow/vector
            'Shape': 'arrow',
            'Layer': int number,
            'w': width,
            'h': height or length,
            'angle': the direction where the arrow is pointing,
            'Color': color | list of colors for gradient,
            'Filled': boolean True or False,
            'stroke_color': color, # NOT NECESSARY
            'vector_origin': 0 means the origin is in the (x,y) coordinate, # NOT NECESSARY
            'text': inscribed text, # NOT NECESSARY
            'text_color': color # NOT NECESSARY
            }
        portrayal = { # custom image
            'Shape': path to image,
            'Layer': int number,
            'size': length of each sides of the image,
            'text': inscribed text, # NOT NECESSARY
            'text_color': color # NOT NECESSARY
            }
    """
    local_includes = ['ContinuousCanvasModule.js']
    local_dir = 'source'

    def __init__(self,
        portrayal_method,
        max_x,
        max_y,
        canvas_width = 500,
        canvas_height = 500,
        min_x = 0,
        min_y = 0
    ):
        self.portrayal_method = portrayal_method
        self.max_x = max_x
        self.max_y = max_y
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.min_x = min_x
        self.min_y = min_y

        new_element = 'new ContinuousCanvasModule({}, {}, {}, {}, {}, {})'.format(self.max_x, self.max_y, self.canvas_width, self.canvas_height, self.min_x, self.min_y)
        self.js_code = 'elements.push(' + new_element + ');'


    def render(self, model):
        grid_state = defaultdict(list)
        for agent in model.space._agent_to_index:
            portrayal = self.portrayal_method(agent)
            if portrayal:
                portrayal['x'] = agent.pos[0]
                portrayal['y'] = agent.pos[1]
                grid_state[portrayal['Layer']].append(portrayal)

        return grid_state
