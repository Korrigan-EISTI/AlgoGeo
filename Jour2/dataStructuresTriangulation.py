import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from convexHull import HullConvex
import dataStructuresPoly


class Triangle:
    def __init__(self, p1, p2, p3):
        self.points = [p1, p2, p3]
        self.neighbours = [-1, -1, -1]  # Indices des triangles voisins
    
    def fillIndexNeighbours(self, triangleEdgeP1P2, triangleEdgeP2P3, triangleEdgeP3P1):
        self.neighbours.clear()
        self.neighbours.extend([triangleEdgeP1P2, triangleEdgeP2P3, triangleEdgeP3P1])

    def orientation(self, p, q, r):
        val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())
        if val == 0:
            return 0 
        elif val > 0:
            return 1 
        else:
            return 2 

    def pointInsideTriangle(self, point):
        first_orientation = None
        for i in range(3):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % 3]
            
            o = self.orientation(p1, p2, point)
            
            if first_orientation is None:
                first_orientation = o
            elif o != 0 and o != first_orientation:
                return False
        
        return True
    
    def circumcenter(self):
        p1, p2, p3 = self.points

        Ax, Ay = p1.getX(), p1.getY()
        Bx, By = p2.getX(), p2.getY()
        Cx, Cy = p3.getX(), p3.getY()

        vectorAB = (Bx - Ax, By - Ay)
        vectorAC = (Cx - Ax, Cy - Ay)
        
        mediatriceAB = (-vectorAB[1], vectorAB[0])
        mediatriceAC = (-vectorAC[1], vectorAC[0])
        
        D = dataStructuresPoly.Point((Ax + Bx) / 2, (Ay + By) / 2)
        E = dataStructuresPoly.Point((Ax + Cx) / 2, (Ay + Cy) / 2)

        Dx, Dy = D.getX(), D.getY()
        medABx, medABy = mediatriceAB
        
        Ex, Ey = E.getX(), E.getY()
        medACx, medACy = mediatriceAC

        A = [
            [medABx, -medACx],
            [medABy, -medACy]
        ]
        b = [
            Ex - Dx,
            Ey - Dy
        ]
        
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]

        if det == 0:
            return None, None
        
        inv_det = 1 / det
        invA = [
            [A[1][1] * inv_det, -A[0][1] * inv_det],
            [-A[1][0] * inv_det, A[0][0] * inv_det]
        ]

        t1 = invA[0][0] * b[0] + invA[0][1] * b[1]
        t2 = invA[1][0] * b[0] + invA[1][1] * b[1]
       
        center_x = Dx + t1 * medABx
        center_y = Dy + t1 * medABy

        center = dataStructuresPoly.Point(center_x, center_y)

        radius = self.distance(p1, center)

        return center, radius
        
    def distance(self, point1, point2):
        return math.sqrt((point1.getX() - point2.getX())**2  + (point1.getY() - point2.getY())**2)
    
    def isPointInsideCircumcircle(self, point):
        center, radius = self.circumcenter()
        if center is None:
            # Le triangle est dégénéré (points colinéaires)
            return False

        distance = self.distance(center, point)
    
        # Inclure une marge de tolérance pour les calculs flottants
        epsilon = 1e-9
        return distance <= radius + epsilon


