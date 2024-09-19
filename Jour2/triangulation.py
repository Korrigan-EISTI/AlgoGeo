import pygame
import dataStructuresTriangulation
import sys

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

# Initialisation de la triangulation avec le triangle initial
triangulation = dataStructuresTriangulation.Triangulation(screen)
voronoi = dataStructuresTriangulation.Voronoi()

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

                #edges = voronoi.computeVoronoiDiagram(triangulation)
                #triangulation.slowDelaunay()
                triangulation.delaunayIncremental()
                '''screen.fill((255, 255, 255))
                draw_triangles(screen, triangulation.triangles)
                draw_points(screen, triangulation.hull.points)
                #draw_circumcircles(screen, triangulation.triangles)'''
                #drawVoronoi(screen, edges)

    pygame.display.flip()  # Rafraîchir l'écran

pygame.quit()
sys.exit()
