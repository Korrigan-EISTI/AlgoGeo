import scene
import dataStructure3D
import pygame
import sys
import math

class DrawTriangle:
    def __init__(self):
        self.scene = scene.Scene()
        self.mesh = dataStructure3D.TriangleMesh()
        self.yaw = 0
        self.pitch = 0
        self.roll = 0

        self.isIncrementedYaw = False
        self.isIncrementedPitch = False
        self.isIncrementedRoll = False

        self.isLerping = False
        self.lerp_t = 0
        self.lerp_type = None  # 'euler' or 'exponential'

        self.initial_yaw = 0
        self.initial_pitch = 0
        self.initial_roll = 0
        self.initial_axis = dataStructure3D.vec3(1, 0, 0)
        self.initial_angle = 0

        self.globalYaw = 0
        self.globalPitch = 0
        self.globalRoll = 0

    def drawTriangles(self, screen):
        for idx1, idx2, idx3 in self.mesh.index:
            points = [self.scene.apply_transformation(self.mesh.vertex[idx1], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx2], self.mesh), 
                      self.scene.apply_transformation(self.mesh.vertex[idx3], self.mesh)]

            pygame.draw.line(screen, (0, 0, 0), (int(points[0].x), int(points[0].y)), (int(points[1].x), int(points[1].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[1].x), int(points[1].y)), (int(points[2].x), int(points[2].y)), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(points[2].x), int(points[2].y)), (int(points[0].x), int(points[0].y)), 2)

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

    def goBackInInitialState(self, iterations, screen, isExponential=False):
        if iterations == 0:
            return

        font = pygame.font.Font(None, 20)
        # Calcul des angles de rotation par étape
        theta_yaw = self.globalYaw / iterations
        theta_pitch = self.globalPitch / iterations
        theta_roll = self.globalRoll / iterations

        print(f"Yaw: {theta_yaw}, Pitch: {theta_pitch}, Roll: {theta_roll}")

        for i in range(1, iterations + 1):
            screen.fill((255, 255, 255))
            current_yaw = self.globalYaw - theta_yaw * float(i)
            current_pitch = self.globalPitch - theta_pitch * float(i)
            current_roll = self.globalRoll - theta_roll * float(i)

            self.display(screen, font, current_yaw, current_pitch, current_roll)

            print(f"Step {i}/{iterations} -> Yaw: {current_yaw}, Pitch: {current_pitch}, Roll: {current_roll}")

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


    def handle_mouse_events(self, isEulerAngles, isRotationMatrix, isExponentialMap, isQuaternions, isExtrinsic, isIntrinsic, screen):
        mouse_buttons = pygame.mouse.get_pressed()
        key_pressed = pygame.key.get_pressed()
        
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

        if key_pressed[pygame.K_c]:
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

    def render(self, isEulerAngles, isRotationMatrix, isExponentialMap, isQuaternions, isExtrinsic, isIntrinsic):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        self.scene.setup_view_and_projection(800, 600, 0.1, 1000)
        pygame.display.set_caption("Affichage 3D Cube")

        font = pygame.font.Font(None, 20)

        self.mesh.add_vertex(-1, -1, -1)
        self.mesh.add_vertex(1, -1, -1)
        self.mesh.add_vertex(1, 1, -1)
        self.mesh.add_vertex(-1, 1, -1)
        self.mesh.add_vertex(-1, -1, 1)
        self.mesh.add_vertex(1, -1, 1)
        self.mesh.add_vertex(1, 1, 1)
        self.mesh.add_vertex(-1, 1, 1)
        
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

            self.handle_mouse_events(isEulerAngles, isRotationMatrix, isExponentialMap, isQuaternions, isExtrinsic, isIntrinsic, screen)
            
            screen.fill((255, 255, 255))
            self.drawTriangles(screen)

            self.display(screen, font, self.globalYaw, self.globalPitch, self.globalRoll)
            

            # Display Rotation Matrix (if needed)
            # Example: You could extract the matrix from `self.mesh` and display it
            # Assuming you have a method to get the rotation matrix from the mesh
            # rotation_matrix = self.mesh.get_rotation_matrix()
            # Display the matrix elements as text (This is just a template)
            # for i, row in enumerate(rotation_matrix):
            #     row_text = f"{row[0]:.2f} {row[1]:.2f} {row[2]:.2f}"
            #     row_surface = font.render(row_text, True, (0, 0, 0))
            #     screen.blit(row_surface, (10, 50 + i * 30))  # Adjust position as needed

            pygame.display.flip()

def main():
    if len(sys.argv) < 2:
        print("USAGE : TriangleMesh.py <rotationType> <options>\n"
              "\t <rotationType>"
              "\t\t -e : Euler Angles"
              "\t\t -r : Rotation Matrix"
              "\t\t -m : Exponential Map"
              "\t\t -q : Quaternions"
              "\t <options>"
              "\t\t -x : euler in extrinsic method"
              "\t\t -i : euler in intrinsic method")
        sys.exit()
    
    isEulerAngles = '-e' in sys.argv
    isRotationMatrix = '-r' in sys.argv
    isExponentialMap = '-m' in sys.argv
    isQuaternions = '-q' in sys.argv
    isExtrinsic = '-x' in sys.argv
    isIntrinsic = '-i' in sys.argv

    drawTri = DrawTriangle()
    drawTri.render(isEulerAngles, isRotationMatrix, isExponentialMap, isQuaternions, isExtrinsic, isIntrinsic)

if __name__ == '__main__':
    main()
