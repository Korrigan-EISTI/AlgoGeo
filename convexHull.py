import dataStructuresPoly
import pygame
import sys
import random
import math

# Class to generate convex hull and support step-by-step execution for visualization
class HullConvex:
    def __init__(self):
        self.points = []
        n = random.randint(50, 100)  # Generate 50 random points
        for i in range(n):
            self.points.append(dataStructuresPoly.Point(float(random.randint(100, 1180)), float(random.randint(100, 620))))  # Generate random points
        self.segments = []  # Segments forming the convex hull
        self.current_step = 0
        self.hull = []
        self.extremeEdges_step = (0, 0)  # For step-by-step extreme edges calculation
        self.graham_index = 0  # For step-by-step Graham's scan
        self.current_point = None
        self.current_segments = []

    # Step function for Extreme Edges calculation
    def stepExtremeEdges(self):
        pi, pj = self.extremeEdges_step

        if pi >= len(self.points) or pj >= len(self.points):
            return  # Stop when all point pairs have been processed

        p1 = self.points[pi]
        p2 = self.points[pj]

        if self.isExtremeEdge(p1, p2):
            self.current_segments.append(dataStructuresPoly.Segment(p1.x, p2.x, p1.y, p2.y))  # Add extreme edge segment

        pj += 1
        if pj >= len(self.points):
            pi += 1
            pj = pi + 1
            if pi >= len(self.points):
                self.segments = self.current_segments  # Finalize the segments after processing all points
                self.current_point = None
                return

        if pi < len(self.points) and pj < len(self.points):
            self.current_point = (self.points[pi], self.points[pj])  # Update the current point pair
        else:
            self.current_point = None

        self.extremeEdges_step = (pi, pj)

    # Complete extreme edges calculation without steps
    def extremeEdges(self):
        convexHull = []
        n = len(self.points)
        for p_i in range(n):
            for pj in range(p_i + 1, n):
                if self.isExtremeEdge(self.points[p_i], self.points[pj]):
                    convexHull.append(dataStructuresPoly.Segment(self.points[p_i].x, self.points[pj].x, self.points[p_i].y, self.points[pj].y))
        self.segments = convexHull

    # Step function for Jarvis March
    def stepJarvis(self):
        if self.current_step == 0:
            self.hull = []
            self.lowestPoint = min(self.points, key=lambda p: p.getX())  # Start with the lowest point
            self.p1 = self.lowestPoint
            self.current_segments = []
            self.current_point = self.lowestPoint

        if self.p1 == self.lowestPoint and len(self.hull) > 1:
            self.hull.append(self.lowestPoint)
            self.segments = [dataStructuresPoly.Segment(self.hull[i].getX(), self.hull[(i + 1) % len(self.hull)].getX(),
                                                        self.hull[i].getY(), self.hull[(i + 1) % len(self.hull)].getY())
                            for i in range(len(self.hull))]
            self.current_segments = self.segments
            return

        self.hull.append(self.p1)
        next_point = None

        for candidate_point in self.points:
            if candidate_point == self.p1:
                continue

            if next_point is None:
                next_point = candidate_point
            else:
                orient = self.orientation(self.p1, next_point, candidate_point)
                if orient > 0 or (orient == 0 and self.distance(self.p1, candidate_point) > self.distance(self.p1, next_point)):
                    next_point = candidate_point

        if next_point is not None:
            self.p1 = next_point
            self.current_point = next_point
        else:
            print("No valid next point found, breaking out.")
            return

        if len(self.hull) > 1:
            self.current_segments = [dataStructuresPoly.Segment(self.hull[i].getX(), self.hull[(i + 1) % len(self.hull)].getX(),
                                                                self.hull[i].getY(), self.hull[(i + 1) % len(self.hull)].getY())
                                    for i in range(len(self.hull))]

        self.current_step += 1

    # Complete Jarvis March (Gift Wrapping) algorithm
    def jarvis(self):
        self.hull = []
        self.lowestPoint = min(self.points, key=lambda p: p.getX())
        self.p1 = self.lowestPoint
        
        while True:
            self.hull.append(self.p1)
            q = self.points[0]
            for r in self.points:
                if q == self.p1:
                    q = r
                elif self.orientation(self.p1, q, r) > 0 or (self.orientation(self.p1, q, r) == 0 and self.distance(self.p1, r) > self.distance(self.p1, q)):
                    q = r
            if q == self.lowestPoint:
                break
            self.p1 = q
        
        self.segments = [dataStructuresPoly.Segment(self.hull[i].x, self.hull[(i + 1) % len(self.hull)].x, self.hull[i].y, self.hull[(i + 1) % len(self.hull)].y) for i in range(len(self.hull))]

    # Step function for Graham's scan
    def stepGraham(self):
        def cross_product(p1, p2, p3):
            return (p2.getX() - p1.getX()) * (p3.getY() - p1.getY()) - (p2.getY() - p1.getY()) * (p3.getX() - p1.getX())

        if self.graham_index == 0:
            def angle_from_reference(p, reference_point):
                dx = p.getX() - reference_point.getX()
                dy = p.getY() - reference_point.getY()
                return math.atan2(dy, dx)

            def sort_points(points, reference_point):
                return sorted(points, key=lambda p: (angle_from_reference(p, reference_point), p.getX()))

            self.lowest_point = min(self.points, key=lambda p: (p.getY(), p.getX()))  # Find lowest point
            self.sorted_points = sort_points(self.points, self.lowest_point)
            self.hull = [self.lowest_point]
            self.graham_index += 1
            self.current_point = self.sorted_points[0]
            self.current_segments = []

        if self.graham_index < len(self.sorted_points):
            p = self.sorted_points[self.graham_index]
            while len(self.hull) > 1 and cross_product(self.hull[-2], self.hull[-1], p) <= 0:
                self.hull.pop()
            self.hull.append(p)
            self.current_segments = [dataStructuresPoly.Segment(self.hull[i].getX(), self.hull[(i + 1) % len(self.hull)].getX(),
                                                                self.hull[i].getY(), self.hull[(i + 1) % len(self.hull)].getY())
                                    for i in range(len(self.hull))]
            self.current_point = p
            self.graham_index += 1
        else:
            self.segments = [dataStructuresPoly.Segment(self.hull[i].getX(), self.hull[(i + 1) % len(self.hull)].getX(),
                                                        self.hull[i].getY(), self.hull[(i + 1) % len(self.hull)].getY())
                            for i in range(len(self.hull))]
            self.current_segments = self.segments

    # Complete Graham's scan algorithm
    def graham(self):
        def cross_product(p1, p2, p3):
            return (p2.getX() - p1.getX()) * (p3.getY() - p1.getY()) - (p2.getY() - p1.getY()) * (p3.getX() - p1.getX())

        def angle_from_reference(p, reference_point):
            dx = p.getX() - reference_point.getX()
            dy = p.getY() - reference_point.getY()
            return math.atan2(dy, dx)

        def sort_points(points, reference_point):
            return sorted(points, key=lambda p: (angle_from_reference(p, reference_point), p.getX()))
        
        lowest_point = min(self.points, key=lambda p: (p.getY(), p.getX()))
        sorted_points = sort_points(self.points, lowest_point)
        
        hull = [lowest_point]
        
        for p in sorted_points:
            while len(hull) > 1 and cross_product(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)
   
        segments = []
        n = len(hull)
        for i in range(n):
            p1 = hull[i]
            p2 = hull[(i + 1) % n]
            segments.append(dataStructuresPoly.Segment(p1.x, p2.x, p1.y, p2.y))
        
        self.segments = segments

    # Helper function to check orientation of 3 points
    def orientation(self, p, q, r):
        return (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())

    # Helper function to calculate distance between two points
    def distance(self, p1, p2):
        return math.sqrt((p2.getX() - p1.getX()) ** 2 + (p2.getY() - p1.getY()) ** 2)

    # Check if a segment between two points is an extreme edge
    def isExtremeEdge(self, p1, p2):
        sign = None
        for pk in self.points:
            if pk == p1 or pk == p2:
                continue
            v1x = p2.getX() - p1.getX()
            v1y = p2.getY() - p1.getY()
            v2x = pk.getX() - p1.getX()
            v2y = pk.getY() - p1.getY()
            current_sign = v1x * v2y - v1y * v2x
            if current_sign != 0:
                if sign is None:
                    sign = current_sign
                elif (sign > 0 and current_sign < 0) or (sign < 0 and current_sign > 0):
                    return False
        return True

