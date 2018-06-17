import logging

import pyglet

import room
import states
import app

logger = logging.getLogger(__name__)


class Level(states.State):
    def __init__(self, parent: app.App):
        self.app = parent

        # TODO: there will be many, dynamically loaded rooms.
        self.test_room = room.Room(self)

        logger.info(f"New level created: {self}")

    def update(self):
        self.test_room.update()

    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_LINES, ('v2i', (0, 0, 256, 256, 0, 256, 256, 0)))
        self.test_room.draw()
