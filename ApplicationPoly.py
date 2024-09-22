import pygame
import sys
import dataStructuresPoly

# Draws the line segments of the polygon
def draw_segments(screen, poly):
    screen.fill((255, 255, 255))  # Fill background with white
    for segment in poly.segments:
        pygame.draw.line(screen, (0, 0, 0), (segment.p1.getX(), segment.p1.getY()), (segment.p2.getX(), segment.p2.getY()), 1)  # Draw each line segment

# Draws the complete polygon
def draw_polygon(screen, poly):
    if len(poly.points) > 2:  # Ensure there are enough points to form a polygon
        pygame.draw.polygon(screen, (255, 0, 0), [(p.getX(), p.getY()) for p in poly.points])  # Draw the polygon with red color

# Determines the orientation of three points (clockwise, counterclockwise, collinear)
def orientation(p, q, r):
    val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())
    if val == 0:
        return 0  # Collinear
    elif val > 0:
        return 1  # Clockwise
    else:
        return 2  # Counterclockwise

# Checks if a point is inside a convex polygon using orientation checks
def pointInsidePolyConvex(point, poly):
    n = len(poly.points)
   
    first_orientation = None
    for i in range(n):
        p1 = poly.points[i]
        p2 = poly.points[(i + 1) % n]
        
        o = orientation(p1, p2, point)
        
        if first_orientation is None:
            first_orientation = o  # Set initial orientation
        elif o != 0 and o != first_orientation:  # If orientation changes, point is outside
            return False
    
    return True  # If all orientations match, point is inside

# Checks if a point is inside a concave polygon using ray-casting method
def pointInsidePolyConcave(point, poly):
    n = len(poly.points)
    count = 0  # Count of intersections with polygon edges
    x = point.getX()
    y = point.getY()

    for i in range(n):
        next_i = (i + 1) % n
        p1 = poly.points[i]
        p2 = poly.points[next_i]
        
        # Check if the point's Y lies between the Y values of polygon edge
        if min(p1.getY(), p2.getY()) < y <= max(p1.getY(), p2.getY()):
            # Calculate intersection X value
            x_intersect = p1.getX() + ((y - p1.getY()) * (p2.getX() - p1.getX())) / ((p2.getY() - p1.getY()))
            if x < x_intersect:  # If point is to the left of the edge
                count += 1
    
    return count % 2 == 1  # Point is inside if the number of intersections is odd

pygame.init()

# Screen setup
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dessin et événements avec Pygame")

# Game loop variables
running = True
hasPolygon = False
isFinished = False
poly = None
screen.fill((255, 255, 255))
# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Exit the game
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Exit the game with ESC
                running = False
            if event.key == pygame.K_n:  # Start new polygon with 'n' key
                hasPolygon = False
                isFinished = False
                poly = None
                screen.fill((255, 255, 255))  # Clear screen when creating a new polygon
                pygame.display.flip()  # Refresh display

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left-click to add point or check if point is inside polygon
                x, y = pygame.mouse.get_pos()
                if not isFinished:  # Add points while polygon is not closed
                    if not hasPolygon:
                        poly = dataStructuresPoly.Polygon(x, y)  # Create a new polygon
                        hasPolygon = True
                    else:
                        if poly.addPoint(dataStructuresPoly.Point(x, y)):  # Add point and redraw segments
                            draw_segments(screen, poly)
                            pygame.display.flip()
                else:  # Check if the point is inside the polygon after it is finished
                    if poly.isConvex():  # Use appropriate algorithm based on polygon type
                        if pointInsidePolyConvex(dataStructuresPoly.Point(x, y), poly):
                            print("Point is inside polygon")
                        else:
                            print("Point is outside polygon")
                    else:
                        if pointInsidePolyConcave(dataStructuresPoly.Point(x, y), poly):
                            print("Point is inside polygon")
                        else:
                            print("Point is outside polygon")

            elif event.button == 3:  # Right-click to close polygon
                if hasPolygon:
                    poly.closePolygon()  # Mark polygon as finished
                    draw_segments(screen, poly)
                    draw_polygon(screen, poly)
                    pygame.display.flip()
                    isFinished = True

    # Redraw the polygon segments and outline on every frame
    if poly and hasPolygon:
        draw_segments(screen, poly)
        if isFinished:
            draw_polygon(screen, poly)
        pygame.display.flip()

pygame.quit()
sys.exit()
