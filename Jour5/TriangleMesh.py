import pygame
import sys
import dataStructure3D
import scene
import math

def euler_to_quaternion(yaw, pitch, roll):
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)
    qx = dataStructure3D.Quaternion.from_axis_angle(dataStructure3D.vec3(1, 0, 0), pitch_rad)
    qy = dataStructure3D.Quaternion.from_axis_angle(dataStructure3D.vec3(0, 1, 0), yaw_rad)
    qz = dataStructure3D.Quaternion.from_axis_angle(dataStructure3D.vec3(0, 0, 1), roll_rad)
    return qy.multiply(qx).multiply(qz)

def matrix_to_euler(matrix):
    yaw = math.atan2(matrix.mat[1][0], matrix.mat[0][0])
    pitch = math.asin(-matrix.mat[2][0])
    roll = math.atan2(matrix.mat[2][1], matrix.mat[2][2])
    return math.degrees(yaw), math.degrees(pitch), math.degrees(roll)

def quaternion_to_matrix(quat):
    return quat.to_rotation_matrix()

# Slerp function for quaternions
def quaternion_slerp(q1, q2, t):
    dot_product = q1.dot(q2)
    
    # If the dot product is negative, invert one quaternion to take the shorter path
    if dot_product < 0.0:
        q2 = q2.negate()
        dot_product = -dot_product

    if dot_product > 0.9995:  # Close enough to linear interpolation
        result = q1.add(q2.sub(q1).mul(t)).normalize()
    else:
        theta_0 = math.acos(dot_product)  # theta_0 is the angle between the input quaternions
        theta = theta_0 * t               # theta is the angle at the interpolated point
        sin_theta = math.sin(theta)       # compute the sine of theta
        sin_theta_0 = math.sin(theta_0)   # compute the sine of theta_0

        s1 = math.sin((1.0 - t) * theta_0) / sin_theta_0
        s2 = sin_theta / sin_theta_0

        result = q1.mul(s1).add(q2.mul(s2))
    
    return result.normalize()

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
        
        self.current_quaternion = dataStructure3D.Quaternion(1, 0, 0, 0)  # Identity quaternion
        # To store the display data
        self.euler_angles_text = ""
        self.exp_map_text_yaw = ""
        self.exp_map_text_pitch = ""
        self.exp_map_text_roll = ""
        self.quaternion_text = ""
        
        self.intersected_triangle = None  # Store the intersected triangle

    def update_display_data(self):
        # Exponential map (axis * angle)
        axis_yaw = dataStructure3D.vec3(0, 1, 0)
        axis_pitch = dataStructure3D.vec3(1, 0, 0)
        axis_roll = dataStructure3D.vec3(0, 0, 1)

        # Exponential map angles
        yaw_angle = self.globalYaw  # En degrés
        pitch_angle = self.globalPitch  # En degrés
        roll_angle = self.globalRoll  # En degrés

        # Afficher les angles et les axes associés
        self.exp_map_text_yaw = (f"ExpMap Yaw: Axis ({axis_yaw.x}, {axis_yaw.y}, {axis_yaw.z}), Angle: {yaw_angle:.2f}°")
        self.exp_map_text_pitch = (f"ExpMap Pitch: Axis ({axis_pitch.x}, {axis_pitch.y}, {axis_pitch.z}), Angle: {pitch_angle:.2f}°")
        self.exp_map_text_roll = (f"ExpMap Roll: Axis ({axis_roll.x}, {axis_roll.y}, {axis_roll.z}), Angle: {roll_angle:.2f}°")

        # Calculer les quaternions et afficher
        self.current_quaternion = euler_to_quaternion(self.globalYaw, self.globalPitch, self.globalRoll)
        self.quaternion_text = f"Quaternion: {self.current_quaternion.toString()}"

        # Calculer la matrice de rotation et afficher
        rotation_matrix = self.mesh.calculate_rotation(self.globalYaw, self.globalPitch, self.globalRoll)
        matrix_str = '\n'.join(rotation_matrix.toString())
        self.rotation_matrix_text = f"Rotation Matrix:\n{matrix_str}"

        # Afficher les angles d'Euler
        self.euler_angles_text = f"Yaw: {self.globalYaw:.2f}°, Pitch: {self.globalPitch:.2f}°, Roll: {self.globalRoll:.2f}°"

    def display_rotation_data(self, screen, font):
        y_offset = 0
        text_surface = font.render(self.euler_angles_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20

        text_surface = font.render(self.exp_map_text_yaw, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        
        text_surface = font.render(self.exp_map_text_pitch, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20
        
        text_surface = font.render(self.exp_map_text_roll, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20

        text_surface = font.render(self.quaternion_text, True, (0, 0, 0))
        screen.blit(text_surface, (20, y_offset))
        y_offset += 20

        # Afficher la matrice de rotation
        for line in self.rotation_matrix_text.split('\n'):
            text_surface = font.render(line, True, (0, 0, 0))
            screen.blit(text_surface, (20, y_offset))
            y_offset += 20


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

            if self.intersected_triangle == (idx1, idx2, idx3):
                color = (0, 0, 255)  # Highlight the intersected triangle with blue color
            else:
                lighting_intensity = self.scene.light.compute_diffuse_light(normal, vertex1)
                color = (min(255, int(255 * lighting_intensity)), 0, 0)  # Regular red shading for others
            
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

            # Calcul des angles actuels en fonction de l'itération
            current_yaw = self.globalYaw - theta_yaw * i
            current_pitch = self.globalPitch - theta_pitch * i
            current_roll = self.globalRoll - theta_roll * i

            # Conversion des angles actuels en radians
            current_yaw_rad = math.radians(current_yaw)
            current_pitch_rad = math.radians(current_pitch)
            current_roll_rad = math.radians(current_roll)

            self.display_rotation_data(screen, font)

            if not isExponential:
                # Matrices de rotation avec angles d'Euler
                yaw_matrix = self.mesh.calculate_rotation(current_yaw, current_pitch, current_roll)
                self.mesh.model_matrix = yaw_matrix
            elif isEulerAngles:
                # Rotation en utilisant la carte exponentielle
                axis_yaw = dataStructure3D.vec3(0, 1, 0)
                axis_pitch = dataStructure3D.vec3(1, 0, 0)
                axis_roll = dataStructure3D.vec3(0, 0, 1)

                matrix_yaw = self.mesh.exponential_mapFunction(axis_yaw, math.degrees(current_yaw_rad))
                matrix_pitch = self.mesh.exponential_mapFunction(axis_pitch, math.degrees(current_pitch_rad))
                matrix_roll = self.mesh.exponential_mapFunction(axis_roll, math.degrees(current_roll_rad))

                # Combinaison des matrices de rotation exponentielle
                self.mesh.model_matrix = matrix_roll.matrixMultiplication(matrix_pitch).matrixMultiplication(matrix_yaw)
            elif isQuaternions:
                t = i / iterations
                interpolated_quat = quaternion_slerp(self.end_quaternion, self.start_quaternion, t)
                self.mesh.model_matrix = interpolated_quat.to_rotation_matrix()

            # Dessiner les triangles à chaque étape
            self.drawTriangles(screen)
            pygame.display.flip()

            # Attendre un peu pour l'effet visuel
            pygame.time.wait(5)

        # Réinitialisation des angles globaux après la transition
        self.globalYaw, self.globalPitch, self.globalRoll = 0, 0, 0
        self.yaw, self.pitch, self.roll = 0, 0, 0

    def throw_ray(self, mouse_x, mouse_y):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        ndc_x = (2.0 * mouse_x) / screen_width - 1.0
        ndc_y = 1.0 - (2.0 * mouse_y) / screen_height
        
        ray_clip = dataStructure3D.vec4(ndc_x, ndc_y, -1.0, 1.0)
        ray_far_clip = dataStructure3D.vec4(ndc_x, ndc_y, 1.0, 1.0)

        viewport_inverse = self.scene.viewport_matrix.inverse()
        inverse_projection = self.scene.projection_matrix.inverse()
        inverse_view = self.scene.view_matrix.inverse()
        
        ray_eye = (inverse_projection.matrixMultiplication(viewport_inverse)).vectorMultiplication(ray_clip)
        ray_eye_far = (inverse_projection.matrixMultiplication(viewport_inverse)).vectorMultiplication(ray_far_clip)

        ray_eye.z = -1.0
        ray_eye.w = 0.0
        ray_eye_far.z = 1.0
        ray_eye_far.w = 0.0

        ray_world = inverse_view.vectorMultiplication(ray_eye)
        ray_world_far = inverse_view.vectorMultiplication(ray_eye_far)
        ray_direction = ray_world_far.sub(ray_world).normalize()

        closest_intersection = None
        self.closest_distance = float('inf')  # Reset the closest distance
        self.intersected_triangle = None  # Reset intersected triangle
        
        for idx1, idx2, idx3 in self.mesh.index:
            v1 = self.mesh.vertex[idx1]
            v2 = self.mesh.vertex[idx2]
            v3 = self.mesh.vertex[idx3]

            # Check intersection
            intersection, distance = self.ray_intersects_plane(ray_world, ray_direction, v1, v2, v3)

            # Update the closest triangle if it's closer than the previously found one
            if intersection and distance < self.closest_distance:
                closest_intersection = intersection
                self.closest_distance = distance
                self.intersected_triangle = (idx1, idx2, idx3)  
                
        return closest_intersection

    def ray_intersects_plane(self, ray_origin, ray_direction, v1, v2, v3):
        edge1 = v2.sub(v1)
        edge2 = v3.sub(v1)
        normal = edge1.crossProduct(edge2).normalize()

        denominator = normal.dotProduct(ray_direction)
        if abs(denominator) < 1e-6:  # Loosen precision check
            return None, None  # Ray is parallel to the plane

        d = normal.dotProduct(v1)
        t = (d - normal.dotProduct(ray_origin)) / denominator

        if t < 0:
            return None, None  # The intersection is behind the ray origin

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

        # Only rotate when cube mode is enabled and mouse buttons are pressed
        if self.is_cube_mode:
            if mouse_buttons[0]:  # Rotate around Yaw
                self.yaw = 0.1
                self.globalYaw += 0.1
            else:
                self.yaw = 0

            if mouse_buttons[1]:  # Rotate around Pitch
                self.pitch = 0.1
                self.globalPitch += 0.1
            else:
                self.pitch = 0

            if mouse_buttons[2]:  # Rotate around Roll
                self.roll = 0.1
                self.globalRoll += 0.1
            else:
                self.roll = 0

            if keys[pygame.K_c]:
                self.goBackInInitialState(100, screen, isExponentialMap)

            # Apply Euler or Exponential Map rotations conditionally
            if isEulerAngles:
                if isIntrinsic:
                    self.mesh.euler_intrinsic(self.yaw, self.pitch, self.roll)
                if isExtrinsic:
                    self.mesh.euler_extrinsic(self.yaw, self.pitch, self.roll)

            if isExponentialMap:
                if self.yaw != 0:
                    self.mesh.exponential_map(dataStructure3D.vec3(0, 1, 0), self.yaw)
                if self.pitch != 0:
                    self.mesh.exponential_map(dataStructure3D.vec3(1, 0, 0), self.pitch)
                if self.roll != 0:
                    self.mesh.exponential_map(dataStructure3D.vec3(0, 0, 1), self.roll)

            if isQuaternions:
                if self.yaw != 0 or self.pitch != 0 or self.roll != 0:
                    # Update quaternion incrementally
                    delta_quaternion = euler_to_quaternion(self.yaw, self.pitch, self.roll)
                    self.current_quaternion = delta_quaternion.multiply(self.current_quaternion)
                    self.current_quaternion.normalize()
                    self.mesh.model_matrix = self.current_quaternion.to_rotation_matrix()
        else:
            # If not in cube mode, handle camera movements with mouse and keys
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
            self.throw_ray(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])



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

        font = pygame.font.Font(None, 20)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_mouse_events(screen)

            screen.fill((255, 255, 255))
            if self.is_wireframe:
                self.drawTriangles(screen)
            else:
                self.drawTrianglesSolid(screen)
            self.draw_axes(screen)
            
            self.update_display_data()
            self.display_rotation_data(screen, font)
            
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
