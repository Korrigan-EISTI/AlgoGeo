import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from convexHull import HullConvex
import dataStructuresPoly
import time
import pygame


class Triangle:
    def __init__(self, p1, p2, p3):
        self.points = [p1, p2, p3]  # Stores the three points of the triangle
        self.neighbours = [-1, -1, -1]  # Indices of neighboring triangles
    
    # Fills in the neighbor indices for the triangle
    def fillIndexNeighbours(self, triangleEdgeP1P2, triangleEdgeP2P3, triangleEdgeP3P1):
        self.neighbours.clear()
        self.neighbours.extend([triangleEdgeP1P2, triangleEdgeP2P3, triangleEdgeP3P1])

    # Determines the orientation of the three points (collinear, clockwise, or counterclockwise)
    def orientation(self, p, q, r):
        val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())
        if val == 0:
            return 0  # Collinear
        elif val > 0:
            return 1  # Clockwise
        else:
            return 2  # Counterclockwise

    # Checks if a point is inside the triangle using orientation
    def pointInsideTriangle(self, point):
        p1, p2, p3 = self.points
        
        o1 = self.orientation(p1, p2, point)
        o2 = self.orientation(p2, p3, point)
        o3 = self.orientation(p3, p1, point)
        
        # The point is inside if all orientations are the same
        return o1 == o2 == o3

    # Checks if the triangle is degenerate (i.e., points are collinear)
    def isDegenerate(self):
        p1, p2, p3 = self.points
        return self.orientation(p1, p2, p3) == 0  # Collinear points indicate a degenerate triangle
    
    # Calculates the circumcenter of the triangle (center of the circumcircle)
    def circumcenter(self):
        p1, p2, p3 = self.points

        Ax, Ay = p1.getX(), p1.getY()
        Bx, By = p2.getX(), p2.getY()
        Cx, Cy = p3.getX(), p3.getY()

        # Vectors from point A to points B and C
        vectorAB = (Bx - Ax, By - Ay)
        vectorAC = (Cx - Ax, Cy - Ay)
        
        # Perpendicular bisectors (mediatrices) of AB and AC
        mediatriceAB = (-vectorAB[1], vectorAB[0])
        mediatriceAC = (-vectorAC[1], vectorAC[0])
        
        # Midpoints of AB and AC
        D = dataStructuresPoly.Point((Ax + Bx) / 2, (Ay + By) / 2)
        E = dataStructuresPoly.Point((Ax + Cx) / 2, (Ay + Cy) / 2)

        Dx, Dy = D.getX(), D.getY()
        medABx, medABy = mediatriceAB
        
        Ex, Ey = E.getX(), E.getY()
        medACx, medACy = mediatriceAC

        # Solving system of linear equations to find intersection of mediatrices
        A = [
            [medABx, -medACx],
            [medABy, -medACy]
        ]
        b = [
            Ex - Dx,
            Ey - Dy
        ]
        
        det = A[0][0] * A[1][1] - A[0][1] * A[1][0]  # Determinant of matrix A

        if det == 0:  # Lines are parallel, no unique solution
            return None, None
        
        inv_det = 1 / det
        invA = [
            [A[1][1] * inv_det, -A[0][1] * inv_det],
            [-A[1][0] * inv_det, A[0][0] * inv_det]
        ]

        # Solving for intersection coordinates
        t1 = invA[0][0] * b[0] + invA[0][1] * b[1]
        t2 = invA[1][0] * b[0] + invA[1][1] * b[1]
       
        center_x = Dx + t1 * medABx
        center_y = Dy + t1 * medABy

        center = dataStructuresPoly.Point(center_x, center_y)

        # Radius of the circumcircle is the distance from center to any vertex
        radius = self.distance(p1, center)

        return center, radius

    # Calculates the Euclidean distance between two points
    def distance(self, point1, point2):
        return math.sqrt((point1.getX() - point2.getX())**2  + (point1.getY() - point2.getY())**2)
    
    # Checks if a point is inside the circumcircle of the triangle
    def isPointInsideCircumcircle(self, point):
        center, radius = self.circumcenter()
        if center is None:
            return False

        distance = self.distance(center, point)
    
        # Floating-point tolerance to handle precision issues
        epsilon = 1e-6
        return distance <= radius + epsilon
