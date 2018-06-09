import math
import itertools
import ctypes
import random
import cProfile, pstats

import pyglet

from constants import *
from gl_utilities import *

class App(pyglet.window.Window):
    tps = 120
    bg_color = (1, 0.86, 0.36, 1)
    grid_side = 8
    grid_block = 80
    grid_pos = ((SCREEN_WIDTH  - grid_side*grid_block) // 2,
                (SCREEN_HEIGHT - grid_side*grid_block) // 2)
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Toggle grid")
        self.mouse_pos = (0, 0)
        self.ticks = 0
        self.label = pyglet.text.Label("0", anchor_x="left", anchor_y="baseline")
        self.label.y = HEIGHT - self.label.content_height + 4
        self.fps_values, self.fps_update_delay = [], 0
        self.array = [[0 for _ in range(self.grid_side)]
                      for _ in range(self.grid_side)]
        self.colorarray = [[(0, 0, 0) for _ in range(self.grid_side)]
                           for _ in range(self.grid_side)]
        pyglet.clock.schedule_interval(self.update, 1 / self.tps)

        # Chessboard knight
        self.colorcycle = itertools.cycle(((1, 0, 0), (0, 0, 1)))
        #self.next_square(0, 0)
        self.ended = True
        self.last = self.last_color = None

    @property
    def possible_moves(self):
        if self.last is not None:
            x, y = self.last
            possible_moves = [
                (x, y) for x, y in
                    [(x + 1, y + 2), (x + 2, y + 1), 
                     (x + 2, y - 1), (x + 1, y - 2),
                     (x - 1, y - 2), (x - 2, y - 1),
                     (x - 2, y + 1), (x - 1, y + 2)]
                if x in range(self.grid_side) and 
                   y in range(self.grid_side) and 
                   self.array[y][x] == 0
            ]
        else:
            possible_moves = []
        return possible_moves

    def on_draw(self):        
        glClearColor(*self.bg_color)
        glClear(GL_COLOR_BUFFER_BIT)
        possible_moves = self.possible_moves
        for y in range(self.grid_side):
            for x in range(self.grid_side):
                ax = self.grid_pos[0]+x*self.grid_block
                ay = self.grid_pos[1]+y*self.grid_block
                a = self.array[y][x]
                c = self.colorarray[y][x]
                if a:
                    glColor3f(a*c[0], a*c[1], a*c[2])
                elif (x, y) in possible_moves:
                    glColor3f(1, 0.98, 0.55)
                else:
                    glColor3f(1, 1, 1)
                with glQuadContext(ax, ay) as quad:
                    quad.Vertex2(0, 0)
                    quad.Vertex2(self.grid_block, 0)
                    quad.Vertex2(self.grid_block, self.grid_block)
                    quad.Vertex2(0, self.grid_block)
        glColor3f(0.14, 0.14, 0.14)
        with glLinesContext(*self.grid_pos) as lines:
            for x in range(self.grid_side + 1):
                lines.Vertex2(x*self.grid_block, 0)
                lines.Vertex2(x*self.grid_block, self.grid_side*self.grid_block)
            for y in range(self.grid_side + 1):
                lines.Vertex2(0, y*self.grid_block)
                lines.Vertex2(self.grid_side*self.grid_block, y*self.grid_block)
        self.label.draw()

    def update(self, delta):
        self.ticks += 1
        self.fps_values.append(round(pyglet.clock.get_fps(), 1))
        if len(self.fps_values) > 5:
            self.fps_values.pop(0)
        avg = sum(self.fps_values) / len(self.fps_values)
        if self.fps_update_delay == 0:
            self.label.text = f"{round(avg, 1)}"
            self.fps_update_delay = 20
        else:
            self.fps_update_delay -= 1  
        if not self.ended:
            if self.possible_moves:
                self.next_square(*random.choice(self.possible_moves))
            else:
                self.ended = True
                print(self.last_color)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            if self.grid_pos[0] <= x and self.grid_pos[1] <= y:
                ix = (x - self.grid_pos[0]) // self.grid_block
                iy = (y - self.grid_pos[1]) // self.grid_block
                if ix < self.grid_side and iy < self.grid_side:
                    self.next_square(ix, iy)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, buttons, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()

    def next_square(self, x, y):
        self.array[y][x] ^= 1
        self.colorarray[y][x] = next(self.colorcycle)
        self.last = (x, y)
        self.last_color = self.colorarray[y][x]

if __name__ == "__main__":
    app = App()
    pyglet.app.run()
