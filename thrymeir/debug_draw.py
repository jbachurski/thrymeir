import pyglet


def draw_cross(x, y, w, h):
    x, y, w, h = map(int, (x, y, w, h))
    pyglet.graphics.draw(12, pyglet.gl.GL_LINES, ('v2i', (x, y, x + w, y + h,
                                                         x + w, y, x, y + h,
                                                         x, y, x + w, y,
                                                         x + w, y, x + w, y + h,
                                                         x + w, y + h, x, y + h,
                                                         x, y + h, x, y)))


def draw_entity(e):
    draw_cross(e.x, e.y, e.w, e.h)
