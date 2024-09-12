import pygame
import sys
import dataStructuresPoly

def draw_segments(screen, poly):
    screen.fill((255, 255, 255))
    for segment in poly.segments:
        pygame.draw.line(screen, (0, 0, 0), (segment.p1.getX(), segment.p1.getY()), (segment.p2.getX(), segment.p2.getY()), 1)

def draw_polygon(screen, poly):
    if len(poly.points) > 2:
        pygame.draw.polygon(screen, (255, 0, 0), [(p.getX(), p.getY()) for p in poly.points])

def orientation(p, q, r):
    val = (q.getY() - p.getY()) * (r.getX() - q.getX()) - (q.getX() - p.getX()) * (r.getY() - q.getY())
    if val == 0:
        return 0 
    elif val > 0:
        return 1 
    else:
        return 2 

def pointInsidePolyConvex(point, poly):
    n = len(poly.points)
   
    first_orientation = None
    for i in range(n):
        p1 = poly.points[i]
        p2 = poly.points[(i + 1) % n]
        
        o = orientation(p1, p2, point)
        
        if first_orientation is None:
            first_orientation = o
        elif o != 0 and o != first_orientation:
            return False
    
    return True

def pointInsidePolyConcave(point, poly):
    n = len(poly.points)
    count = 0 
    x = point.getX()
    y = point.getY()

    for i in range(n):
        next_i = (i + 1) % n
        p1 = poly.points[i]
        p2 = poly.points[next_i]
        
        if min(p1.getY(), p2.getY()) < y <= max(p1.getY(), p2.getY()):
            x_intersect = p1.getX() + ((y - p1.getY()) * (p2.getX() - p1.getX())) / ((p2.getY() - p1.getY()))
            if x < x_intersect:
                count += 1
    
    return count % 2 == 1

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dessin et événements avec Pygame")

running = True
hasPolygon = False
isFinished = False
poly = None
while running:
    screen.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_n:
                hasPolygon = False
                isFinished = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = pygame.mouse.get_pos()
                if not isFinished:
                    if not hasPolygon:
                        poly = dataStructuresPoly.Polygon(x, y)
                        hasPolygon = True
                    else:
                        if poly.addPoint(dataStructuresPoly.Point(x, y)):
                            draw_segments(screen, poly)
                            pygame.display.flip()
                else:
                    if (poly.isConvex()):
                        if (pointInsidePolyConvex(dataStructuresPoly.Point(x, y), poly)):
                            print("Point is inside polygon")
                        else :
                            print("Point is outside polygon")
                    else:
                        if (pointInsidePolyConcave(dataStructuresPoly.Point(x, y), poly)):
                            print("Point is inside polygon")
                        else :
                            print("Point is outside polygon")

            elif (event.button == 3):
                if hasPolygon:
                    poly.closePolygon()
                    draw_segments(screen, poly)
                    draw_polygon(screen, poly)
                    pygame.display.flip()
                    isFinished = True

    pygame.display.flip()

pygame.quit()
sys.exit()
