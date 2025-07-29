from .game_object import Component, GameObject
from .surface import SurfaceComponent
from .color import ColorComponent
from .transform import Transform
from .vmath_mini import Vector2d
import pygame as pg



class LabelComponent(Component):
    text: str
    font: pg.font.Font

    def __init__(self, text: str, font: pg.font.Font = None):
        self.text = text
        if font is None: font = pg.font.SysFont("consolas", 30)
        self.font = font

    def set_sys_font(self, name: str, size: int, bold = 0, italic = 0):
        self.font = pg.font.SysFont(name, size, bold, italic)

    def draw(self):
        surf = self.game_object.get_component(SurfaceComponent)
        text = self.font.render(self.text, 1, self.game_object.get_component(ColorComponent).color)

        surf.pg_surf.blit(text, ((surf.size - Vector2d.from_tuple(text.get_size())) / 2).as_tuple())

