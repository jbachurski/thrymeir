import logging

import pyglet

import creature
import level


__all__ = ['Room']


logger = logging.getLogger(__name__)


class Room:
    def __init__(self, parent: 'level.Level'):
        self.level = parent

        self.to_update = set()
        self.to_draw = set()

        # TODO: This, along with all other things, will be loaded from Tiled map file.
        self.player = creature.Player(self, 10, 10, 16, 32,
                                      pyglet.image.TextureRegion(0, 0, 0, 16, 32, self.level.app.entities_image))

    def update(self):
        for entity in self.to_update:
            entity.update()

    def draw(self):

        # TODO: This will be replaced by state-of-the art insertion-sorted dynamic batch for optimal performance.
        entities = list(self.to_draw)
        entities.sort(key=lambda e: e.y)

        for entity in entities:
            entity.texture_region.blit(int(entity.x), int(entity.y))
