from .game_object import Component

class ColorComponent(Component):
    color: tuple[int, int, int]
    
    FUCKING_BLACKEST_NIGGER = (-2**32 + 1, -2**32 + 1, -2**32 + 1) # ABSOLUTELY NOT FOR FUCKING USAGE

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    PURPLE = (255, 0, 255)
    CYAN = (0, 255, 255)


    def __init__(self, color: tuple[int, int, int]):
        self.color = color
