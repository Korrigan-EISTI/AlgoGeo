import dataStructure3D
import math

class Scene:
    def __init__(self):
        self.view_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                0, 1, 0, 0,
                                0, 0, 1, 0,
                                0, 0, 0, 1)
        
        self.projection_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                      0, 1, 0, 0,
                                                      0, 0, 1, 0,
                                                      0, 0, 0, 1)
        
        self.viewport_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                                    0, 1, 0, 0,
                                                    0, 0, 1, 0,
                                                    0, 0, 0, 1)
    
    def set_view_matrix(self, matrix):
        self.view_matrix = matrix

    def set_projection_matrix(self, matrix):
        self.projection_matrix = matrix

    def set_viewport_matrix(self, matrix):
        self.viewport_matrix = matrix
    
    def apply_transformation(self, vec, mesh):
        modelViewMatrix = self.view_matrix.matrixMultiplication(mesh.model_matrix)
        transformation_mat = self.viewport_matrix.matrixMultiplication(self.projection_matrix.matrixMultiplication(modelViewMatrix)
        )
        transformed_vec = transformation_mat.vectorMultiplication(vec)
        return transformed_vec
    
    def setup_view_and_projection(self, w, h, n, far):
        # Définir la matrice de vue avec une translation sur Z
        view_matrix = dataStructure3D.mat4(1, 0, 0, 0,
                                           0, 1, 0, 0,
                                           0, 0, 1, -3,  # Translation sur Z
                                           0, 0, 0, 1)
        self.set_view_matrix(view_matrix)

        # Projection orthographique (ajustée pour centrer le rendu)
        left = -2
        right = 2
        bottom = -2
        top = 2
        near = n
        far = far
        projection_matrix = dataStructure3D.mat4(2 / (right - left), 0, 0, - (right + left) / (right - left),
                                                 0, 2 / (top - bottom), 0, - (top + bottom) / (top - bottom),
                                                 0, 0, -2 / (far - near), - (far + near) / (far - near),
                                                 0, 0, 0, 1)
        self.set_projection_matrix(projection_matrix)

        # Correction de la matrice de viewport pour bien centrer (0, 0)
        viewport_matrix = dataStructure3D.mat4(
            w / 2, 0, 0, w / 2,    # Centre X avec décalage de moitié de la largeur
            0, -h / 2, 0, h / 2,   # Centre Y avec inversion pour la fenêtre
            0, 0, 1, 0,            # Z inchangé
            0, 0, 0, 1
        )
        self.set_viewport_matrix(viewport_matrix)
