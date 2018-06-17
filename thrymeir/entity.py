import pyglet

import room


class Entity:
    def __init__(self, parent: 'room.Room', x: float, y: float, w: float, h: float,
                 texture_region: pyglet.image.TextureRegion):
        self.room = parent
        self.x, self.y, self.w, self.h = x, y, w, h
        self.texture_region = texture_region

        self.room.to_draw.add(self)
