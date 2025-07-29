from .game_object import GameObject, Component
from typing import Callable, Any
import pygame as pg


class KeyBindComponent(Component):
    cmd: Callable[[GameObject, tuple[int]], None]
    listen: list[int]
    listen_for_hold: bool
    on_press: bool
    previous: list[int]
    args: list[Any]
    active: bool


    def __init__(self, listen: tuple[int], listen_for_hold: bool, on_press: bool,  cmd: Callable[[GameObject, tuple[int], list[Any]], None], *args: list[Any], active: bool = True):
        self.listen = tuple(listen)
        self.listen_for_hold = listen_for_hold
        self.on_press = on_press
        self.cmd = cmd
        self.active = active
        self.args = args
        self.previous = []
    
    def iteration(self):
        if not self.active:
            return
        keys = pg.key.get_pressed()
        listen_keys = []
        for i in self.listen:
            if keys[i]: listen_keys.append(i)
        active_keys = []
        if not self.listen_for_hold:
            for i in self.listen:
                if (self.on_press == (i in listen_keys) == (not (i in self.previous))):
                    active_keys.append(i)
            self.previous = listen_keys.copy()
        else:
            active_keys = listen_keys
        
        if len(active_keys) != 0:
            self.cmd(self.game_object, tuple(active_keys), *self.args)
        

