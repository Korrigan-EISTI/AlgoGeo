import pygame
import sys
import dataStructure3D
import scene

class DrawTriangle:
    def __init__(self):
        self.scene = scene.Scene()
        self.mesh = dataStructure3D.TriangleMesh()
        self.last_mouse_pos = None

    def drawTriangles(self, screen):
        for idx1, idx2, idx3 in self.mesh.index:
            points = [self.scene.apply_transformation(self.mesh.vertex[idx1], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx2], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx3], self.mesh)]

            pygame.draw.line(screen, (0, 0, 0), (int(points[0].x), int(points[0].y)), (int(points[1].x), int(points[1].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[1].x), int(points[1].y)), (int(points[2].x), int(points[2].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[2].x), int(points[2].y)), (int(points[0].x), int(points[0].y)), 2)

    def draw_axes(self, screen):
        # Draw the world axes for reference
        origin = dataStructure3D.vec4(0, 0, 0, 1)
        x_axis = dataStructure3D.vec4(2, 0, 0, 1)
        y_axis = dataStructure3D.vec4(0, 2, 0, 1)
        z_axis = dataStructure3D.vec4(0, 0, 2, 1)

        origin_screen = self.scene.apply_transformation(origin, self.mesh)
        x_axis_screen = self.scene.apply_transformation(x_axis, self.mesh)
        y_axis_screen = self.scene.apply_transformation(y_axis, self.mesh)
        z_axis_screen = self.scene.apply_transformation(z_axis, self.mesh)

        pygame.draw.line(screen, (255, 0, 0), (int(origin_screen.x), int(origin_screen.y)), (int(x_axis_screen.x), int(x_axis_screen.y)), 3)  # X-axis (red)
        pygame.draw.line(screen, (0, 255, 0), (int(origin_screen.x), int(origin_screen.y)), (int(y_axis_screen.x), int(y_axis_screen.y)), 3)  # Y-axis (green)
        pygame.draw.line(screen, (0, 0, 255), (int(origin_screen.x), int(origin_screen.y)), (int(z_axis_screen.x), int(z_axis_screen.y)), 3)  # Z-axis (blue)

    def handle_mouse_events(self):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # Mouse-based camera rotation
        if mouse_buttons[0]:
            if self.last_mouse_pos:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                self.scene.rotate_camera(dx * 0.1, dy * 0.1)  # Scale rotation speed

        # Keyboard-based camera translation
        if keys[pygame.K_z]:
            self.scene.translate_camera(0, 0, 0.1)  # Forward
        if keys[pygame.K_s]:
            self.scene.translate_camera(0, 0, -0.1)  # Backward
        if keys[pygame.K_q]:
            self.scene.translate_camera(-0.1, 0, 0)  # Left
        if keys[pygame.K_d]:
            self.scene.translate_camera(0.1, 0, 0)  # Right
        if keys[pygame.K_a]:
            self.scene.translate_camera(0, 0.1, 0)  # Up
        if keys[pygame.K_e]:
            self.scene.translate_camera(0, -0.1, 0)  # Down

        # Toggle projection mode
        if keys[pygame.K_p]:
            self.scene.is_orthographic = not self.scene.is_orthographic
            if not self.scene.is_orthographic:
                self.scene.set_projection_perspective(800, 600, 0.1, 1000)
            else:
                self.scene.set_projection_orthographic(800, 600, 0.1, 1000)

        self.last_mouse_pos = mouse_pos

    def render(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        self.scene.setup_view_and_projection(800, 600, 0.1, 1000)
        pygame.display.set_caption("3D Projection with Camera and Axes")

        # Add cube vertices
        self.mesh.add_vertex(-1, -1, -1)
        self.mesh.add_vertex(1, -1, -1)
        self.mesh.add_vertex(1, 1, -1)
        self.mesh.add_vertex(-1, 1, -1)
        self.mesh.add_vertex(-1, -1, 1)
        self.mesh.add_vertex(1, -1, 1)
        self.mesh.add_vertex(1, 1, 1)
        self.mesh.add_vertex(-1, 1, 1)

        # Add triangles for the cube
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

            self.handle_mouse_events()
            
            screen.fill((255, 255, 255))
            self.drawTriangles(screen)
            self.draw_axes(screen)  # Draw the world axes
            pygame.display.flip()

triangles = DrawTriangle()
triangles.render()
