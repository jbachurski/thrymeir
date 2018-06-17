import contextlib

import pyglet
from pyglet import gl

__all__ = ['LetterboxViewport']


class LetterboxViewport:
    # Some GL-specific code is commented out.
    # This means that for now everything works without it, but it may be needed if something breaks.

    def __init__(self, window: pyglet.window.Window, scene_width: int, scene_height: int, smooth_scaling: bool = False):
        self.window = window
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.texture = pyglet.image.Texture.create(scene_width, scene_height,
                                                   rectangle=scene_width != scene_height)

        if not smooth_scaling:
            # Disable smooth scaling
            gl.glTexParameteri(self.texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(self.texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

        # glClearColor(0, 0, 0, 1)
        # glMatrixMode(GL_PROJECTION)

        self.texture_x = self.texture_y = self.scale_width = self.scale_height = 0

        @window.event
        def on_resize(w, h):
            self.on_window_resize()
        self.on_window_resize()

    def begin_drawing(self) -> None:
        gl.glViewport(0, 0, self.scene_width, self.scene_height)
        self.set_fixed_projection()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def end_drawing(self) -> None:
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)

        gl.glViewport(0, 0, self.window.width, self.window.height)
        self.set_window_projection()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # glColor3f(1, 1, 1)

        self.texture.blit(self.texture_x, self.texture_y, width=self.scale_width, height=self.scale_height)
        self.on_window_resize()

    @contextlib.contextmanager
    def draw(self):
        self.begin_drawing()
        yield
        self.end_drawing()

    def set_fixed_projection(self) -> None:
        # Override this method if you need to change the projection of the fixed resolution viewport.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.scene_width, 0, self.scene_height, -1, 1)
        # gl.glMatrixMode(gl.GL_MODELVIEW)

    def set_window_projection(self) -> None:
        # This is the same as the default window projection, reprinted here for clarity.
        # gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        # glMatrixMode(gl.GL_MODELVIEW)

    def on_window_resize(self) -> None:
        scale = min(self.window.width / self.scene_width, self.window.height / self.scene_height)
        self.scale_width = scale * self.scene_width
        self.scale_height = scale * self.scene_height

        self.texture_x = (self.window.width - self.scale_width) / 2
        self.texture_y = (self.window.height - self.scale_height) / 2