class Triangulation:
    def __init__(self, screen):
        self.triangles = []
        self.hull = HullConvex()
        self.screen = screen
        self.stepByStep = False

    def findTriangleThatContainsPoint(self, point):
        for triangle in self.triangles:
            if triangle.pointInsideTriangle(point):
                return triangle
        return None


    def triangulateConvexHull(self):
        self.hull.graham()
        convex_hull_points = self.hull.points
        
        reference_point = min(self.hull.points, key=lambda p : p.getY())
        segments = self.sortSegmentsByReferencePoint(reference_point, self.hull.segments)
        
        for i in range(len(segments)):
            triangle = Triangle(reference_point, segments[i].p1, segments[i].p2)
            self.triangles.append(triangle)
            
            if self.stepByStep:
                screen.fill((255, 255, 255))
                draw_triangles(self.screen, self.triangles)
                draw_points(self.screen, self.hull.points)
                pygame.display.flip()
                pygame.time.wait(100)
        
        self.updateNeighbours()
        self.insertConvexAllPoints(convex_hull_points, segments)
        
    def sortSegmentsByReferencePoint(self, reference_point, segments):
        # Trouver l'index du segment contenant le reference_point
        for i, segment in enumerate(segments):
            if self.segmentContainsPoint(segment, reference_point):
                # Amener ce segment au début
                segments.insert(0, segments.pop(i))
                break
        return segments

    def segmentContainsPoint(self, segment, point):
        # Vérifie si le segment contient le point (p1 ou p2)
        return segment.p1 == point or segment.p2 == point

    def isOnConvexHull(self, point, segments):
        for segment in segments:
            if self.segmentContainsPoint(segment, point):
                return True
        return False
    
    def insertConvexAllPoints(self, points, segments):
        i = 0
        for point in points :
            print(f"{i + 1} / {len(self.hull.points)} : Inserting point ({point.x}, {point.y})")
            if not self.isOnConvexHull(point, segments) :
                self.insertPointIntoTriangulation(point)
                
                if self.stepByStep:
                    screen.fill((255, 255, 255))
                    draw_triangles(self.screen, self.triangles)
                    draw_points(self.screen, self.hull.points)
                    pygame.display.flip()
                    pygame.time.wait(100)
            i += 1

    def insertPointIntoTriangulation(self, point, isIncremental=False):
        triangle_containing_point = self.findTriangleThatContainsPoint(point)
        if not triangle_containing_point:
            print(f"Le point ({point.x},{point.y}) n'est pas dans la triangulation.")
            return

        p1, p2, p3 = triangle_containing_point.points

        new_triangle1 = Triangle(p1, p2, point)
        new_triangle2 = Triangle(p2, p3, point)
        new_triangle3 = Triangle(p3, p1, point)

        # Skip degenerate triangles
        if new_triangle1.isDegenerate() or new_triangle2.isDegenerate() or new_triangle3.isDegenerate():
            print("Triangle dégénéré trouvé, il ne sera pas ajouté.")
            return

        idx1 = len(self.triangles)
        idx2 = idx1 + 1
        idx3 = idx2 + 1

        neighbours = triangle_containing_point.neighbours

        new_triangle1.fillIndexNeighbours(neighbours[0], idx2, idx3)
        new_triangle2.fillIndexNeighbours(idx1, neighbours[1], idx3)
        new_triangle3.fillIndexNeighbours(idx1, idx2, neighbours[2])
        
        self.triangles.remove(triangle_containing_point)

        self.triangles.extend([new_triangle1, new_triangle2, new_triangle3])

        self.updateNeighbours()

        if isIncremental:
            self.delaunayCheck(new_triangle1)
            self.delaunayCheck(new_triangle2)
            self.delaunayCheck(new_triangle3)

    def sortPointsByAngle(self, reference_point, points):
        def angle_from_reference(p):
            dx = p.getX() - reference_point.getX()
            dy = p.getY() - reference_point.getY()
            return math.atan2(dy, dx)
        
        return sorted(points, key=angle_from_reference)

    def insertPoints(self, internal_points):
        for point in internal_points:
            self.insertPointIntoTriangulation(point)

    def delaunayCheck(self, t=None):
        stack = []
        for point in self.hull.points:
            if t.isPointInsideCircumcircle(point):
                stack.append(t)
        self.checkDelaunayCondition(stack, True)

    def getStack(self):
        stack = []
        for point in self.hull.points:
            for triangle in self.triangles:
                if triangle.isPointInsideCircumcircle(point):
                    stack.append(triangle)
        return stack

    def checkDelaunayCondition(self, stack, isIncremental):
        while stack:
            triangle = stack.pop()

            if triangle not in self.triangles:
                continue

            for i, neighbor_index in enumerate(triangle.neighbours):
                if neighbor_index == -1:
                    continue

                neighbor_triangle = self.triangles[neighbor_index]
                shared_edge = self.findSharedEdge(triangle, neighbor_triangle)

                if shared_edge:
                    opposite_point_in_neighbor = self.getOppositePoint(neighbor_triangle, shared_edge)
                    if opposite_point_in_neighbor is None:
                        continue

                    if triangle.isPointInsideCircumcircle(opposite_point_in_neighbor):
                        self.flipEdge(triangle, neighbor_triangle, shared_edge, isIncremental)

                                                
    def shouldFlipEdge(self, triangle1, triangle2, edge):
        # Vérifiez si le point opposé dans l'autre triangle est à l'intérieur du cercle circonscrit
        opposite_point_in_triangle1 = triangle1.getOppositePoint(edge)
        opposite_point_in_triangle2 = triangle2.getOppositePoint(edge)

        # Vérifiez la condition Delaunay
        if triangle1.isPointInsideCircumcircle(opposite_point_in_triangle2) or triangle2.isPointInsideCircumcircle(opposite_point_in_triangle1):
            return True
        return False

                        
    def removeTriangle(self, triangle):
        for t in self.triangles:
            p1, p2, p3 = t.points
            if (p1 == triangle.points[0] and triangle.points[1] == p2 and p3 == triangle.points[2]) or (p2 == triangle.points[0] and triangle.points[1] == p3 and p1 == triangle.points[2]) or (p3 == triangle.points[0] and triangle.points[1] == p1 and p2 == triangle.points[2]):
                self.triangles.remove(t)

    def findSharedEdge(self, triangle1, triangle2):
        # Finds the shared edge between two triangles
        shared_points = [p for p in triangle1.points if p in triangle2.points]
        if len(shared_points) == 2:
            return shared_points
        return None

    def flipEdge(self, triangle1, triangle2, shared_edge, isIncremental=False):
        p1, p2 = shared_edge
        opposite_point1 = self.getOppositePoint(triangle1, shared_edge)
        opposite_point2 = self.getOppositePoint(triangle2, shared_edge)

        new_triangle1 = Triangle(opposite_point1, p1, opposite_point2)
        new_triangle2 = Triangle(opposite_point1, p2, opposite_point2)

        # Skip flip if new triangles are degenerate
        if new_triangle1.isDegenerate() or new_triangle2.isDegenerate():
            print("Flip ignoré car cela créerait un triangle dégénéré.")
            return

        idx_triangle1 = self.triangleIndex(triangle1)
        idx_triangle2 = self.triangleIndex(triangle2)

        # Replace old triangles with new triangles
        self.triangles[idx_triangle1] = new_triangle1
        self.triangles[idx_triangle2] = new_triangle2

        # Update neighbours and continue with flip process
        self.updateNeighbours()
        
        if self.stepByStep:
            screen.fill((255, 255, 255))
            draw_triangles(self.screen, self.triangles)
            draw_points(self.screen, self.hull.points)
            pygame.display.flip()
            pygame.time.wait(100)

        if isIncremental:
            self.delaunayCheck(new_triangle1)
            self.delaunayCheck(new_triangle2)

    def triangleIndex(self, triangle):
        for i,t in enumerate(self.triangles):
            p1, p2, p3 = t.points
            if (p1 == triangle.points[0] and triangle.points[1] == p2 and p3 == triangle.points[2]) or (p2 == triangle.points[0] and triangle.points[1] == p3 and p1 == triangle.points[2]) or (p3 == triangle.points[0] and triangle.points[1] == p1 and p2 == triangle.points[2]):
                return i
        return -1
            
    def neighboursIndex(self, idx_triangle):
        for t in self.triangles:
            for i, n in enumerate(t.neighbours):
                if idx_triangle == n:
                    return i
        return -1
     
    def findNewNeighborIdx(self, triangle):
        # Find index of the new neighbor triangle after the edge flip
        for i, t in enumerate(self.triangles):
            if t is triangle:
                return i
        return -1
    
    def arePointsEqual(self, p1, p2, epsilon=1e-6):
        return abs(p1.getX() - p2.getX()) < epsilon and abs(p1.getY() - p2.getY()) < epsilon

    # Modify getOppositePoint to use the arePointsEqual helper
    def getOppositePoint(self, triangle, edge):
        for point in triangle.points:
            if not (self.arePointsEqual(point, edge[0]) or self.arePointsEqual(point, edge[1])):
                return point
        return None

    # Other methods remain unchanged

    # Example of updateNeighbours using arePointsEqual to check edge equivalence
    def updateNeighbours(self):
        # Dictionnaire pour stocker les arêtes et les triangles associés
        edge_to_triangle = {}

        # Parcourir les triangles pour identifier leurs arêtes
        for i, triangle in enumerate(self.triangles):
            points = triangle.points
            for j in range(3):
                # Identifier une arête en triant les points pour éviter les inversions
                edge = tuple(sorted([points[j], points[(j + 1) % 3]], key=lambda p: (p.getX(), p.getY())))
                if edge in edge_to_triangle:
                    edge_to_triangle[edge].append(i)
                else:
                    edge_to_triangle[edge] = [i]

        # Mise à jour des voisins en fonction des arêtes partagées
        for i, triangle in enumerate(self.triangles):
            points = triangle.points
            neighbours = [-1, -1, -1]

            for j in range(3):
                edge = tuple(sorted([points[j], points[(j + 1) % 3]], key=lambda p: (p.getX(), p.getY())))
                if edge in edge_to_triangle:
                    neighbour_indices = edge_to_triangle[edge]
                    for ni in neighbour_indices:
                        if ni != i:
                            neighbours[j] = ni
                            break
            
            triangle.fillIndexNeighbours(*neighbours)


        
    def slowDelaunay(self):
        self.triangulateConvexHull()
        
        for triangle in self.triangles:
            self.delaunayCheck(triangle)
        
        screen.fill((255, 255, 255))
        draw_triangles(self.screen, self.triangles)
        draw_points(self.screen, self.hull.points)
        pygame.display.flip()
        pygame.time.wait(100)

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
        p1 = dataStructuresPoly.Point(mid_x - 6 * deltaMax, mid_y - deltaMax)
        p2 = dataStructuresPoly.Point(mid_x, mid_y + deltaMax)
        p3 = dataStructuresPoly.Point(mid_x + 6 * deltaMax, mid_y - deltaMax)

        super_triangle = Triangle(p1, p2, p3)
        self.triangles.append(super_triangle)
        return super_triangle

    def delaunayIncremental(self):
        super_triangle = self.createSuperTriangle()
        
        if self.stepByStep:
            screen.fill((255, 255, 255))
            draw_triangles(self.screen, self.triangles)
            draw_points(self.screen, self.hull.points)
            pygame.display.flip()
            pygame.time.wait(100)
        
        for i,point in enumerate(self.hull.points):
            print(f"{i + 1} / {len(self.hull.points)} : Inserting point ({point.x}, {point.y})")
            self.insertPointIntoTriangulation(point, True)
            
        self.removeSuperTriangle(super_triangle)
        
        screen.fill((255, 255, 255))
        draw_triangles(self.screen, self.triangles)
        draw_points(self.screen, self.hull.points)
        pygame.display.flip()
        pygame.time.wait(100)

    def removeSuperTriangle(self, super_triangle):
        super_points = super_triangle.points
        
        # Récupérer les triangles valides (ceux qui ne contiennent pas de points du super-triangle)
        valid_triangles = []

        for triangle in self.triangles:
            for i in range(3):
                if not self.isOnePointInSuperTriangle(super_points, triangle.points):
                    valid_triangles.append(triangle)
        
        # Mettre à jour la liste des triangles en ne gardant que les triangles valides
        self.triangles = valid_triangles

        # Réinitialiser les voisins des triangles restants
        self.updateNeighbours()

        print("Super triangle supprimé et voisins mis à jour.")
        
    def isOnePointInSuperTriangle(self, super_triangle, points):
        for i in range(3):
            if self.arePointsEqual(super_triangle[0], points[i]) or self.arePointsEqual(super_triangle[1], points[i]) or self.arePointsEqual(super_triangle[2], points[i]): 
                return True
        return False
        
