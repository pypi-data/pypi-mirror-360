from .game_object import Component, GameObject, DEBUG
import pygame as pg
from .vmath_mini import Vector2d

from .transform import Transform

import bisect

class SurfaceComponent(Component):
    pg_surf: pg.Surface
    size: Vector2d
    crop: bool
    depth: int
    oncoming: list[GameObject]
    layer: int


    def __init__(self, size: Vector2d, crop:bool=True, layer: int = 0):
        self.size = size
        self.pg_surf = pg.Surface(size.as_tuple(), pg.SRCALPHA, 32)
        self.crop = crop
        self.depth = 1
        self.oncoming = []
        self.layer = layer
        if DEBUG:
            self.pg_surf.set_alpha(128)

    def first_iteration(self):
        if self.game_object.parent is None:
            return
        if self.crop:
            self.depth = 1
            self.game_object.parent.get_component(SurfaceComponent).add_oncoming(self.game_object)
        else:
            self.update_oncoming()

    def blit(self):
        if self.game_object == GameObject.root:
            return
        elif self.game_object.parent == GameObject.root:
            surf = self.game_object.parent.get_component(SurfaceComponent) 
            pos = self.game_object.get_component(Transform).pos - GameObject.get_group_by_tag("Camera")[0].get_component(Transform).pos
            pos += Vector2d.from_tuple(pg.display.get_surface().get_size())/2
        else:
            if self.crop:
                pos = self.game_object.get_component(Transform).pos + (self.game_object.parent.get_component(SurfaceComponent).size / 2)
                surf = self.game_object.parent.get_component(SurfaceComponent) 
            else:
                g_obj = self.game_object
                pos_changed = False
                for i in range(self.depth):
                    if g_obj.get_component(Transform).changed:
                        pos_changed = True
                        break
                    g_obj = g_obj.parent
                if pos_changed:
                    pos, surf = self.update_oncoming()
                else:
                    pos = Vector2d(0, 0)
                    g_obj = self.game_object
                    for i in range(self.depth):
                        pos += g_obj.get_component(Transform).pos
                        g_obj = g_obj.parent
                    pos += (g_obj.get_component(SurfaceComponent).size / 2)
                    surf = g_obj.get_component(SurfaceComponent)
        surf.pg_surf.blit(self.pg_surf, (pos - self.size / 2).as_tuple())

    def update_oncoming(self) -> tuple[Vector2d, "SurfaceComponent"]:
        g_obj = self.game_object.parent
        surf = self.game_object.parent.get_component(SurfaceComponent) 
        abs_coords = self.game_object.get_component(Transform).pos
        def is_box_in_box(center_abs_pos: Vector2d, size1: Vector2d, size2: Vector2d) -> bool:
            return (center_abs_pos - size1 / 2).is_in_box(size2 / -2, size2 / 2) and (center_abs_pos + size1 / 2).is_in_box(size2 / -2, size2 / 2)
        prev_g_obj = self.game_object
        for i in range(self.depth):
            prev_g_obj = prev_g_obj.parent
        self.depth = 1
        while g_obj != GameObject.root:
            if is_box_in_box(abs_coords, self.size, g_obj.get_component(SurfaceComponent).size):
                surf = g_obj.get_component(SurfaceComponent) 
                break
            abs_coords += g_obj.get_component(Transform).pos
            g_obj = g_obj.parent
            self.depth += 1

        prev_g_obj.get_component(SurfaceComponent).remove_oncoming(self.game_object)
        g_obj.get_component(SurfaceComponent).add_oncoming(self.game_object)
        pos = abs_coords + (g_obj.get_component(SurfaceComponent).size / 2)
        return pos, surf
    
    def add_oncoming(self, g_obj: GameObject):
        if g_obj not in self.oncoming:
            bisect.insort(self.oncoming, g_obj, key=lambda x: x.get_component(SurfaceComponent).depth - (1 / (x.get_component(SurfaceComponent).layer + 1)))

    def remove_oncoming(self, g_obj: GameObject):
        if g_obj in self.oncoming:
            self.oncoming.remove(g_obj)

    def destroy(self):
        g_obj = self.game_object
        for i in range(self.depth):
            g_obj = g_obj.parent 
        g_obj.get_component(SurfaceComponent).remove_oncoming(self.game_object)