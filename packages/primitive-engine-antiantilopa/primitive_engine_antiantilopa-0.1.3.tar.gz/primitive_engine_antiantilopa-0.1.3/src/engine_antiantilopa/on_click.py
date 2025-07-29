from .game_object import Component, GameObject
from .vmath_mini import Vector2d
import pygame as pg
from .shape import ShapeComponent
from .transform import Transform
from typing import Callable, Any

class OnClickComponent(Component):
    cmd: Callable[[GameObject, tuple[bool, bool, bool], Vector2d, list[Any]], None]
    listen: tuple[bool, bool, bool]
    listen_for_hold: bool
    on_press: bool
    previous: tuple[bool, bool, bool]
    args: list[Any]
    active: bool

    def __init__(self, listen: tuple[bool, bool, bool], listen_for_hold: bool, on_press: bool, cmd: Callable[[GameObject, tuple[bool, bool, bool], Vector2d, list[Any]], None], *args: list[Any], active: bool = True):
        self.cmd = cmd
        self.listen = listen
        self.listen_for_hold = listen_for_hold
        self.on_press = on_press
        self.args = args
        self.active = active
        self.previous = (False, False, False)

    def iteration(self):
        if not self.active:
            return
        mouse = pg.mouse.get_pressed()
        tmp = list(pg.mouse.get_pressed())
        if not self.listen_for_hold:
            for i in (0, 1, 2):
                tmp[i] = (self.on_press == tmp[i] == (not self.previous[i]))

            self.previous = mouse

        for i in (0, 1, 2):
            tmp[i] = tmp[i] and self.listen[i]

        if not(tmp[0] or tmp[1] or tmp[2]):
            return None


        m_pos = Vector2d(*pg.mouse.get_pos())
        
        m_pos = self.get_relative_coord(m_pos) + GameObject.get_group_by_tag("Camera")[0].get_component(Transform).pos

        if self.game_object.get_component(ShapeComponent).does_collide(m_pos):
            self.cmd(self.game_object, tmp, m_pos, *self.args)

    def get_relative_coord(self, pos: Vector2d) -> Vector2d:
        pos -= Vector2d.from_tuple(pg.display.get_window_size()) / 2
        g_obj = self.game_object
        while not (g_obj.parent is None):
            pos -= g_obj.parent.get_component(Transform).pos
            g_obj = g_obj.parent
        return pos