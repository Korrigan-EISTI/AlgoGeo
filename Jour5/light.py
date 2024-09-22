import math
import dataStructure3D

class Light:
    def __init__(self, vec, intensity):
        self.position = vec
        self.intensity = intensity

    def calculate_normal(self, v1, v2, v3):
        edge1 = v2.sub(v1)
        edge2 = v3.sub(v1)

        normal = edge1.crossProduct(edge2).normalize()

        return normal
    
    def compute_diffuse_light(self, normal, point):
        light_dir = self.position.sub(point).normalize()
        diffuse = max(normal.dotProduct(light_dir), 0.0) * self.intensity
        
        return diffuse