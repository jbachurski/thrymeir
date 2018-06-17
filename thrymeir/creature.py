import pyglet

import entity
import room

SQRT2 = 2 ** 0.5


class Creature(entity.Entity):
    def __init__(self, parent: 'room.Room', x: float, y: float, w: float, h: float,
                 texture_region: pyglet.image.TextureRegion):
        super().__init__(parent, x, y, w, h, texture_region)

        self.walking_speed = 10.0

        self.walking_n = self.walking_e = self.walking_s = self.walking_w = False

        self.room.to_update.add(self)

    def update(self):
        move_x = (0, 1)[self.walking_e] + (0, -1)[self.walking_w]
        move_y = (0, 1)[self.walking_n] + (0, -1)[self.walking_s]

        # Walking diagonally.
        if move_x and move_y:
            move_x = move_x / abs(move_x) / SQRT2
            move_y = move_y / abs(move_y) / SQRT2

        self.x += move_x * self.walking_speed
        self.y += move_y * self.walking_speed


class Player(Creature):
    def update(self):
        keys = self.room.level.app.key_state  # Whether ‘tis nobler in the mind to suffer...?

        # TODO: This will be separated into some kind of input component.
        self.walking_n = keys[pyglet.window.key.UP]
        self.walking_e = keys[pyglet.window.key.RIGHT]
        self.walking_s = keys[pyglet.window.key.DOWN]
        self.walking_w = keys[pyglet.window.key.LEFT]

        super().update()
