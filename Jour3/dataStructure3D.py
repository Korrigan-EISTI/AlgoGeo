import math
import pygame
import sys

class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        norm = self.length()
        if norm == 0:
            return
        return vec3(self.x / norm, self.y / norm, self.z / norm)
    
    def neg(self):
        return vec3(-self.x, -self.y, -self.z)
    
    def mul(self, k):
        return vec3(self.x * k, self.y * k, self.z * k)
    
    def add(self, vec):
        return vec3(self.x + vec.x, self.y + vec.y, self.z + vec.z)
    
    def sub(self, vec):
        return vec3(self.x - vec.x, self.y - vec.y, self.z - vec.z)
    
    def dotProduct(self, vec):
        return (self.x * vec.x) + (self.y * vec.y) + (self.z * vec.z)
    
    def crossProduct(self, vec):
        return vec3((self.y * vec.z) - (self.z * vec.y), 
                    (self.z * vec.x) - (self.x * vec.z), 
                    (self.x * vec.y) - (self.y * vec.x))

    def show(self):
        print(f'({self.x}, {self.y}, {self.z})')

    def hom(self):
        return vec4(self.x, self.y, self.z, 1)

class vec4(vec3):
    def __init__(self, x, y, z, w):
        super().__init__(x, y, z)
        self.w = w
    
    def toCartesian(self):
        return vec3(self.x / self.w, self.y / self.w, self.z / self.w)
    
    def show(self):
        print(f'({self.x}, {self.y}, {self.z}, {self.w})')

class mat4:
    def __init__(self, 
                 m00, m01, m02, m03,
                 m10, m11, m12, m13,
                 m20, m21, m22, m23,
                 m30, m31, m32, m33):
        self.mat = [[m00, m01, m02, m03],
                    [m10, m11, m12, m13],
                    [m20, m21, m22, m23],
                    [m30, m31, m32, m33]]

    def show(self):
        print("Matrice:")
        for row in self.mat:
            print(row)
    
    def scalarMultiplication(self, k):
        return mat4(self.mat[0][0] * k, self.mat[0][1] * k, self.mat[0][2] * k, self.mat[0][3] * k,
                    self.mat[1][0] * k, self.mat[1][1] * k, self.mat[1][2] * k, self.mat[1][3] * k,
                    self.mat[2][0] * k, self.mat[2][1] * k, self.mat[2][2] * k, self.mat[2][3] * k,
                    self.mat[3][0] * k, self.mat[3][1] * k, self.mat[3][2] * k, self.mat[3][3] * k)
    
    def calculateComposante(self, i, j, mat):
        result  = (self.mat[i][0] * mat.mat[0][j])
        result += (self.mat[i][1] * mat.mat[1][j])
        result += (self.mat[i][2] * mat.mat[2][j])
        result += (self.mat[i][3] * mat.mat[3][j])
        return result
    
    def matrixMultiplication(self, mat):
        return mat4(self.calculateComposante(0, 0, mat), self.calculateComposante(0, 1, mat), self.calculateComposante(0, 2, mat), self.calculateComposante(0, 3, mat),
                    self.calculateComposante(1, 0, mat), self.calculateComposante(1, 1, mat), self.calculateComposante(1, 2, mat), self.calculateComposante(1, 3, mat),
                    self.calculateComposante(2, 0, mat), self.calculateComposante(2, 1, mat), self.calculateComposante(2, 2, mat), self.calculateComposante(2, 3, mat),
                    self.calculateComposante(3, 0, mat), self.calculateComposante(3, 1, mat), self.calculateComposante(3, 2, mat), self.calculateComposante(3, 3, mat))
    
    def calculateVectorComposante(self, i, vec):
        if (isinstance(vec, vec3)):
            vec = vec.hom()
        return (self.mat[i][0] * vec.x) + (self.mat[i][1] * vec.y) + (self.mat[i][2] * vec.z) + (self.mat[i][3] * vec.w)
        
    def vectorMultiplication(self, vec):
        return vec4(self.calculateVectorComposante(0, vec), self.calculateVectorComposante(1, vec), self.calculateVectorComposante(2, vec), self.calculateVectorComposante(3, vec))

    # Fonction pour calculer le déterminant d'une matrice 2x2
    def determinant2x2(self, a, b, c, d):
        return a * d - b * c

    # Fonction pour calculer le déterminant d'une matrice 3x3
    def determinant3x3(self, mat3):
        return (mat3[0][0] * self.determinant2x2(mat3[1][1], mat3[1][2], mat3[2][1], mat3[2][2])
               - mat3[0][1] * self.determinant2x2(mat3[1][0], mat3[1][2], mat3[2][0], mat3[2][2])
               + mat3[0][2] * self.determinant2x2(mat3[1][0], mat3[1][1], mat3[2][0], mat3[2][1]))

    # Fonction pour extraire une matrice 3x3 en retirant la ligne i et la colonne j
    def submatrix3x3(self, i, j):
        mat3 = []
        for row in range(4):
            if row == i:
                continue
            row_data = []
            for col in range(4):
                if col == j:
                    continue
                row_data.append(self.mat[row][col])
            mat3.append(row_data)
        return mat3

    # Fonction pour calculer le déterminant de la matrice 4x4
    def determinant(self):
        det = 0
        for col in range(4):
            # Extraction de la sous-matrice 3x3
            submat = self.submatrix3x3(0, col)
            # Calcul du cofacteur
            cofactor = ((-1) ** col) * self.mat[0][col] * self.determinant3x3(submat)
            # Ajout au déterminant
            det += cofactor
        return det

    # Calcul de la matrice inverse
    def inverse(self):
        det = self.determinant()
        if det == 0:
            print("La matrice n'est pas inversible")
            return None
        
        new_m00 =  self.determinant3x3(self.submatrix3x3(0, 0))
        new_m01 = -self.determinant3x3(self.submatrix3x3(0, 1))
        new_m02 =  self.determinant3x3(self.submatrix3x3(0, 2))
        new_m03 = -self.determinant3x3(self.submatrix3x3(0, 3))

        new_m10 = -self.determinant3x3(self.submatrix3x3(1, 0))
        new_m11 =  self.determinant3x3(self.submatrix3x3(1, 1))
        new_m12 = -self.determinant3x3(self.submatrix3x3(1, 2))
        new_m13 =  self.determinant3x3(self.submatrix3x3(1, 3))

        new_m20 =  self.determinant3x3(self.submatrix3x3(2, 0))
        new_m21 = -self.determinant3x3(self.submatrix3x3(2, 1))
        new_m22 =  self.determinant3x3(self.submatrix3x3(2, 2))
        new_m23 = -self.determinant3x3(self.submatrix3x3(2, 3))

        new_m30 = -self.determinant3x3(self.submatrix3x3(3, 0))
        new_m31 =  self.determinant3x3(self.submatrix3x3(3, 1))
        new_m32 = -self.determinant3x3(self.submatrix3x3(3, 2))
        new_m33 =  self.determinant3x3(self.submatrix3x3(3, 3))

        return mat4(new_m00, new_m01, new_m02, new_m03,
                    new_m10, new_m11, new_m12, new_m13,
                    new_m20, new_m21, new_m22, new_m23,
                    new_m30, new_m31, new_m32, new_m33).scalarMultiplication(1 / det)

