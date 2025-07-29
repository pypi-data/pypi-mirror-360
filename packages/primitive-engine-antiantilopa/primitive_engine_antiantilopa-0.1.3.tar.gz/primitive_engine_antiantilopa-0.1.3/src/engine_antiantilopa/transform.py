from .game_object import Component
from .vmath_mini import Vector2d, Angle

class Transform(Component):
    objs: list["Transform"] = []
    pos: Vector2d
    abs_pos: Vector2d
    rotation: Angle
    changed: bool

    def __init__(self, pos: Vector2d = Vector2d(0, 0), rotation: Angle|float = 0) -> None:
        Transform.objs.append(self)
        self.pos = pos
        self.abs_pos = Vector2d(0, 0)
        self.changed = False
        if not isinstance(rotation, Angle):
            self.rotation = Angle(rotation)
        else:
            self.rotation = rotation

    def first_iteration(self):
        g_obj = self.game_object
        while g_obj.parent is not None:
            self.abs_pos += g_obj.get_component(Transform).pos
            g_obj = g_obj.parent

    def move(self, delta: Vector2d):
        self.pos += delta
        self.game_object.need_blit_set_true()
        self.changed = True
        self.update_abs_pos(self.game_object.parent.get_component(Transform).abs_pos if self.game_object.parent else Vector2d(0, 0))
    
    def rotate(self, delta: Angle):
        self.rotation += delta
        self.game_object.need_blit_set_true()
        self.changed = True

    def set_pos(self, pos: Vector2d):
        self.pos = pos
        self.game_object.need_blit_set_true()
        self.changed = True
        self.update_abs_pos(self.game_object.parent.get_component(Transform).abs_pos if self.game_object.parent else Vector2d(0, 0))

    
    def set_rotation(self, rotation: Angle):
        self.rotation = rotation
        self.game_object.need_blit_set_true()
        self.changed = True

    def update_abs_pos(self, abs_pos: Vector2d):
        self.abs_pos = abs_pos + self.pos
        for child in self.game_object.childs:
            child.get_component(Transform).update_abs_pos(self.abs_pos)

    @staticmethod
    def refresh():
        for obj in Transform.objs:
            obj.changed = False

    def __str__(self):
        return f"Transform: {self.pos}, {self.rotation}"
    
    def destroy(self):
        Component.destroy(self)
        Transform.objs.remove(self)