from .vmath_mini import Vector2d
from .game_object import Component
from .surface import SurfaceComponent
from .transform import Transform
from typing import Callable
from .color import ColorComponent
import pygame as pg

class ShapeComponent(Component):
    collide_formula: Callable[[Vector2d], bool]

    def __init__(self, collide_formula: Callable[[Vector2d], bool]) -> None:
        self.collide_formula = collide_formula

    def does_collide(self, pos: Vector2d) -> bool:
        return self.collide_formula((pos - self.game_object.get_component(Transform).pos).complex_multiply(self.game_object.get_component(Transform).rotation.to_vector2d()))

    def __str__(self):
        return f""

class CircleShapeComponent(ShapeComponent):
    radius: float
    need_draw: bool

    def __init__(self, radius: float, need_draw: bool = True) -> None:
        def collide_formula(pos: Vector2d) -> bool:
            return (pos.x**2 + pos.y**2) <= radius**2
        super().__init__(collide_formula)
        self.radius = radius
        self.need_draw = need_draw

    def does_collide(self, pos: Vector2d) -> bool:
        return self.collide_formula(pos - self.game_object.get_component(Transform).pos)

    def draw(self):
        if not self.need_draw:
            return
        if self.game_object.contains_component(ColorComponent):
            pg.draw.circle(
                surface=self.game_object.get_component(SurfaceComponent).pg_surf, 
                color=self.game_object.get_component(ColorComponent).color, 
                center=(Vector2d.from_tuple(self.game_object.get_component(SurfaceComponent).pg_surf.get_size()) / 2).as_tuple(),
                radius=self.radius
            )

    def __str__(self):
        return f"CircleComponent: {self.radius}"
    
class RectShapeComponent(ShapeComponent):
    size: Vector2d
    need_draw: bool

    def __init__(self, size: Vector2d, need_draw: bool = True) -> None:
        def collide_formula(pos: Vector2d) -> bool:
            return 2 * abs(pos.x) <= size.x and 2 * abs(pos.y) <= size.y
        super().__init__(collide_formula)
        self.size = size
        self.need_draw = need_draw

    def draw(self):
        if not self.need_draw:
            return
        if self.game_object.contains_component(ColorComponent):
            pg.draw.rect(
                surface=self.game_object.get_component(SurfaceComponent).pg_surf, 
                color=self.game_object.get_component(ColorComponent).color, 
                rect=((((Vector2d.from_tuple(self.game_object.get_component(SurfaceComponent).pg_surf.get_size()) - self.size) / 2)).as_tuple() + self.size.as_tuple())
            )

    def __str__(self):
        return f"RectComponent: {self.size}"


class RectBorderShapeComponent(ShapeComponent):
    size: Vector2d
    width: float
    need_draw: bool

    def __init__(self, size: Vector2d, width: float, need_draw: bool = True) -> None:
        def collide_formula(pos: Vector2d) -> bool:
            return (2 * abs(pos.x) <= size.x and 2 * abs(pos.y) <= size.y) and not (2 * abs(pos.x) <= size.x - 2 * self.width and 2 * abs(pos.y) <= size.y - 2 * self.width)
        super().__init__(collide_formula)
        self.size = size
        self.width = width
        self.need_draw = need_draw

    def draw(self):
        if not self.need_draw:
            return
        if self.game_object.contains_component(ColorComponent):
            pg.draw.rect(
                surface=self.game_object.get_component(SurfaceComponent).pg_surf, 
                color=self.game_object.get_component(ColorComponent).color, 
                rect=((((Vector2d.from_tuple(self.game_object.get_component(SurfaceComponent).pg_surf.get_size()) - self.size) / 2)).as_tuple() + self.size.as_tuple()),
                width=self.width
            )

    def __str__(self):
        return f"RectBorderComponent: {self.size}"