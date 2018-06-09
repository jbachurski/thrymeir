import pyglet
import os
from enum import Enum

class Tile:
    overdraw = False
    def __init__(self, col, row, metadata={}):
        self.col, self.row = col, row
        self.metadata = metadata
        self.image = pyglet.resource.image('missing_tile.png')