class Voronoi:
    def __init__(self):
        self.cells = {}
        
    def addCell(self, point, vertices):
        self.cells[point] = vertices
        
    def getCell(self, point):
        self.cells.get(point, [])
        
    def computeVoronoiDiagram(self, triangulation):
        voronoi_edges = []
        circumcenters = []
        
        triangulation.delaunayIncremental()
        
        for triangle in triangulation.triangles:
            circumcenter, _ = triangle.circumcenter()
            if circumcenter:
                circumcenters.append(circumcenter)
                
        for triangle in triangulation.triangles:
            for i in range(3):
                p1 = triangle.points[i]
                p2 = triangle.points[(i + 1) % 3]
                edge = (p1, p2)
                
                neighbour_index = triangle.neighbours[i]
                
                if neighbour_index == -1:  # Edge on the convex hull
                    voronoi_edges.extend(self.handleConvexHullEdge(triangle, circumcenters, edge))
                else:
                    neighbour_triangle = triangulation.triangles[neighbour_index]
                    circumcenter1, _ = triangle.circumcenter()
                    circumcenter2, _ = neighbour_triangle.circumcenter()
                    
                    if circumcenter1 and circumcenter2:
                        voronoi_edges.append((circumcenter1, circumcenter2))
        
        return voronoi_edges
    
    def handleConvexHullEdge(self, triangle, circumcenters, edge):
        circumcenter, _ = triangle.circumcenter()
        if not circumcenter:
            return []
        
        p1, p2 = edge
        edge_vector = (p2.x - p1.x, p2.y - p1.y)
        orthogonal_vector = (-edge_vector[1], edge_vector[0])
        
        far_point = dataStructuresPoly.Point(
            circumcenter.getX() + orthogonal_vector[0] * 1000,  # Extend far enough
            circumcenter.getY() + orthogonal_vector[1] * 1000
        )
        
        return [(circumcenter, far_point)]

