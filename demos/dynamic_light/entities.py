import math

from numba import jit, void, float64
from pyglet.gl import * # pylint: disable=W0614

from constants import WIDTH, HEIGHT
from gl_utilities import (
    glTriangleFanContext, glTrianglesContext,
    glLinesContext, draw_polygon
)
import lighting

class LightSource:
    light_color = (1.0, 1.0, 0.0, 0.75)
    radius = math.hypot(WIDTH, HEIGHT) / 2 + 100.0
    #radius = 100.0
    strength_over = 0.0
    quality_passes = 30
    vertex_cast_multiplies = 2
    fallback_passes = 512
    draw_raycasts = 0
    draw_all_raycasts = 0
    draw_raycast_lines = 0
    rcp_delay = 900
    def __init__(self, x, y, light_color, vertices, edges, rects, auto_rcp=True):
        self.x, self.y = float(x), float(y)
        self.ticks = 0
        self.bg_color = (0, 0, 0, 0)
        self.light_color = light_color
        self.vertices = vertices
        self.edges = edges
        #RCP - RayCast Preprocessing
        self.raycasts, self.all_raycasts = [], []
        self.vertices_rcp, self.edges_rcp = lighting.raycast_preprocessing(**self.rpc_kwargs)
        self.rcp_update = self.rcp_delay
        self.force_rcp = True
        self.updated_rcp = True
        self.auto_rcp = auto_rcp

    def update(self, delta):
        self.ticks += 1
        if self.rcp_update > 0:
            self.rcp_update -= 1
    
    @property
    def rpc_kwargs(self):
        return dict(
            mx=self.x, my=self.y,
            quality_passes=self.quality_passes,
            vertex_cast_multiplies=self.vertex_cast_multiplies,
            fallback_passes = self.fallback_passes,
            radius=self.radius,
            vertices=self.vertices,
            edges=self.edges
        )

    @property
    def raycast_kwargs(self):
        return dict(
            mx=self.x, my=self.y,
            quality_passes=self.quality_passes,
            vertex_cast_multiplies=self.vertex_cast_multiplies,
            fallback_passes = self.fallback_passes,
            radius=self.radius,
            vertices=self.vertices if self.auto_rcp else self.vertices_rcp,
            edges=self.edges if self.auto_rcp else self.edges_rcp,
            auto_preprocessing=self.auto_rcp,
            collect_all_raycasts=False
        )

    @staticmethod    
    @jit(void(float64, float64, float64, float64, float64, float64, float64, float64))
    def set_light_color(x, y, c_strength, radius, r, g, b, a):
        d = math.hypot(x, y)
        s = min(1, 1 - (1 - c_strength) * d/radius)
        glColor4f(r, g, b, a * s)

    def draw(self):
        # Sinusoidal-wave based ligth strength
        #c_strength = 1 - (math.sin((self.ticks % 100) / 100 * math.tau) + 1)/2
        # Raycasts are calculated here to make sure they are updated
        # .draw() happens on every screen refresh and .update() every 1/60th of a second
        if (not self.auto_rcp and self.rcp_update <= 0) or self.force_rcp:
            self.vertices_rcp, self.edges_rcp = lighting.raycast_preprocessing(**self.rpc_kwargs)
            self.rcp_update = self.rcp_delay
            self.updated_rcp = True
            self.force_rcp = False
        if self.updated_rcp or self.auto_rcp:
            self.raycasts, self.all_raycasts = lighting.get_light_raycasts(**self.raycast_kwargs)  # pylint: disable=W0612
            self.update_rcp = False
        c_strength = self.strength_over 
        with glTriangleFanContext(self.x, self.y, enclose=True) as fan:
            glColor4f(*self.light_color)
            fan.Vertex2(0, 0)
            r, g, b, a = self.light_color
            for (x1, y1), (x2, y2) in zip(self.raycasts, self.raycasts[1:]):
                self.set_light_color(x1, y1, c_strength, self.radius, r, g, b, a)
                glVertex2f(self.x + x1, self.y + y1)
                self.set_light_color(x2, y2, c_strength, self.radius, r, g, b, a)
                glVertex2f(self.x + x2, self.y + y2)
            self.set_light_color(self.raycasts[0][0], self.raycasts[0][1], c_strength, self.radius, r, g, b, a)
            glVertex2f(self.x + self.raycasts[0][0], self.y + self.raycasts[0][1])

        if self.draw_all_raycasts:
            for px, py in self.all_raycasts:
                draw_polygon(px+self.x, py+self.y, 5, 10, (1, 0, 0, 0.5))
        if self.draw_raycasts:
            for px, py in self.raycasts:
                draw_polygon(px+self.x, py+self.y, 5, 10, (0, 1, 0, 1))
        if self.draw_raycast_lines:
            glColor4f(1, 0, 0, 1)
            with glLinesContext(self.x, self.y) as lines:
                for px, py in self.raycasts:
                    lines.Vertex2(0, 0)
                    lines.Vertex2(px, py)
    
    def delete(self):
        pass

