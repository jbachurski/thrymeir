import math
import itertools
import contextlib
import ctypes
import cProfile, pstats

import pyglet
from pyglet.gl import * # pylint: disable=W0614

from constants import WIDTH, HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from letterbox import LetterboxViewport
from gl_utilities import (
    glTriangleFanContext, glTrianglesContext,
    glLinesContext, glQuadContext,
    draw_polygon
)
from entities import LightSource, Box, BoxSizeDrag

requires_letterbox = WIDTH != SCREEN_WIDTH or HEIGHT != SCREEN_HEIGHT

class AutoProfile:
    def __init__(self, name="nameless"):
        self.profiler = cProfile.Profile()
        self.name = name
    def start(self):
        self.profiler.enable()
    def stop(self, dump=False):
        self.profiler.disable()
        if dump:
            self.profiler.dump_stats(self.name + ".stats")
        stats = pstats.Stats(self.profiler)
        stats.strip_dirs(); stats.sort_stats("ncalls")
        stats.print_stats()

class App(pyglet.window.Window):
    tps = 60
    bg_color = (0.3, 0.3, 0.75, 1)
    bg_light_color = (0.75, 0.75, 1, 0)#.1)
    ls = 0.5
    colors = itertools.cycle(((1, 1, 1, ls), 
        (1, 1, 0, ls), (1, 0, 0, ls), 
        (0, 1, 0, ls), (0, 0, 1, ls)
    ))
    grid_gap = 20
    out_gap = 3
    def __init__(self, *, enable_letterbox=requires_letterbox):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Dynamic lighting demo")
        self.mouse_pos = (0, 0)
        self.ticks = 0
        self.profiler = None
        self.enable_letterbox = enable_letterbox
        self.label = pyglet.text.Label("0", anchor_x="left", anchor_y="baseline")
        self.label.y = HEIGHT - self.label.content_height + 4
        self.fps_values, self.fps_update_delay = [], 0
        
        self.light_sources = []
        self.boxes = []
        g = self.out_gap
        self.edges = [
            [(g, g), (WIDTH - g, g)],
            [(g, g), (g, HEIGHT - g)],
            [(WIDTH - g, g), (WIDTH - g, HEIGHT - g)],
            [(g, HEIGHT - g), (WIDTH - g, HEIGHT - g)]
        ]
        self.vertices = [
            [g, g], [WIDTH - g, g],
            [g, HEIGHT - g], [WIDTH - g, HEIGHT - g]
        ]
        self.rects = []
        self.add_light_source(WIDTH // 2, HEIGHT // 2)
        self.add_box(4*g, 2*g)
        self.dragging = None

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glClearColor(*self.bg_color)
        if self.enable_letterbox:
            self.letterbox = LetterboxViewport(self, WIDTH, HEIGHT)
        else:
            self.letterbox = None
        pyglet.clock.schedule_interval(self.update, 1 / self.tps)

    def on_draw(self):
        if self.enable_letterbox:
            with self.letterbox.draw():
                self._on_draw()
        else:
            self._on_draw()

    def _on_draw(self):        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(*self.bg_color)
        glClear(GL_COLOR_BUFFER_BIT)
        
        self.draw_grid()
        
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        glBindTexture(GL_TEXTURE_2D, light_texture)
        self.draw_light_to_texture()
        glBindTexture(GL_TEXTURE_2D, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        glBindTexture(GL_TEXTURE_2D, light_texture)
        self.render_light()
        glBindTexture(GL_TEXTURE_2D, 0)

        for d in self.boxes:
            d.draw()
        self.draw_drag_points()
        self.label.draw()

    def update(self, delta):
        self.ticks += 1
        self.fps_values.append(round(pyglet.clock.get_fps(), 1))
        if len(self.fps_values) > 5:
            self.fps_values.pop(0)
        avg = sum(self.fps_values) / len(self.fps_values)
        if self.fps_update_delay == 0:
            self.label.text = f"{round(avg, 1)} (ls: {len(self.light_sources)}, b: {len(self.boxes)})"
            self.fps_update_delay = 20
        else:
            self.fps_update_delay -= 1
        for d in self.light_sources:
            d.update(delta)
        for d in self.boxes:
            d.update(delta)
    
    def _translate_for_letterbox(self, x, y):
        return (x // (self.width // self.letterbox.scene_width), 
                y // (self.height // self.letterbox.scene_height))

    def handle_light_entity_change(self, d):
        if isinstance(d, LightSource):
            d.force_rcp = True
        elif isinstance(d, (Box, BoxSizeDrag)):
            for d in self.light_sources:
                d.force_rcp = True                

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.enable_letterbox:
            x, y = self._translate_for_letterbox(x, y)
        if buttons & pyglet.window.mouse.LEFT:
            for d in itertools.chain(self.light_sources, self.boxes):
                if math.hypot(d.x - x, d.y - y) <= 20:
                    self.dragging = d
                    break
                elif isinstance(d, Box) and \
                   math.hypot(d.x + d.w - x, d.y + d.h - y) <= 20:
                    self.dragging = BoxSizeDrag(d, x-d.w, y-d.h)
                    break
            else:
                return
            self.handle_light_entity_change(self.dragging)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.enable_letterbox:
            x, y = self._translate_for_letterbox(x, y)
        self.mouse_pos = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.enable_letterbox:
            x, y = self._translate_for_letterbox(x, y)
        if buttons & pyglet.window.mouse.LEFT and \
           self.dragging is not None:
            self.dragging.x = x
            self.dragging.y = y
            self.handle_light_entity_change(self.dragging)
            def on_screen(x, y): return 0 <= x <= WIDTH and 0 <= y <= HEIGHT
            if not on_screen(x, y) and \
               not isinstance(self.dragging, BoxSizeDrag) and \
               (not isinstance(self.dragging, Box) or not on_screen(x+self.dragging.w, y+self.dragging.h)):
                self.dragging.delete()
                if isinstance(self.dragging, LightSource):
                    self.light_sources.remove(self.dragging)
                elif isinstance(self.dragging, Box):
                    self.boxes.remove(self.dragging)
                self.dragging = None

    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.enable_letterbox:
            x, y = self._translate_for_letterbox(x, y)
        if buttons & pyglet.window.mouse.LEFT:
            self.handle_light_entity_change(self.dragging)
            self.dragging = None

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        elif symbol == pyglet.window.key.F3:
            self.add_light_source(*self.mouse_pos)
        elif symbol == pyglet.window.key.F4:
            self.add_box(*self.mouse_pos)
        elif symbol == pyglet.window.key.F7:
            if self.profiler is not None:
                self.profiler.stop()
            self.profiler = AutoProfile()
            self.profiler.start()
        elif symbol == pyglet.window.key.F8:
            if self.profiler is not None:
                self.profiler.stop()
                self.profiler = None
        if self.light_sources: 
            if symbol == pyglet.window.key.LEFT:
                self.light_sources[0].x -= 1
            elif symbol == pyglet.window.key.RIGHT:
                self.light_sources[0].x += 1
            elif symbol == pyglet.window.key.UP:
                self.light_sources[0].y += 1
            elif symbol == pyglet.window.key.DOWN:
                self.light_sources[0].y -= 1
            elif symbol == pyglet.window.key.F9:
                for d in self.light_sources:
                    d.auto_rcp = not d.auto_rcp
            else:
                return
            self.handle_light_entity_change(self.light_sources[0])

    def add_light_source(self, x, y):
        self.light_sources.append(
            LightSource(x, y, next(self.colors), self.vertices, self.edges, self.rects, False)
        )
        self.handle_light_entity_change(self.light_sources[-1])

    def add_box(self, x, y):
        self.boxes.append(Box(x, y, 100, 100, self.vertices, self.edges, self.rects))
        self.handle_light_entity_change(self.boxes[-1])

    def draw_grid(self):
        glLineWidth(1)
        glColor4f(1, 1, 1, 1)
        for x in range(self.grid_gap, WIDTH, self.grid_gap):
            with glLinesContext(x, 0) as lines:
                lines.Vertex2(0, 0)
                lines.Vertex2(0, HEIGHT)
        for y in range(self.grid_gap, HEIGHT, self.grid_gap):
            with glLinesContext(0, y) as lines:
                lines.Vertex2(0, 0)
                lines.Vertex2(WIDTH, 0)

    def draw_light_to_texture(self):
        glBindTexture(GL_TEXTURE_2D, light_texture)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        if self.bg_light_color[3] > 0:
            glColor4f(*self.bg_light_color)
            with glQuadContext(0, 0):
                glVertex2f(0, 0)
                glVertex2f(WIDTH, 0)
                glVertex2f(WIDTH, HEIGHT)
                glVertex2f(0, HEIGHT)
        for d in self.light_sources:
            d.draw()
    
    def render_light(self):
        glBindTexture(GL_TEXTURE_2D, light_texture)
        glEnable(GL_TEXTURE_2D)
        glBlendFunc(GL_DST_COLOR, GL_ZERO)

        glColor4f(1, 1, 1, 1)
        with glQuadContext(0, 0) as quad:
            glTexCoord2f(0, 0)
            quad.Vertex2(0, 0)
            glTexCoord2f(1, 0)
            quad.Vertex2(WIDTH, 0)
            glTexCoord2f(1, 1)
            quad.Vertex2(WIDTH, HEIGHT)
            glTexCoord2f(0, 1)
            quad.Vertex2(0, HEIGHT)

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

    def draw_drag_points(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for d in self.boxes:
            draw_polygon(d.x, d.y, 2, 6, (1, 0, 0, 1))
            draw_polygon(d.x+d.w, d.y+d.h, 2, 6, (1, 0, 0, 1))
        for d in self.light_sources:
            draw_polygon(d.x, d.y, 2, 6, (1, 0, 0, 1))  

if __name__ == "__main__":
    
    app = App()

    # Setup framebuffer
    fbo = GLuint()
    glGenFramebuffers(1, ctypes.byref(fbo))
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glEnable(GL_BLEND)

    # Setup light texture
    light_texture = GLuint()
    glGenTextures(1, ctypes.byref(light_texture))
    glBindTexture(GL_TEXTURE_2D, light_texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, WIDTH, HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, 0)
    glFramebufferTexture2D(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
        GL_TEXTURE_2D, light_texture, 0
    )

    assert glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE
    glBindFramebuffer(GL_FRAMEBUFFER, 0)    
    glBindTexture(GL_TEXTURE_2D, 0)

    pyglet.app.run()
    glDeleteFramebuffers(1, ctypes.byref(fbo))
