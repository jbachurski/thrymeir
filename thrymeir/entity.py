from typing import *

import pyglet

import room


class Entity:
    def __init__(self, parent: 'room.Room', x: float, y: float, w: float, h: float,
                 texture_region: Optional[pyglet.image.TextureRegion] = None):
        self.room = parent
        self.x, self.y, self.w, self.h = x, y, w, h
        self.texture_region = texture_region

        self.register()

    def register(self):
        if self.texture_region is not None:
            self.room.to_draw.add(self)