class Box:
    color = (1, 1, 1, 1)
    def __init__(self, x, y, w, h, parent_vertices, parent_edges, parent_rects):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.edges = [[(0, 0), (0, 0)] for _ in range(4)]
        self.redo_edges()
        self.parent_edges = parent_edges
        self.parent_edges.extend(self.edges)
        self.vertices = [[0, 0] for _ in range(4)]
        self.redo_vertices()
        self.parent_vertices = parent_vertices
        self.parent_vertices.extend(self.vertices)
        self.rect = [self.vertices[0], self.vertices[3]]
        self.parent_rects = parent_rects
        self.parent_rects.append(self.rect)
        self.lx, self.ly, self.lw, self.lh = x, y, w, h

    def draw(self):
        glColor4f(*self.color)
        with glTrianglesContext(self.x, self.y) as tri:
            tri.Vertex2(0, 0)
            tri.Vertex2(self.w, 0)
            tri.Vertex2(self.w, self.h)
        with glTrianglesContext(self.x, self.y) as tri:
            tri.Vertex2(0, 0)
            tri.Vertex2(self.w, self.h)
            tri.Vertex2(0, self.h)

    def update(self, delta):
        if self.lx != self.x or self.ly != self.y or \
           self.lw != self.w or self.lh != self.h:
            self.redo_edges()
            self.redo_vertices()
            self.lx, self.ly, self.lw, self.lh = self.x, self.y, self.w, self.h

    def redo_edges(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.edges[0][0] = (x, y)
        self.edges[0][1] = (x+w, y)
        self.edges[1][0] = (x, y)
        self.edges[1][1] = (x, y+h)
        self.edges[2][0] = (x+w, y)
        self.edges[2][1] = (x+w, y+h)
        self.edges[3][0] = (x, y+h)
        self.edges[3][1] = (x+w, y+h)
    
    def redo_vertices(self):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.vertices[0][0] = x
        self.vertices[0][1] = y
        self.vertices[1][0] = x+w
        self.vertices[1][1] = y
        self.vertices[2][0] = x
        self.vertices[2][1] = y+h
        self.vertices[3][0] = x+w
        self.vertices[3][1] = y+h

    def delete(self):
        for e in self.edges:
            self.parent_edges.remove(e)
        for v in self.vertices:
            self.parent_vertices.remove(v)
        self.parent_rects.remove(self.rect)

class BoxSizeDrag:
    def __init__(self, parent, sx, sy):
        self.parent = parent
        self.sx, self.sy = sx, sy
    @property
    def x(self):
        return self.parent.w
    @property
    def y(self):
        return self.parent.h
    @x.setter
    def x(self, value):
        self.parent.w = max(value - self.sx, 8)
    @y.setter
    def y(self, value):
        self.parent.h = max(value - self.sy, 8)