# Helper function to draw segments on the screen
def draw_segments(screen, segments):
    for segment in segments:
        pygame.draw.line(screen, (0, 0, 0), 
                         (segment.p1.getX(), segment.p1.getY()), 
                         (segment.p2.getX(), segment.p2.getY()), 2)

# Helper function to draw points on the screen
def draw_points(screen, points, current_point=None):
    for point in points:
        color = (0, 0, 0)
        if current_point and (point == current_point[0] or point == current_point[1]):
            color = (255, 0, 0)  # Highlight current point in red
        pygame.draw.circle(screen, color, (int(point.getX()), int(point.getY())), 5)

def __main__():
    # Display usage in case of bad arguments
    if len(sys.argv) < 2:
        print("USAGE : ConvexHull.py <Type of convex Hull> <Type of rapidity>\n "
              "\tType of convex Hull: \n"
              "\t\t-j : jarvis \n"
              "\t\t-e : extreme edges \n"
              "\t\t-g : graham \n"
              "\tType of rapidity\n"
              "\t\t-s : step by step\n")
        sys.exit()

    hullConvex = HullConvex()

    stepByStep = '-s' in sys.argv
    executeJarvis = '-j' in sys.argv
    executeExtremeEdge = '-e' in sys.argv
    executeGraham = '-g' in sys.argv

    # Initialize pygame
    pygame.init()

    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Dessin et événements avec Pygame")

    running = True
    isCreated = False
    isAnimating = False
    screen.fill((255, 255, 255))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not isAnimating:
                    if executeExtremeEdge and not isCreated:
                        if stepByStep:
                            isAnimating = True 
                        else:
                            hullConvex.extremeEdges()
                            isCreated = True
                    elif executeJarvis and not isCreated:
                        if stepByStep:
                            isAnimating = True
                        else:
                            hullConvex.jarvis()
                            isCreated = True
                    elif executeGraham and not isCreated:
                        if stepByStep:
                            isAnimating = True
                        else:
                            hullConvex.graham()
                            isCreated = True

        if isAnimating:
            if executeExtremeEdge and not isCreated:
                hullConvex.stepExtremeEdges()
                if not hullConvex.segments:
                    screen.fill((255, 255, 255))
                    draw_points(screen, hullConvex.points, hullConvex.current_point)
                    draw_segments(screen, hullConvex.current_segments)
                    pygame.display.flip()
                    pygame.time.wait(100)
                else:
                    isCreated = True  # End animation
                    isAnimating = False
            elif executeJarvis and not isCreated:
                hullConvex.stepJarvis()
                if not hullConvex.segments:
                    screen.fill((255, 255, 255))
                    draw_points(screen, hullConvex.points, (hullConvex.p1, hullConvex.current_point))
                    draw_segments(screen, hullConvex.current_segments)
                    pygame.display.flip()
                    pygame.time.wait(100)
                else:
                    isCreated = True
                    isAnimating = False
            elif executeGraham and not isCreated:
                hullConvex.stepGraham()
                if not hullConvex.segments:
                    screen.fill((255, 255, 255))
                    draw_points(screen, hullConvex.points, (hullConvex.lowest_point, hullConvex.current_point))
                    draw_segments(screen, hullConvex.current_segments)
                    pygame.display.flip()
                    pygame.time.wait(100)
                else:
                    isCreated = True
                    isAnimating = False

        # Draw points and segments in non-step mode
        if not stepByStep:
            draw_points(screen, hullConvex.points)
        if isCreated and hullConvex.segments and not stepByStep:
            draw_segments(screen, hullConvex.segments)

        pygame.display.flip()  # Refresh screen

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    __main__()
