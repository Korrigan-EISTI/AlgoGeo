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
triangulation = dataStructuresTriangulation.Triangulation()

screen.fill((255, 255, 255))
draw_points(screen, triangulation.hull.points)
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

                triangulation.delaunayIncremental()
                screen.fill((255, 255, 255))
                draw_points(screen, triangulation.hull.points)
                draw_triangles(screen, triangulation.triangles)

    pygame.display.flip()  # Rafraîchir l'écran

pygame.quit()
sys.exit()
