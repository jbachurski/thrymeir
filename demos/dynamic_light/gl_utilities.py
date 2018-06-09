import math

from pyglet.gl import * # pylint: disable=W0614

def glContextFactory(state):
    class GlContext:
        def __init__(self, mx=0, my=0, *, enclose=False):
            self.mx, self.my = mx, my
            self.vertices = 0
            self.initial, self.closing = None, None
            self.enclose = enclose

        def __enter__(self, *args):
            glBegin(state)
            return self

        def Vertex2(self, x, y):
            x += self.mx; y += self.my
            glVertex2f(x, y)
            self.vertices += 1
            if self.vertices == 1:
                self.initial = (x, y)
            elif self.vertices == 2:
                self.closing = (x, y)

        def __exit__(self, *args):
            if self.enclose and self.closing is not None and \
               state == GL_TRIANGLE_FAN:
                glVertex2f(*self.closing)
            glEnd()
    return GlContext

glTriangleFanContext = glContextFactory(GL_TRIANGLE_FAN)
glTrianglesContext = glContextFactory(GL_TRIANGLES)
glLinesContext = glContextFactory(GL_LINES)
glQuadContext = glContextFactory(GL_QUADS)

def draw_polygon(x, y, r, p, c):
    with glTriangleFanContext(x, y, enclose=True) as fan:
        glColor4f(*c)
        for i in range(p):
            a = (i/p) * math.tau
            fan.Vertex2(math.cos(a)*r, math.sin(a)*r)