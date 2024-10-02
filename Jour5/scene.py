import dataStructure3D
import math
from light import Light

class Scene:
    def __init__(self):
        self.cameraMatrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                 0, 1, 0, 0,
                                                 0, 0, 1, 0,
                                                 0, 0, 0, 1)
        self.view_matrix = self.cameraMatrix.inverse()
        self.projection_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                      0, 1, 0, 0,
                                                      0, 0, 1, 0,
                                                      0, 0, 0, 1)
        self.viewport_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                    0, 1, 0, 0,
                                                    0, 0, 1, 0,
                                                    0, 0, 0, 1)
        self.is_orthographic = True
        self.camera_position = dataStructure3D.vec4(0, 0, -10, 1)
        self.camera_rotation = dataStructure3D.vec4(0, 0, 0, 1)  # Yaw, Pitch, Roll
        self.light = Light(dataStructure3D.vec4(0, 0, -25, 0.7), 1)

    def set_view_matrix(self, matrix):
        self.view_matrix = matrix

    def set_projection_matrix(self, matrix):
        self.projection_matrix = matrix

    def set_viewport_matrix(self, matrix):
        self.viewport_matrix = matrix

    def set_projection_orthographic(self, w, h, n, far):
        left = -2
        right = 2
        bottom = -2
        top = 2
        near = n
        far = far
        projection_matrix = dataStructure3D.mat4(
            2 / (right - left), 0, 0, -(right + left) / (right - left),
            0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom),
            0, 0, -2 / (far - near), -(far + near) / (far - near),
            0, 0, 0, 1
        )
        self.set_projection_matrix(projection_matrix)

    def set_projection_perspective(self, w, h, n, far):
        fov = 60  # Field of View in degrees
        aspect = w / h
        top = n * math.tan(math.radians(fov) / 2)
        bottom = -top
        right = top * aspect
        left = -right
        projection_matrix = dataStructure3D.mat4(
            2 * n / (right - left), 0, 0, 0,
            0, 2 * n / (top - bottom), 0, 0,
            0, 0, -(far + n) / (far - n), -2 * far * n / (far - n),
            0, 0, -1, 0
        )
        self.set_projection_matrix(projection_matrix)

    def apply_transformation(self, vec, mesh):
        modelViewMatrix = self.view_matrix.matrixMultiplication(mesh.model_matrix)
        transformation_mat = self.viewport_matrix.matrixMultiplication(
            self.projection_matrix.matrixMultiplication(modelViewMatrix)
        )
        transformed_vec = transformation_mat.vectorMultiplication(vec)

        if not self.is_orthographic and transformed_vec.w != 0:
            transformed_vec.x /= transformed_vec.w
            transformed_vec.y /= transformed_vec.w
            transformed_vec.z /= transformed_vec.w

        return transformed_vec

    def setup_view_and_projection(self, w, h, n, far):
        # Default camera setup (initially looking at -Z direction)
        view_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                           0, 1, 0, 0,
                                           0, 0, 1, -10,
                                           0, 0, 0, 1)
        self.set_view_matrix(view_matrix)
        self.cameraMatrix = view_matrix.inverse()

        # Set projection mode based on orthographic or perspective flag
        if self.is_orthographic:
            self.set_projection_orthographic(w, h, n, far)
        else:
            self.set_projection_perspective(w, h, n, far)

        viewport_matrix = dataStructure3D.mat4(
            w / 2, 0, 0, w / 2,
            0, -h / 2, 0, h / 2,
            0, 0, 1, 0,
            0, 0, 0, 1
        )
        self.set_viewport_matrix(viewport_matrix)
        
    def screen_to_world_direction(self, screen_x, screen_y):
        # 1. Conversion des coordonnées de la souris en coordonnées normalisées de l'écran (NDC)
        normalized_x = (2.0 * screen_x) / 800 - 1.0  # Largeur de l'écran de 800
        normalized_y = 1.0 - (2.0 * screen_y) / 600  # Hauteur de l'écran de 600

        # Cas de la projection orthographique
        if self.is_orthographic:
            # La position du rayon est obtenue par projection dans l'espace monde (sur le plan de projection)
            ray_origin = dataStructure3D.vec4(normalized_x, normalized_y, 0, 1)
            
            # La direction du rayon est constante, généralement vers l'avant (négatif sur l'axe Z)
            ray_direction = dataStructure3D.vec3(0, 0, -1).normalize()
            
            # Inverser la matrice de vue pour obtenir la position de départ dans l'espace monde
            ray_origin_world = self.view_matrix.inverse().vectorMultiplication(ray_origin)
            return ray_origin_world, ray_direction  # Retourner l'origine et la direction du rayon

        # Cas de la projection perspective
        else:
            # 2. Création du rayon en coordonnées de clip space (NDC avec z = -1 pour les rayons vers l'avant)
            ray_clip = dataStructure3D.vec4(normalized_x, normalized_y, -1.0, 1.0)

            # 3. Transformation inverse de la matrice de projection pour obtenir les coordonnées dans l'espace de vue
            ray_eye = self.projection_matrix.inverse().vectorMultiplication(ray_clip)
            ray_eye = dataStructure3D.vec4(ray_eye.x, ray_eye.y, -1.0, 0.0)  # Mettre z = -1 et w = 0 pour un rayon

            # 4. Transformation inverse de la matrice de vue pour obtenir la direction dans l'espace monde
            ray_world = self.view_matrix.inverse().vectorMultiplication(ray_eye)

            # 5. Créer un vecteur direction dans l'espace monde et le normaliser
            ray_world_dir = dataStructure3D.vec3(ray_world.x, ray_world.y, ray_world.z).normalize()

            # La position du rayon en perspective part de la caméra
            ray_origin = dataStructure3D.vec4(self.cameraMatrix.mat[0][3], self.cameraMatrix.mat[1][3], self.cameraMatrix.mat[2][3], self.cameraMatrix.mat[3][3])

            return ray_origin, ray_world_dir  # Retourner l'origine et la direction du rayon


    def rotate_camera(self, yaw, pitch):
        # Apply yaw (rotation around Y-axis) and pitch (rotation around X-axis) to the camera
        yaw_matrix = dataStructure3D.mat4(
            math.cos(math.radians(yaw)), 0, math.sin(math.radians(yaw)), 0,
            0, 1, 0, 0,
            -math.sin(math.radians(yaw)), 0, math.cos(math.radians(yaw)), 0,
            0, 0, 0, 1
        )
        pitch_matrix = dataStructure3D.mat4(
            1, 0, 0, 0,
            0, math.cos(math.radians(pitch)), -math.sin(math.radians(pitch)), 0,
            0, math.sin(math.radians(pitch)), math.cos(math.radians(pitch)), 0,
            0, 0, 0, 1
        )

        # Combine yaw and pitch and apply to the view matrix
        rotation_matrix = yaw_matrix.matrixMultiplication(pitch_matrix)
        self.view_matrix = rotation_matrix.matrixMultiplication(self.view_matrix)
        self.cameraMatrix = self.view_matrix.inverse()

    def translate_camera(self, tx, ty, tz):
        # Apply translation to the camera position
        translation_matrix = dataStructure3D.mat4(
            1, 0, 0, tx,
            0, 1, 0, ty,
            0, 0, 1, tz,
            0, 0, 0, 1
        )

        # Update the view matrix
        self.view_matrix = translation_matrix.matrixMultiplication(self.view_matrix)
        self.cameraMatrix = self.view_matrix.inverse()
