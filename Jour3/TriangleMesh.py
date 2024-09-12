import scene
import dataStructure3D
import pygame
import sys

class DrawTriangle:
    def __init__(self):
        self.scene = scene.Scene()
        self.mesh = dataStructure3D.TriangleMesh()
        self.last_mouse_pos = None
        self.is_rotating = False
        self.is_translating = False

    def drawTriangles(self, screen):
        for idx1, idx2, idx3 in self.mesh.index:
            # Récupérer les points transformés
            points = [self.scene.apply_transformation(self.mesh.vertex[idx1], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx2], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx3], self.mesh)]

            # Dessiner les lignes du triangle
            pygame.draw.line(screen, (0, 0, 0), (int(points[0].x), int(points[0].y)), (int(points[1].x), int(points[1].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[1].x), int(points[1].y)), (int(points[2].x), int(points[2].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[2].x), int(points[2].y)), (int(points[0].x), int(points[0].y)), 2)

    def handle_mouse_events(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()  # Obtenir les états des touches

        if mouse_buttons[0]:  # Si le bouton gauche de la souris est enfoncé
            if self.last_mouse_pos:
                dx = mouse_pos[0] - self.last_mouse_pos[0]  # Différence en x
                dy = mouse_pos[1] - self.last_mouse_pos[1]  # Différence en y

                # Appliquer yaw pour le mouvement horizontal (gauche-droite)
                if dx != 0:
                    self.mesh.yaw(dx)
                if dy != 0:
                    self.mesh.pitch(dy)

        elif mouse_buttons[2]:
            if self.last_mouse_pos:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                
                tx = dx
                ty = dy

                objectCoordsSystemTranslation = dataStructure3D.vec4(tx, ty, 0, 1)

                invViewPortProj = (self.scene.viewport_matrix.inverse()).matrixMultiplication(self.scene.projection_matrix.inverse())
                invViewportProjView = (self.scene.view_matrix.inverse()).matrixMultiplication(invViewPortProj)
                inverse = (self.mesh.model_matrix.inverse()).matrixMultiplication(invViewportProjView)
                objectCoordsSystemTranslation = inverse.vectorMultiplication(objectCoordsSystemTranslation)

                self.mesh.translate(objectCoordsSystemTranslation.x, objectCoordsSystemTranslation.y, objectCoordsSystemTranslation.z)

        # Zoom avec les touches + et -
        if keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]:  # Vérifier si la touche + est enfoncée
            self.mesh.scale(1.01)  # Zoom avant, augmente la taille de 10%
        elif keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:  # Vérifier si la touche - est enfoncée
            self.mesh.scale(0.9)  # Zoom arrière, diminue la taille de 10%

        # Mettre à jour la dernière position de la souris
        self.last_mouse_pos = mouse_pos


    def render(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        self.scene.setup_view_and_projection(800, 600, 0.1, 1000)
        pygame.display.set_caption("Affichage 3D Cube")
        
        # Ajouter les sommets du cube
        self.mesh.add_vertex(-1, -1, -1)
        self.mesh.add_vertex(1, -1, -1)
        self.mesh.add_vertex(1, 1, -1)
        self.mesh.add_vertex(-1, 1, -1)
        self.mesh.add_vertex(-1, -1, 1)
        self.mesh.add_vertex(1, -1, 1)
        self.mesh.add_vertex(1, 1, 1)
        self.mesh.add_vertex(-1, 1, 1)
        
        # Ajouter les triangles du cube
        self.mesh.add_triangle(0, 1, 2)
        self.mesh.add_triangle(0, 2, 3)
        self.mesh.add_triangle(4, 5, 6)
        self.mesh.add_triangle(4, 6, 7)
        self.mesh.add_triangle(0, 1, 5)
        self.mesh.add_triangle(0, 5, 4)
        self.mesh.add_triangle(2, 3, 7)
        self.mesh.add_triangle(2, 7, 6)
        self.mesh.add_triangle(0, 3, 7)
        self.mesh.add_triangle(0, 7, 4)
        self.mesh.add_triangle(1, 2, 6)
        self.mesh.add_triangle(1, 6, 5)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Gérer les événements de la souris pour yaw, pitch, zoom et translation
            self.handle_mouse_events()
            
            screen.fill((255, 255, 255))
            self.drawTriangles(screen)
            pygame.display.flip()

# Initialiser et lancer
drawTri = DrawTriangle()
drawTri.render()
