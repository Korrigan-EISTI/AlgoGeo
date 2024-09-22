import pygame
import sys
import dataStructure3D
import scene
import math

class DrawTriangle:
    def __init__(self):
        self.scene = scene.Scene()
        self.mesh = dataStructure3D.TriangleMesh()
        self.mesh_axes = dataStructure3D.TriangleMesh()  # Axes mesh
        self.last_mouse_pos = None
        self.is_wireframe = False
        self.is_cube_mode = False

        
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.globalYaw = 0
        self.globalPitch = 0
        self.globalRoll = 0

    def should_cull_backface(self, normal, v1):
        view_vector = v1.sub(self.scene.camera_position).normalize()
        dot_product = normal.dotProduct(view_vector)
        return dot_product >= 0

    def drawTriangles(self, screen):
        for idx1, idx2, idx3 in self.mesh.index:
            points = [self.scene.apply_transformation(self.mesh.vertex[idx1], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx2], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx3], self.mesh)]

            pygame.draw.line(screen, (0, 0, 0), (int(points[0].x), int(points[0].y)), (int(points[1].x), int(points[1].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[1].x), int(points[1].y)), (int(points[2].x), int(points[2].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[2].x), int(points[2].y)), (int(points[0].x), int(points[0].y)), 2)
    
    def drawTrianglesSolid(self, screen):
        for idx1, idx2, idx3 in self.mesh.index:
            v1 = self.scene.apply_transformation(self.mesh.vertex[idx1], self.mesh)
            v2 = self.scene.apply_transformation(self.mesh.vertex[idx2], self.mesh)
            v3 = self.scene.apply_transformation(self.mesh.vertex[idx3], self.mesh)
            points_2d = [(int(v.x), int(v.y)) for v in [v1, v2, v3]]

            vertex1 = (self.scene.view_matrix.matrixMultiplication(self.mesh.model_matrix)).vectorMultiplication(self.mesh.vertex[idx1])
            vertex2 = (self.scene.view_matrix.matrixMultiplication(self.mesh.model_matrix)).vectorMultiplication(self.mesh.vertex[idx2])
            vertex3 = (self.scene.view_matrix.matrixMultiplication(self.mesh.model_matrix)).vectorMultiplication(self.mesh.vertex[idx3])
            
            normal = self.scene.light.calculate_normal(vertex1, vertex2, vertex3)
            cam_pos = dataStructure3D.vec4(self.scene.cameraMatrix.mat[0][3], self.scene.cameraMatrix.mat[1][3], self.scene.cameraMatrix.mat[2][3], self.scene.cameraMatrix.mat[3][3])
            view_vector = vertex1.sub(cam_pos).normalize()

            if normal.dotProduct(view_vector) < 0:
                continue  

            lighting_intensity = self.scene.light.compute_diffuse_light(normal, vertex1)
            '''if (self.throw_ray(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])):
                color = (min(0, int(255 * lighting_intensity)), 0, 0)
            else :'''
            color = (min(255, int(255 * lighting_intensity)), 0, 0)
            pygame.draw.polygon(screen, color, points_2d, 0)
            

    def draw_axes(self, screen):
        origin = dataStructure3D.vec4(0, 0, 0, 1)
        x_axis = dataStructure3D.vec4(2, 0, 0, 1)
        y_axis = dataStructure3D.vec4(0, 2, 0, 1)
        z_axis = dataStructure3D.vec4(0, 0, 2, 1)

        # Applying transformations to the axes mesh instead of the cube mesh
        origin_screen = self.scene.apply_transformation(origin, self.mesh_axes)
        x_axis_screen = self.scene.apply_transformation(x_axis, self.mesh_axes)
        y_axis_screen = self.scene.apply_transformation(y_axis, self.mesh_axes)
        z_axis_screen = self.scene.apply_transformation(z_axis, self.mesh_axes)

        pygame.draw.line(screen, (255, 0, 0), (int(origin_screen.x), int(origin_screen.y)), (int(x_axis_screen.x), int(x_axis_screen.y)), 3)  # X-axis (red)
        pygame.draw.line(screen, (0, 255, 0), (int(origin_screen.x), int(origin_screen.y)), (int(y_axis_screen.x), int(y_axis_screen.y)), 3)  # Y-axis (green)
        pygame.draw.line(screen, (0, 0, 255), (int(origin_screen.x), int(origin_screen.y)), (int(z_axis_screen.x), int(z_axis_screen.y)), 3)  # Z-axis (blue)

    def goBackInInitialState(self, iterations, screen, isExponential=False):
        if iterations == 0:
            return

        font = pygame.font.Font(None, 20)
        # Calcul des angles de rotation par étape
        theta_yaw = self.globalYaw / iterations
        theta_pitch = self.globalPitch / iterations
        theta_roll = self.globalRoll / iterations

        for i in range(1, iterations + 1):
            screen.fill((255, 255, 255))
            current_yaw = self.globalYaw - theta_yaw * float(i)
            current_pitch = self.globalPitch - theta_pitch * float(i)
            current_roll = self.globalRoll - theta_roll * float(i)

            self.display(screen, font, current_yaw, current_pitch, current_roll)

            current_yaw = math.radians(current_yaw)
            current_pitch = math.radians(current_pitch)
            current_roll = math.radians(current_roll)

            if not isExponential:
                roll_matrix = dataStructure3D.mat4(math.cos(current_roll), -math.sin(current_roll), 0, 0,
                                                math.sin(current_roll), math.cos(current_roll), 0, 0,
                                                0, 0, 1, 0,
                                                0, 0, 0, 1)

                pitch_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                    0, math.cos(current_pitch), -math.sin(current_pitch), 0,
                                                    0, math.sin(current_pitch), math.cos(current_pitch), 0,
                                                    0, 0, 0, 1)

                yaw_matrix = dataStructure3D.mat4(math.cos(current_yaw), 0, math.sin(current_yaw), 0,
                                                0, 1, 0, 0,
                                                -math.sin(current_yaw), 0, math.cos(current_yaw), 0, 
                                                0, 0, 0, 1)

                self.mesh.model_matrix = yaw_matrix.matrixMultiplication(pitch_matrix).matrixMultiplication(roll_matrix)
            else:
                # Calcul des matrices de rotation pour la carte exponentielle
                axis_yaw = dataStructure3D.vec3(0, 1, 0)
                axis_pitch = dataStructure3D.vec3(1, 0, 0)
                axis_roll = dataStructure3D.vec3(0, 0, 1)

                matrixYaw = self.mesh.exponential_mapFunction(axis_yaw, math.degrees(current_yaw))
                matrixPitch = self.mesh.exponential_mapFunction(axis_pitch, math.degrees(current_pitch))
                matrixRoll = self.mesh.exponential_mapFunction(axis_roll, math.degrees(current_roll))

                self.mesh.model_matrix = matrixRoll.matrixMultiplication(matrixPitch.matrixMultiplication(matrixYaw))

            self.drawTriangles(screen)
            pygame.display.flip()
            pygame.time.wait(5)

        self.globalYaw, self.globalPitch, self.globalRoll = 0, 0, 0
        self.yaw, self.pitch, self.roll = 0, 0, 0
        self.mesh.euler_intrinsic(self.globalYaw, self.globalPitch, self.globalRoll)

    def display(self, screen, font, yaw, pitch, roll):
        tab = self.mesh.calculate_rotation(yaw, pitch, roll).toString()
        matrix0_angle_text = tab[0]
        matrix1_angle_text = tab[1]
        matrix2_angle_text = tab[2]
        matrix3_angle_text = tab[3]
        euler_angles_text = f"Yaw: {yaw % 360:.2f}°, Pitch: {pitch % 360:.2f}°, Roll: {roll%360:.2f}°"
        y_offset = 20
        text_surface = font.render(matrix0_angle_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        text_surface = font.render(matrix1_angle_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        text_surface = font.render(matrix2_angle_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        text_surface = font.render(matrix3_angle_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        text_surface = font.render(euler_angles_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))

    def throw_ray(self, mouse_x, mouse_y):
        # Step 1: Convert mouse position to normalized device coordinates (NDC)
        screen_width, screen_height = pygame.display.get_surface().get_size()
        ndc_x = (2.0 * mouse_x) / screen_width - 1.0
        ndc_y = 1.0 - (2.0 * mouse_y) / screen_height  # Inverted Y-axis for NDC

        # Step 2: Create the ray in view space (using inverse of projection matrix)
        # Near point (NDC space)
        ray_clip = dataStructure3D.vec4(ndc_x, ndc_y, -1.0, 1.0)  # Point on near plane
        # Far point (NDC space)
        ray_far_clip = dataStructure3D.vec4(ndc_x, ndc_y, 1.0, 1.0)  # Point on far plane

        # Transform ray into world space using inverse view and projection matrices
        viewport_inverse = self.scene.viewport_matrix.inverse()
        inverse_projection = self.scene.projection_matrix.inverse()
        inverse_view = self.scene.view_matrix.inverse()

        # Step 3: Convert the clip space coordinates to world space
        ray_eye = (inverse_projection.matrixMultiplication(viewport_inverse)).vectorMultiplication(ray_clip)
        ray_eye_far = (inverse_projection.matrixMultiplication(viewport_inverse)).vectorMultiplication(ray_far_clip)

        ray_eye.z = -1.0
        ray_eye.w = 0.0
        ray_eye_far.z = 1.0
        ray_eye_far.w = 0.0

        # Step 4: Transform the ray to world space
        ray_world = inverse_view.vectorMultiplication(ray_eye)
        ray_world_far = inverse_view.vectorMultiplication(ray_eye_far)
        ray_direction = ray_world_far.sub(ray_world).normalize()

        # Step 5: Check for intersections with the plane of the triangles
        closest_intersection = None
        closest_distance = float('inf')
        
        for idx1, idx2, idx3 in self.mesh.index:
            v1 = self.mesh.vertex[idx1]
            v2 = self.mesh.vertex[idx2]
            v3 = self.mesh.vertex[idx3]

            intersection, distance = self.ray_intersects_plane(ray_world, ray_direction, v1, v2, v3)

            if intersection and distance < closest_distance:
                closest_intersection = intersection
                closest_distance = distance

        return closest_intersection  # Return the closest intersection point, if any

    def ray_intersects_plane(self, ray_origin, ray_direction, v1, v2, v3):
        # Step 1: Calculate the normal of the triangle plane
        edge1 = v2.sub(v1)
        edge2 = v3.sub(v1)
        normal = edge1.crossProduct(edge2).normalize()

        # Step 2: Check if the ray is parallel to the plane
        denominator = normal.dotProduct(ray_direction)
        if abs(denominator) < 1e-8:
            return None, None  # Ray is parallel to the plane

        # Step 3: Calculate the intersection point with the plane
        d = normal.dotProduct(v1)  # Distance from the origin to the plane
        t = (d - normal.dotProduct(ray_origin)) / denominator

        if t < 0:
            return None, None  # The intersection is behind the ray origin

        # Step 4: Compute the intersection point
        intersection_point = ray_origin.add(ray_direction.mul(t))
        return intersection_point, t
    
    def handle_mouse_events(self, screen):
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_m]:
            self.is_cube_mode = not self.is_cube_mode

        if keys[pygame.K_p]:
                self.scene.is_orthographic = not self.scene.is_orthographic
                if not self.scene.is_orthographic:
                    self.scene.set_projection_perspective(800, 600, 0.1, 1000)
                else:
                    self.scene.set_projection_orthographic(800, 600, 0.1, 1000)

        if keys[pygame.K_w]:
                self.is_wireframe = not self.is_wireframe

        if self.is_cube_mode :
            if mouse_buttons[0]: 
                self.yaw = 0.1
                self.globalYaw += 0.1
            else:
                self.yaw = 0

            if mouse_buttons[1]: 
                self.pitch = 0.1
                self.globalPitch += 0.1
            else:
                self.pitch = 0

            if mouse_buttons[2]: 
                self.roll = 0.1
                self.globalRoll += 0.1
            else:
                self.roll = 0

            if keys[pygame.K_c]:
                self.goBackInInitialState(100, screen, isExponentialMap)

            if isEulerAngles:
                if isIntrinsic:
                    self.mesh.euler_intrinsic(self.yaw, self.pitch, self.roll)
                if isExtrinsic:
                    self.mesh.euler_extrinsic(self.yaw, self.pitch, self.roll)

            if isExponentialMap:
                if (self.yaw > 0):
                    self.mesh.exponential_map(dataStructure3D.vec3(0, 1, 0), self.yaw)
                if (self.pitch > 0):
                    self.mesh.exponential_map(dataStructure3D.vec3(1, 0, 0), self.pitch)
                if (self.roll > 0):
                    self.mesh.exponential_map(dataStructure3D.vec3(0, 0, 1), self.roll)

        else : 
            if mouse_buttons[0]:
                if self.last_mouse_pos:
                    dx = mouse_pos[0] - self.last_mouse_pos[0]
                    dy = mouse_pos[1] - self.last_mouse_pos[1]
                    self.scene.rotate_camera(dx * 0.1, dy * 0.1)  # Scale rotation speed

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

            self.last_mouse_pos = mouse_pos

    def render(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        self.scene.setup_view_and_projection(800, 600, 0.1, 1000)
        pygame.display.set_caption("3D Projection with Camera and Axes")

        self.mesh.add_vertex(-1, -1, -1)  # 0
        self.mesh.add_vertex(1, -1, -1)   # 1
        self.mesh.add_vertex(1, 1, -1)    # 2
        self.mesh.add_vertex(-1, 1, -1)   # 3
        self.mesh.add_vertex(-1, -1, 1)   # 4
        self.mesh.add_vertex(1, -1, 1)    # 5
        self.mesh.add_vertex(1, 1, 1)     # 6
        self.mesh.add_vertex(-1, 1, 1)    # 7

        # Front face
        self.mesh.add_triangle(0, 1, 2)   # Keep this order
        self.mesh.add_triangle(0, 2, 3)   # Keep this order

        # Back face
        self.mesh.add_triangle(4, 6, 5)   # Reorder for counterclockwise (was 4, 5, 6)
        self.mesh.add_triangle(4, 7, 6)   # Reorder for counterclockwise (was 4, 6, 7)

        # Left face
        self.mesh.add_triangle(0, 4, 5)   # Reorder for counterclockwise (was 0, 1, 5)
        self.mesh.add_triangle(0, 5, 1)   # Reorder for counterclockwise (was 0, 5, 4)

        # Right face
        self.mesh.add_triangle(2, 6, 7)   # Keep this order
        self.mesh.add_triangle(2, 7, 3)   # Reorder for counterclockwise (was 2, 7, 6)

        # Top face
        self.mesh.add_triangle(0, 3, 7)   # Keep this order
        self.mesh.add_triangle(0, 7, 4)   # Keep this order

        # Bottom face
        self.mesh.add_triangle(1, 5, 6)   # Reorder for counterclockwise (was 1, 2, 6)
        self.mesh.add_triangle(1, 6, 2)   # Reorder for counterclockwise (was 1, 6, 5)


        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_mouse_events(screen)

            if (self.is_cube_mode):
                self.display(screen, pygame.font.Font(None, 20), self.globalYaw, self.globalPitch, self.globalRoll)

            
            screen.fill((255, 255, 255))
            if self.is_wireframe:
                self.drawTriangles(screen)
            else:
                self.drawTrianglesSolid(screen)
            self.draw_axes(screen)
            pygame.display.flip()

if len(sys.argv) < 2:
        print("USAGE : TriangleMesh.py <rotationType> <options>\n"
              "\t <rotationType>\n"
              "\t\t -e : Euler Angles \n"
              "\t\t -r : Rotation Matrix \n"
              "\t\t -m : Exponential Map \n"
              "\t\t -q : Quaternions \n"
              "\t <options>\n"
              "\t\t -x : euler in extrinsic method\n"
              "\t\t -i : euler in intrinsic method\n")
        sys.exit()
    
isEulerAngles = '-e' in sys.argv
isRotationMatrix = '-r' in sys.argv
isExponentialMap = '-m' in sys.argv
isQuaternions = '-q' in sys.argv
isExtrinsic = '-x' in sys.argv
isIntrinsic = '-i' in sys.argv

drawTri = DrawTriangle()
drawTri.render()