import math

class TriangleMesh:
    def __init__(self):
        self.vertex = []
        self.index = []
        # Initialise la matrice de modèle comme une matrice identité
        self.model_matrix = mat4(1, 0, 0, 0,
                                 0, 1, 0, 0,
                                 0, 0, 1, 0,
                                 0, 0, 0, 1)

    def add_vertex(self, x, y, z):
        self.vertex.append(vec3(x, y, z))

    def add_triangle(self, v1, v2, v3):
        self.index.append((v1, v2, v3))

    def scale(self, scaleFactor):
        scale_matrix = mat4(scaleFactor, 0, 0, 0,
                            0, scaleFactor, 0, 0,
                            0, 0, scaleFactor, 0,
                            0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(scale_matrix)


    def pitch(self, angle):
        angle_rad = math.radians(angle)
        rotation_matrix = mat4(1, 0, 0, 0,
                               0, math.cos(angle_rad), -math.sin(angle_rad), 0,
                               0, math.sin(angle_rad), math.cos(angle_rad), 0,
                               0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(rotation_matrix)

    def yaw(self, angle):
        angle_rad = math.radians(angle)
        rotation_matrix = mat4(math.cos(angle_rad), 0, math.sin(angle_rad), 0,
                               0, 1, 0, 0,
                               -math.sin(angle_rad), 0, math.cos(angle_rad), 0,
                               0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(rotation_matrix)

    def roll(self, angle):
        angle_rad = math.radians(angle)
        rotation_matrix = mat4(math.cos(angle_rad), -math.sin(angle_rad), 0, 0,
                               math.sin(angle_rad), math.cos(angle_rad), 0, 0,
                               0, 0, 1, 0,
                               0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(rotation_matrix)
    
    def translate(self, tx, ty, tz):
        translation_matrix = mat4(1, 0, 0, tx,
                                  0, 1, 0, ty,
                                  0, 0, 1, tz,
                                  0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(translation_matrix)

    def apply_transformation(self):
        for i in range(len(self.vertex)):
            self.vertex[i] = self.model_matrix.vectorMultiplication(self.vertex[i].hom()).toCartesian()