def draw_triangles(screen, triangles):
    for triangle in triangles:
        points = triangle.points
        pygame.draw.line(screen, (0, 0, 0), (points[0].getX(), points[0].getY()), (points[1].getX(), points[1].getY()), 2)
        pygame.draw.line(screen, (0, 0, 0), (points[1].getX(), points[1].getY()), (points[2].getX(), points[2].getY()), 2)
        pygame.draw.line(screen, (0, 0, 0), (points[2].getX(), points[2].getY()), (points[0].getX(), points[0].getY()), 2)

def draw_points(screen, points):
    for point in points:
        pygame.draw.circle(screen, (0, 0, 255), (int(point.getX()), int(point.getY())), 5)
        
def drawVoronoi(screen, edges):
    for edge in edges:
        pygame.draw.line(screen, (0, 255, 0), (edge[0].getX(), edge[0].getY()), (edge[1].getX(), edge[1].getY()), 2)
        pygame.draw.circle(screen, (0, 255, 0), (int(edge[0].getX()), int(edge[0].getY())), 5)
        pygame.draw.circle(screen, (0, 255, 0), (int(edge[1].getX()), int((edge[1].getY()))), 5)

def draw_circumcircles(screen, triangles):
    for triangle in triangles:
        center, radius = triangle.circumcenter()
        if center and radius > 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(center.getX()), int(center.getY())), int(radius), 1)

