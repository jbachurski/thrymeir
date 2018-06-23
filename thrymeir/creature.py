import pyglet

import entity
import rectangular_logic
import room

SQRT2 = 2 ** 0.5
INV_SQRT2 = 1 / SQRT2
def sign(x): return -1 if x < 0 else 1

class Creature(entity.Entity):
    def __init__(self, parent: 'room.Room', x: float, y: float, w: float, h: float,
                 texture_region: pyglet.image.TextureRegion):
        super().__init__(parent, x, y, w, h, texture_region)

        self.walking_speed = 10.0

        self.walking_n = self.walking_e = self.walking_s = self.walking_w = False

    def register(self):
        super().register()
        self.room.to_update.add(self)

    def update(self):
        self.handle_movement()
    
    def handle_movement(self):
        move_x = (0, 1)[self.walking_e] + (0, -1)[self.walking_w]
        move_y = (0, 1)[self.walking_n] + (0, -1)[self.walking_s]

        # Walking diagonally.
        if move_x and move_y:
            move_x = sign(move_x) * INV_SQRT2
            move_y = sign(move_y) * INV_SQRT2

        if move_x:
            self.x += move_x * self.walking_speed

            for wall in self.room.walls:
                if not rectangular_logic.is_collision(self.x, self.y, self.w, self.h, wall.x, wall.y, wall.w, wall.h):
                    continue
                if move_x > 0:
                    self.x = wall.x - self.w
                elif move_x < 0:
                    self.x = wall.x + wall.w
                break

        if move_y:
            self.y += move_y * self.walking_speed

            for wall in self.room.walls:
                if not rectangular_logic.is_collision(self.x, self.y, self.w, self.h, wall.x, wall.y, wall.w, wall.h):
                    continue
                if move_y > 0:
                    self.y = wall.y - self.h
                elif move_y < 0:
                    self.y = wall.y + wall.h


class Player(Creature):
    def handle_movement(self):
        keys = self.room.level.app.key_state  # Whether ‘tis nobler in the mind to suffer...?

        # TODO: This will be separated into some kind of input component.
        self.walking_n = keys[pyglet.window.key.UP]
        self.walking_e = keys[pyglet.window.key.RIGHT]
        self.walking_s = keys[pyglet.window.key.DOWN]
        self.walking_w = keys[pyglet.window.key.LEFT]

        super().handle_movement()
