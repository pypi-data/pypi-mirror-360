from .game_object import Component
from .label import LabelComponent
import pygame as pg

pg.key.start_text_input()

class EntryComponent(LabelComponent):
    active: bool

    def __init__(self, default_text: str = "", font = None, active: bool = False):
        LabelComponent.__init__(self, default_text, font)
        self.active = active
    
    def iteration(self):
        if self.active:
            need_update = False
            for event in pg.event.get(eventtype=pg.TEXTINPUT, pump=False):
                self.text += event.text
                need_update = True
            for event in pg.event.get(eventtype=pg.KEYDOWN, pump=False):
                if event.key == pg.K_BACKSPACE:
                    if len(self.text) > 0:
                        self.text = self.text[:-1]
                        need_update = True
            if need_update:
                self.game_object.need_blit_set_true()
                self.game_object.need_draw = True

    def clear(self):
        self.text = ""
        self.game_object.need_draw = True
        self.game_object.need_blit_set_true()