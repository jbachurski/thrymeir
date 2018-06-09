import math
import itertools

import numba
from numba import jit, float64
from pyglet.gl import * # pylint: disable=W0614

from gl_utilities import (
    glTriangleFanContext, glTrianglesContext,
    glLinesContext, draw_polygon
)

@jit(nopython=True, cache=True)
def in_interval(n, a, b, prec=5e-4):
    if b < a:
        a, b = b, a
    return a <= n <= b or close_equal(a, n, prec) or close_equal(b, n, prec)

@jit(nopython=True, cache=True)
def close_equal(x, y, prec=5e-4):
    return 0 <= abs(x - y) <= prec

@jit(nopython=True, cache=True)
def sign(x):
    return -1 if x < 0 else 1

@jit(float64(float64, float64), nopython=True, cache=True)
def hypot(x, y):
    return math.hypot(x, y)

@jit(cache=True)
def vector_angle(vector):
    return math.atan2(vector[1], vector[0])

@jit(numba.typeof((1.0, 1.0))(float64, float64), nopython=True, cache=True)
def vector_at_angle(angle, length):
    return (math.cos(angle) * length, math.sin(angle) * length)

@jit(cache=True)
def transformed_vector(vector, dangle, dlength):
    return vector_at_angle(vector_angle(vector) + dangle, hypot(*vector) + dlength)

@jit(cache=True)
def get_intersection(v, e):
    # Intersection of vector v and edge e. v starts in (0, 0).
    a, c = v[1] / v[0], 0
    if close_equal(e[0][0], e[1][0]):
        ix = e[0][0]
        iy = a*ix
        if in_interval(iy, e[0][1], e[1][1]) and sign(ix) == sign(v[0]):
            return (float(ix), float(iy))
        else:
            return None
    else:
        b = (e[0][1] - e[1][1]) / (e[0][0] - e[1][0])
        d = e[0][1] - b * e[0][0]
        if a == c:
            return None
        else:
            ix = (d - c) / (a - b)
            iy = (a*d - b*c) / (a - b)
            if in_interval(ix, e[0][0], e[1][0]) and \
                in_interval(ix, v[0], 0) and sign(ix) == sign(v[0]) and \
                in_interval(iy, e[0][1], e[1][1]) and \
                in_interval(iy, v[1], 0):
                return (float(ix), float(iy))

def raycast_preprocessing(mx, my, quality_passes, vertex_cast_multiplies, fallback_passes, 
                          radius, vertices, edges):
    vertices_p = []
    if (len(vertices) * vertex_cast_multiplies * 2) + quality_passes <= float("inf"):
        for i, v in enumerate(vertices):
            t = (float(v[0] - mx), float(v[1] - my))
            u = vector_angle(t)
            for i in range(-vertex_cast_multiplies, vertex_cast_multiplies+1):
                vertices_p.append(vector_at_angle(u+i*0.015, radius))
        for i in range(quality_passes+1):
            a = (i/quality_passes) * math.tau
            vertices_p.append(vector_at_angle(a, radius))
    else:
        for i in range(fallback_passes+1):
            a = (i/fallback_passes) * math.tau
            vertices_p.append(vector_at_angle(a, radius))
    vertices_p.sort(key=vector_angle)
    edges_p = [sorted([(e[0][0]-mx, e[0][1]-my), 
                       (e[1][0]-mx, e[1][1]-my)], 
                      key=vector_angle) 
               for e in edges]
    return vertices_p, edges_p

def get_light_raycasts(mx, my, quality_passes, vertex_cast_multiplies, fallback_passes, 
                       radius, vertices, edges, auto_preprocessing=True,
                       collect_all_raycasts=False):
    if auto_preprocessing:
        vertices, edges = raycast_preprocessing(
            mx, my, quality_passes, vertex_cast_multiplies, fallback_passes,
            radius, vertices, edges
        )
    raycasts = []
    all_raycasts = []
    active_edges = {
        i for i in range(len(edges)) 
        if vector_angle(edges[i][0]) <= -math.pi/2 and
           vector_angle(edges[i][1]) >= math.pi/2
    }
    to_dereverse = list(active_edges)
    for i in active_edges:
        edges[i].reverse()
    edge_begins = sorted(
        [i for i in range(len(edges))], 
        key=lambda i: vector_angle(edges[i][0])
    )
    edge_ends = sorted(
        [i for i in range(len(edges))], 
        key=lambda i: vector_angle(edges[i][1])
    )
    i, j = 0, 0
    for v in vertices:
        if v[0] == 0:
            v = (1.0, v[1])
        if v[1] == 0:
            v = (v[0], 1.0)
        u = vector_angle(v)
        while i < len(edge_begins) and vector_angle(edges[edge_begins[i]][0]) <= u:
            active_edges.add(edge_begins[i])
            i += 1
        raypoint = v
        raypoint_dist = radius
        for ei in active_edges:
            e = edges[ei]
            ip = get_intersection(v, e)
            if ip is not None:
                ix, iy = ip
                q = math.hypot(ix, iy)
                if q <= radius:
                    if collect_all_raycasts:
                        all_raycasts.append(ip)
                    if q < raypoint_dist:
                        raypoint = ip
                        raypoint_dist = math.hypot(*raypoint)
        while j < len(edge_ends) and vector_angle(edges[edge_ends[j]][1]) <= u:
            active_edges.discard(edge_ends[j])
            j += 1
        raycasts.append(raypoint)
    raycasts.sort(key=vector_angle)
    for i in to_dereverse:
        edges[i].reverse()
    return raycasts, all_raycasts