# Initialisation de pygame
pygame.init()

width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dessin et événements avec Pygame")

running = True
isLaunched = False

if len(sys.argv) < 2:
    print("USAGE : dataStructureTriangulation.py <type> <option> \n"
          "\t <type> :\n"
          "\t\t -n : naive triangulation\n"
          "\t\t -d : slow delaunay\n"
          "\t\t -i : delaunay incremental\n"
          "\t\t -v : Voronoi Diagram\n"
          "\t <option> : \n"
          "\t\t -s : step by step")
    sys.exit()
    
triangulation = Triangulation(screen)
voronoi = Voronoi()

stepByStep = '-s' in sys.argv
naive = '-n' in sys.argv
v = '-v' in sys.argv
slow = '-d' in sys.argv
inc = '-i' in sys.argv
screen.fill((255, 255, 255))
# Boucle principale
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not isLaunched:
                    isLaunched = True
                if isLaunched:
                    if stepByStep:
                            triangulation.stepByStep = True
                    if naive:
                        triangulation.triangulateConvexHull()
                    elif slow:
                        triangulation.slowDelaunay()
                    elif inc:
                        triangulation.delaunayIncremental()
                    elif v:
                        edges = voronoi.computeVoronoiDiagram(triangulation)
                        drawVoronoi(screen, edges)
                    
    pygame.display.flip()

pygame.quit()
sys.exit()



