import dataStructure3D
import math

class Plane:
    def __init__(self, a, b, c, n):
        self.p1 = a
        self.p2 = b
        self.p3 = c
        self.normal = n
        normal = (b.sub(a)).crossProduct(c.sub(a)).normalize()
        self.d = -normal.dotProduct(a)

    def ray_intersects_plane(self, ray_origin, ray_direction):
        denom = self.normal.dotProduct(ray_direction)
        if abs(denom) > 1e-6:
            t = -(self.normal.dotProduct(ray_origin) + self.d) / denom
            if t >= 0:
                intersection_point = ray_origin.add(ray_direction.scale(t))
                return True, intersection_point
        return False, None