class Triangulation:
    def __init__(self):
        self.triangles = []
        self.hull = HullConvex()

    def findTriangleThatContainsPoint(self, point):
        for triangle in self.triangles:
            if triangle.pointInsideTriangle(point):
                return triangle
        return None


    def triangulateConvexHull(self):
        self.hull.graham()
        convex_hull_points = self.hull.points

        if len(self.hull.segments) < 3:
            print("Pas assez de points pour former une triangulation.")
            return
        
        reference_point = self.hull.segments[0].p1
        self.sortPointsByAngle(reference_point, convex_hull_points)
        
        for i in range(1, len(self.hull.segments) - 1):
            triangle = Triangle(reference_point, self.hull.segments[i].p1, self.hull.segments[i].p2)
            self.triangles.append(triangle)

        last_point = self.hull.segments[-1].p2
        closing_triangle = Triangle(reference_point, self.hull.segments[-1].p1, last_point)
        self.triangles.append(closing_triangle)

        self.updateNeighbours()
        self.insertConvexAllPoints(convex_hull_points)

    def insertConvexAllPoints(self, points):
        for point in points :
            self.insertPointIntoTriangulation(point)

    def insertPointIntoTriangulation(self, point, isDelaunay = False):
        triangle_containing_point = self.findTriangleThatContainsPoint(point)
        if not triangle_containing_point:
            print("Le point n'est pas dans la triangulation.")
            return

        self.triangles.remove(triangle_containing_point)

        p1, p2, p3 = triangle_containing_point.points

        new_triangle1 = Triangle(p1, p2, point)
        new_triangle2 = Triangle(p2, p3, point)
        new_triangle3 = Triangle(p3, p1, point)
        
        idx1 = len(self.triangles)
        idx2 = idx1 + 1
        idx3 = idx2 + 1
        
        neighbours = triangle_containing_point.neighbours
        
        new_triangle1.fillIndexNeighbours(neighbours[0], idx2, idx3)
        new_triangle2.fillIndexNeighbours(idx1, neighbours[1], idx3)
        new_triangle3.fillIndexNeighbours(idx1, idx2, neighbours[2])
        
        self.triangles.extend([new_triangle1, new_triangle2, new_triangle3])

        self.updateNeighbours()

        if (isDelaunay):
            self.delaunayCheck()

    def sortPointsByAngle(self, reference_point, points):
        def angle_from_reference(p):
            dx = p.getX() - reference_point.getX()
            dy = p.getY() - reference_point.getY()
            return math.atan2(dy, dx)
        
        return sorted(points, key=angle_from_reference)

    def insertPoints(self, internal_points):
        for point in internal_points:
            self.insertPointIntoTriangulation(point)

    def delaunayCheck(self):
        changed = True
        while changed:
            changed = False
            for triangle in self.triangles:
                if changed:
                    break

                for neighbour_index in triangle.neighbours:
                    if neighbour_index != -1 and neighbour_index < len(self.triangles):
                        neighbour_triangle = self.triangles[neighbour_index]
                        
                        external_point = None
                        for point in neighbour_triangle.points:
                            if point not in triangle.points:
                                external_point = point
                                break
                        
                        if external_point and triangle.isPointInsideCircumcircle(external_point):
                            print(f"Flip nécessaire entre {triangle} et {neighbour_triangle}")
                            if (self.flipEdge(triangle, neighbour_triangle) == None):
                                break
                            changed = True

    def flipEdge(self, triangle1, triangle2):
        p1, p2 = self.findCommonEdge(triangle1, triangle2)
        if not p1 or not p2:
            print("Les triangles ne partagent pas d'arête commune.")
            return None
       
        points1 = triangle1.points
        points2 = triangle2.points
        p3 = next(p for p in points1 if p != p1 and p != p2)
        p4 = next(p for p in points2 if p != p1 and p != p2)

        self.triangles.remove(triangle1)
        self.triangles.remove(triangle2)

        new_triangle1 = Triangle(p1, p3, p4)
        new_triangle2 = Triangle(p2, p3, p4)

        idx1 = len(self.triangles)
        idx2 = idx1 + 1

        neighbours1 = triangle1.neighbours
        neighbours2 = triangle2.neighbours

        new_triangle1.fillIndexNeighbours(
            self.findTriangleIndex(p1, p3),
            idx2,
            self.findTriangleIndex(p4, p1)
        )
        new_triangle2.fillIndexNeighbours(
            idx1,
            self.findTriangleIndex(p3, p4),
            self.findTriangleIndex(p4, p2)
        )

        for i, index in enumerate(neighbours1):
            if index != -1 and index < len(self.triangles):
                existing_triangle = self.triangles[index]
                if i == 0:
                    existing_triangle.neighbours[1] = idx2
                elif i == 1:
                    existing_triangle.neighbours[2] = idx1
                elif i == 2:
                    existing_triangle.neighbours[0] = idx1

        for i, index in enumerate(neighbours2):
            if index != -1 and index < len(self.triangles):
                existing_triangle = self.triangles[index]
                if i == 0:
                    existing_triangle.neighbours[1] = idx2
                elif i == 1:
                    existing_triangle.neighbours[2] = idx1
                elif i == 2:
                    existing_triangle.neighbours[0] = idx2

        self.triangles.extend([new_triangle1, new_triangle2])

        self.updateNeighbours()

    def findCommonEdge(self, t1, t2):
        points1 = set(t1.points)
        points2 = set(t2.points)
        common_points = points1.intersection(points2)
        if len(common_points) == 2:
            return tuple(common_points)
        return None, None

    def findTriangleIndex(self, p1, p2):
        for i, triangle in enumerate(self.triangles):
            if (p1 in triangle.points and p2 in triangle.points and
                (p1, p2) in [(triangle.points[0], triangle.points[1]),
                             (triangle.points[1], triangle.points[2]),
                             (triangle.points[2], triangle.points[0])]):
                return i
        return -1
    
    def updateNeighbours(self):
        edge_to_triangle = {}

        for i, triangle in enumerate(self.triangles):
            points = triangle.points
            for j in range(3):
                edge = tuple(sorted([points[j], points[(j + 1) % 3]]))
                if edge in edge_to_triangle:
                    edge_to_triangle[edge].append(i)
                else:
                    edge_to_triangle[edge] = [i]
     
        for i, triangle in enumerate(self.triangles):
            points = triangle.points
            neighbours = [-1, -1, -1]

            for j in range(3):
                edge = tuple(sorted([points[j], points[(j + 1) % 3]]))
                if edge in edge_to_triangle:
                    neighbour_indices = edge_to_triangle[edge]
                    for ni in neighbour_indices:
                        if ni != i:
                            neighbours[j] = ni
                            break
            
            triangle.fillIndexNeighbours(*neighbours)
        
    def slowDelaunay(self):
        self.triangulateConvexHull()
        self.delaunayCheck()

    def createSuperTriangle(self):
        points = self.hull.points
        min_x = min(p.getX() for p in points)
        max_x = max(p.getX() for p in points)
        min_y = min(p.getY() for p in points)
        max_y = max(p.getY() for p in points)

        # Calculer des points suffisamment grands pour contenir tous les autres points
        dx = max_x - min_x
        dy = max_y - min_y
        deltaMax = max(dx, dy)
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        # Créer un super-triangle
        p1 = dataStructuresPoly.Point(mid_x - 3 * deltaMax, mid_y - deltaMax)
        p2 = dataStructuresPoly.Point(mid_x, mid_y + deltaMax)
        p3 = dataStructuresPoly.Point(mid_x + 3 * deltaMax, mid_y - deltaMax)

        super_triangle = Triangle(p1, p2, p3)
        self.triangles.append(super_triangle)
        return super_triangle

    def delaunayIncremental(self):
        super_triangle = self.createSuperTriangle()
        for point in self.hull.points:
            self.insertPointIntoTriangulation(point)
        #self.removeSuperTriangle(super_triangle)

    def removeSuperTriangle(self, super_triangle):
        super_points = set(super_triangle.points)  # Points du super-triangle
        
        # Récupérer les triangles valides (ceux qui ne contiennent pas de points du super-triangle)
        valid_triangles = []
        
        for triangle in self.triangles:
            # Si le triangle n'a aucun sommet appartenant au super-triangle, il est valide
            if not any(p in super_points for p in triangle.points):
                valid_triangles.append(triangle)
        
        # Mettre à jour la liste des triangles pour ne garder que les triangles valides
        self.triangles = valid_triangles

        # Recalculer les voisins après suppression des triangles du super-triangle
        self.updateNeighbours()





