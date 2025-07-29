from .game_object import GameObject, Component, DEBUG
from .surface import SurfaceComponent
from .camera import Camera
from .transform import Transform
from .vmath_mini import Vector2d
import pygame as pg

pg.init()
pg.font.init()
pg.mixer.init()

class Engine:

    def __init__(self, window_size: Vector2d|tuple[int, int] = Vector2d(0, 0)):
        if not isinstance(window_size, Vector2d):
            window_size = Vector2d.from_tuple(window_size)
        GameObject.root.add_component(Transform(Vector2d(0, 0)))
        GameObject.root.add_component(SurfaceComponent(window_size))
        GameObject.root.get_component(SurfaceComponent).pg_surf = pg.display.set_mode(GameObject.root.get_component(SurfaceComponent).pg_surf.get_size())
        GameObject.root.add_child(Camera)

    def run(self, fps = 20):
        run = True
        clock = pg.time.Clock()

        self.first_iteration()
        self.forced_blit()

        while run:
            clock.tick(fps)
            for event in pg.event.get(eventtype=pg.QUIT):
                if event.type == pg.QUIT:
                    run = False

            self.iteration()
            pg.event.clear()

            self.draw()

            self.refresh()

            pg.display.flip()
            if DEBUG:
                print(f"fps = {clock.get_fps()}")

    def first_iteration(self):
        for g_obj in GameObject.objs:
            g_obj.first_iteration()

    def iteration(self):
        for g_obj in GameObject.objs:
            g_obj.iteration()
        
    def draw(self):
        window_size = GameObject.root.get_component(SurfaceComponent).size
        camera_pos = Camera.get_component(Transform).pos
        for g_obj in GameObject.objs:
            if not g_obj.active:
                continue
            if g_obj.need_draw:
                g_obj.need_draw = True
                g_obj.get_component(SurfaceComponent).pg_surf.fill((0, 0, 0, 0))
                for other_oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                    other_oncomer.need_blit = True
                pass
            else:
                for oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                    if oncomer.need_blit:
                        dist = (window_size + oncomer.get_component(SurfaceComponent).size)
                        if (oncomer.get_component(Transform).abs_pos - camera_pos + dist / 2).is_in_box(Vector2d(0, 0), dist):
                            g_obj.get_component(SurfaceComponent).pg_surf.fill((0, 0, 0, 0))
                            g_obj.need_draw = True
                            for other_oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                                other_oncomer.need_blit = True
                            break

        for g_obj in GameObject.objs:
            if g_obj.active:
                g_obj.draw()
                g_obj.need_draw = False

        def blit(g_obj: GameObject) -> bool:
            def check(g_obj: GameObject):
                if not g_obj.active:
                    return False
                if g_obj.need_blit:
                    return True
                for oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                    if check(oncomer):
                        return True
                return False
            for oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                if not check(oncomer):
                    continue
                dist = (window_size + oncomer.get_component(SurfaceComponent).size)
                if (oncomer.get_component(Transform).abs_pos - camera_pos + dist / 2).is_in_box(Vector2d(0, 0), dist):
                    if blit(oncomer):
                        g_obj.need_blit = True

            if not (g_obj in GameObject.get_group_by_tag("Camera")):
                if g_obj.need_blit and g_obj.active:
                    g_obj.get_component(SurfaceComponent).blit()
                    g_obj.need_blit = False
                    return True
            return False

        blit(GameObject.root)
        Camera.get_component(SurfaceComponent).blit()
        Camera.need_blit = False
    
    def forced_blit(self):
        self.iteration()
        for g_obj in GameObject.objs:
            g_obj.draw()
            g_obj.need_draw = False
            g_obj.need_blit = False
        def blit(g_obj: GameObject):
            for oncomer in g_obj.get_component(SurfaceComponent).oncoming:
                blit(oncomer)
            if not (g_obj in GameObject.get_group_by_tag("Camera")):
                g_obj.get_component(SurfaceComponent).blit()
        blit(GameObject.root)
        Camera.need_blit = False
        self.refresh()
    
    def refresh(self):
        for cls in Component.component_classes:
            cls.refresh()

    @staticmethod
    def set_debug(value: bool):
        global DEBUG
        DEBUG = value