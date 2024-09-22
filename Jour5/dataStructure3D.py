import math

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
    
    def toString(self):
        tab = []
        s = ''
        for row in self.mat:
            s+='|'
            for col in row:
                s+= ' ' + str(col)
            s+=' |'
            tab.append(s)
            s = ''
        return tab
    
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

    def determinant2x2(self, a, b, c, d):
        return a * d - b * c

    def determinant3x3(self, mat3):
        return (mat3[0][0] * self.determinant2x2(mat3[1][1], mat3[1][2], mat3[2][1], mat3[2][2])
               - mat3[0][1] * self.determinant2x2(mat3[1][0], mat3[1][2], mat3[2][0], mat3[2][2])
               + mat3[0][2] * self.determinant2x2(mat3[1][0], mat3[1][1], mat3[2][0], mat3[2][1]))

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

    def determinant(self):
        det = 0
        for col in range(4):
            submat = self.submatrix3x3(0, col)
            cofactor = ((-1) ** col) * self.mat[0][col] * self.determinant3x3(submat)
            det += cofactor
        return det

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

class Quaternion:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def add(self, other):
        return Quaternion(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
    
    def multiply(self, other):
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)
    
    def div(self, scalar):
        return Quaternion(self.w / scalar, self.x / scalar, self.y / scalar, self.z / scalar)


    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self):
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        norm = self.norm()
        if norm == 0:
            return Quaternion(1, 0, 0, 0)  # Avoid division by zero, return identity quaternion
        self.w /= norm
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def inverse(self):
        return self.conjugate() / (self.norm() ** 2)

    def rotate_vector(self, v):
        q_v = Quaternion(0, v.x, v.y, v.z)
        q_conj = self.conjugate()
        q_result = self * q_v * q_conj
        return vec3(q_result.x, q_result.y, q_result.z)
    
    def to_rotation_matrix(self):
        xx = self.x * self.x
        yy = self.y * self.y
        zz = self.z * self.z
        xy = self.x * self.y
        xz = self.x * self.z
        yz = self.y * self.z
        wx = self.w * self.x
        wy = self.w * self.y
        wz = self.w * self.z

        return mat4(
            1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy), 0,
            2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx), 0,
            2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy), 0,
            0, 0, 0, 1
        )
        
    @staticmethod
    def from_axis_angle(axis, angle):
        half_angle = angle / 2
        sin_half_angle = math.sin(half_angle)
        return Quaternion(
            math.cos(half_angle),
            axis.x * sin_half_angle,
            axis.y * sin_half_angle,
            axis.z * sin_half_angle
        )
        
    def toString(self):
        return f"Quaternion: (w: {self.w:.2f}, x: {self.x:.2f}, y: {self.y:.2f}, z: {self.z:.2f})"

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

    def calculate_rotation(self, angleYaw, anglePitch, angleRoll):
        yaw_rad = math.radians(angleYaw)
        pitch_rad = math.radians(anglePitch)
        roll_rad = math.radians(angleRoll)
        roll_matrix = mat4(math.cos(roll_rad), -math.sin(roll_rad), 0, 0,
                           math.sin(roll_rad), math.cos(roll_rad), 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1)

        pitch_matrix = mat4(1, 0, 0, 0,
                            0, math.cos(pitch_rad), -math.sin(pitch_rad), 0,
                            0, math.sin(pitch_rad), math.cos(pitch_rad), 0,
                            0, 0, 0, 1)

        yaw_matrix = mat4(math.cos(yaw_rad), 0, math.sin(yaw_rad), 0,
                          0, 1, 0, 0,
                          -math.sin(yaw_rad), 0, math.cos(yaw_rad), 0,
                          0, 0, 0, 1)
        return roll_matrix.matrixMultiplication(pitch_matrix.matrixMultiplication(yaw_matrix))

    def scale(self, scaleFactor):
        scale_matrix = mat4(scaleFactor, 0, 0, 0,
                            0, scaleFactor, 0, 0,
                            0, 0, scaleFactor, 0,
                            0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(scale_matrix)

    def euler_intrinsic(self, yaw, pitch, roll):
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)
        roll_rad = math.radians(roll)

        roll_matrix = mat4(math.cos(roll_rad), -math.sin(roll_rad), 0, 0,
                           math.sin(roll_rad), math.cos(roll_rad), 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1)

        pitch_matrix = mat4(1, 0, 0, 0,
                            0, math.cos(pitch_rad), -math.sin(pitch_rad), 0,
                            0, math.sin(pitch_rad), math.cos(pitch_rad), 0,
                            0, 0, 0, 1)

        yaw_matrix = mat4(math.cos(yaw_rad), 0, math.sin(yaw_rad), 0,
                          0, 1, 0, 0,
                          -math.sin(yaw_rad), 0, math.cos(yaw_rad), 0,
                          0, 0, 0, 1)

        self.model_matrix = yaw_matrix.matrixMultiplication(pitch_matrix).matrixMultiplication(roll_matrix).matrixMultiplication(self.model_matrix)

    def euler_extrinsic(self, yaw, pitch, roll):
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)
        roll_rad = math.radians(roll)

        roll_matrix = mat4(math.cos(roll_rad), -math.sin(roll_rad), 0, 0,
                           math.sin(roll_rad), math.cos(roll_rad), 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1)

        pitch_matrix = mat4(1, 0, 0, 0,
                            0, math.cos(pitch_rad), -math.sin(pitch_rad), 0,
                            0, math.sin(pitch_rad), math.cos(pitch_rad), 0,
                            0, 0, 0, 1)

        yaw_matrix = mat4(math.cos(yaw_rad), 0, math.sin(yaw_rad), 0,
                          0, 1, 0, 0,
                          -math.sin(yaw_rad), 0, math.cos(yaw_rad), 0,
                          0, 0, 0, 1)

        self.model_matrix = self.model_matrix.matrixMultiplication(roll_matrix).matrixMultiplication(pitch_matrix).matrixMultiplication(yaw_matrix)
    
    def exponential_map(self, axis, angle):
        axis = axis.normalize()
        x, y, z = axis.x, axis.y, axis.z
        angle_rad = math.radians(angle)

        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        one_minus_cos_a = 1 - cos_a

        rotation_matrix = mat4(
            cos_a + x * x * one_minus_cos_a, x * y * one_minus_cos_a - z * sin_a, x * z * one_minus_cos_a + y * sin_a, 0,
            y * x * one_minus_cos_a + z * sin_a, cos_a + y * y * one_minus_cos_a, y * z * one_minus_cos_a - x * sin_a, 0,
            z * x * one_minus_cos_a - y * sin_a, z * y * one_minus_cos_a + x * sin_a, cos_a + z * z * one_minus_cos_a, 0,
            0, 0, 0, 1
        )

        self.model_matrix = self.model_matrix.matrixMultiplication(rotation_matrix)
    
    def exponential_mapFunction(self, axis, angle):
        axis = axis.normalize()
        x, y, z = axis.x, axis.y, axis.z
        angle_rad = math.radians(angle)

        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        one_minus_cos_a = 1 - cos_a

        rotation_matrix = mat4(
            cos_a + x * x * one_minus_cos_a, x * y * one_minus_cos_a - z * sin_a, x * z * one_minus_cos_a + y * sin_a, 0,
            y * x * one_minus_cos_a + z * sin_a, cos_a + y * y * one_minus_cos_a, y * z * one_minus_cos_a - x * sin_a, 0,
            z * x * one_minus_cos_a - y * sin_a, z * y * one_minus_cos_a + x * sin_a, cos_a + z * z * one_minus_cos_a, 0,
            0, 0, 0, 1
        )

        return rotation_matrix
    
    def translate(self, tx, ty, tz):
        translation_matrix = mat4(1, 0, 0, tx,
                                  0, 1, 0, ty,
                                  0, 0, 1, tz,
                                  0, 0, 0, 1)
        self.model_matrix = self.model_matrix.matrixMultiplication(translation_matrix)
        
    def yaw(self, angle):
        radian_angle = math.radians(angle)
        rotation_matrix = mat4(
            math.cos(radian_angle), 0, math.sin(radian_angle), 0,
            0,                      1,                      0, 0,
            -math.sin(radian_angle),0, math.cos(radian_angle), 0,
            0,                       0,                       0, 1
        )
        self.model_matrix = rotation_matrix.matrixMultiplication(self.model_matrix)

    def pitch(self, angle):
        # Créez une matrice de rotation autour de l'axe X (pitch)
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotation_matrix = mat4(
            1, 0, 0, 0,
            0, cos_a, -sin_a, 0,
            0, sin_a, cos_a, 0,
            0, 0, 0, 1
        )
        self.model_matrix = rotation_matrix.matrixMultiplication(self.model_matrix)

    def roll(self, angle):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotation_matrix = mat4(
            cos_a, -sin_a, 0, 0,
            sin_a, cos_a, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        )
        self.model_matrix = rotation_matrix.matrixMultiplication(self.model_matrix)
    

    def apply_transformation(self):
        for i in range(len(self.vertex)):
            self.vertex[i] = self.model_matrix.vectorMultiplication(self.vertex[i].hom()).toCartesian()

