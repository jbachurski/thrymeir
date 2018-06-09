import logging

import pyglet

import states
import app

logger = logging.getLogger(__name__)


class Level(states.State):
    def __init__(self, parent: app.App):
        self.app = parent

        logger.info(f"New level created: {self}")

    def on_update(self):
        pass

    def on_draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_LINES, ('v2i', (0, 0, 256, 256, 0, 256, 256, 0)))
