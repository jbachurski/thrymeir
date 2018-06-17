import logging

import pyglet

import creature
import debug_draw
import entity
import level


__all__ = ['Room']


logger = logging.getLogger(__name__)


class Room:
    def __init__(self, parent: 'level.Level'):
        self.level = parent

        self.walls = set()
        self.half_walls = set()

        self.to_update = set()
        self.to_draw = set()

        self.to_keep = set()  # If entity isn't in any other set, it is here to hide from garbage collector.

        # TODO: This, along with all other things, will be loaded from Tiled map file.
        self.player = creature.Player(self, 100, 100, 16, 32,
                                      pyglet.image.TextureRegion(0, 0, 0, 16, 32, self.level.app.entities_image))
        self.walls.add(entity.Entity(self, 0, 0, 256, 16))
        self.walls.add(entity.Entity(self, 0, 0, 16, 256))
        self.walls.add(entity.Entity(self, 256 - 16, 0, 16, 256))
        self.walls.add(entity.Entity(self, 0, 256 - 16, 256, 16))
        self.walls.add(entity.Entity(self, 50, 50, 40, 30))

    def update(self):
        for e in self.to_update:
            e.update()

    def draw(self):
        for wall in self.walls:
            debug_draw.draw_entity(wall)

        # TODO: This will be replaced by state-of-the art insertion-sorted dynamic batch for optimal performance.
        entities = list(self.to_draw)
        entities.sort(key=lambda e: e.y)

        for e in entities:
            e.texture_region.blit(int(e.x), int(e.y))
