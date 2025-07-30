import numpy as np
import functools
import math
from KUtils.Typing import *
from KUtils import KBuf, KDim


class Transform3D(KBuf[np.float32, KDim(4, 4)]):
    def __matmul__(self, other):
        res = np.array(self) @ np.array(other)
        if isinstance(other, Transform3D):
            return Transform3D(res)
        else:
            return res

    @property
    def rotation(self):
        return self.buf[:3, :3]

    @property
    def position(self):
        return self.buf[:3, 3]

    @property
    def mat(self) -> np.ndarray:
        return self.buf

    def __axis(self, col: int):
        axis = self.mat[:3, col]
        return axis / np.linalg.norm(axis)

    @functools.cached_property
    def x(self):
        return self.__axis(0)

    @functools.cached_property
    def y(self):
        return self.__axis(1)

    @functools.cached_property
    def z(self):
        return self.__axis(2)

    @functools.cached_property
    def translation(self):
        return self.buf[:3, 3]

    @functools.cached_property
    def rotation(self):
        return self.buf[:3, :3]

    @classmethod
    def TRS(cls,
            translation: np.ndarray | tuple | list = None,
            rotation: np.ndarray | tuple | list = None,
            euler: bool = True,
            degrees: bool = True,
            scale: np.ndarray | tuple | list = None) -> Self:
        if translation is None:
            translation = np.zeros(3)
        else:
            translation = np.array(translation)
        if rotation is None:
            rotation = np.zeros(3)
        else:
            rotation = np.array(rotation)
        if scale is None:
            scale = np.ones(3)
        else:
            scale = np.array(scale)

        # Create scaling matrix
        scale_matrix = np.eye(4)
        scale_matrix[:3, :3] = np.diag(scale)

        # Create rotation matrix
        if rotation.shape == (3, ):
            # Convert degrees to radians if needed
            if degrees:
                rotation = np.radians(rotation)
            # Create rotation matrix from Euler angles (using XYZ order)
            from scipy.spatial.transform import Rotation
            rot = Rotation.from_euler('xyz', rotation)
            rotation_matrix = np.eye(4)
            rotation_matrix[:3, :3] = rot.as_matrix()
        else:
            if rotation.shape == (3, 3) or rotation.shape == (4, 4):
                # Rotation matrix provided
                rotation_matrix = np.eye(4)
                rotation_matrix[:3, :3] = rotation[:3, :3]
            elif rotation.shape == (4,):
                # Quaternion provided
                from scipy.spatial.transform import Rotation
                rot = Rotation.from_quat(rotation)
                rotation_matrix = np.eye(4)
                rotation_matrix[:3, :3] = rot.as_matrix()
            else:
                raise ValueError("Invalid rotation input. Must be 3x3 matrix or 4D quaternion when euler=False")

        # Create translation matrix
        translation_matrix = np.eye(4)
        translation_matrix[:3, 3] = translation

        # Combine transformations: T * R * S
        transformation = translation_matrix @ rotation_matrix @ scale_matrix

        return cls(transformation)

    @classmethod
    def Euler(cls, x: float = 0, y: float = 0, z: float = 0, degrees: bool = True) -> Self:
        if degrees:
            x = math.radians(x)
            y = math.radians(y)
            z = math.radians(z)

            # Create individual rotation matrices
        cos_x, sin_x = math.cos(x), math.sin(x)
        cos_y, sin_y = math.cos(y), math.sin(y)
        cos_z, sin_z = math.cos(z), math.sin(z)

        # Rotation around X axis
        Rx = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Rotation around Y axis
        Ry = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Rotation around Z axis
        Rz = np.array([
            [cos_z, -sin_z, 0, 0],
            [sin_z, cos_z, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Combine rotations in ZYX order (common in 3D graphics)
        # rotation_matrix = Rz @ Ry @ Rx
        rotation_matrix = Rx @ Ry @ Rz

        return cls(rotation_matrix)

    def apply(self, target: np.ndarray):
        """
        应用当前变换矩阵到目标数组上

        参数:
            target: 要变换的目标数组，可以是:
                - 单个点(3D向量，形状为(3,))
                - 单个齐次点(4D向量，形状为(4,))
                - 点集(形状为(N,3)或(N,4))
                - 齐次坐标点集(形状为(4,N))

        返回:
            变换后的点/点集
        """
        target = np.array(target).copy()
        if target.ndim == 1:  # 单个点
            if target.shape[0] == 3:  # 非齐次坐标
                # 转换为齐次坐标，添加1作为第4个分量
                point = np.append(target, 1.0)
                transformed = self.buf @ point
                return transformed[:3]  # 返回非齐次坐标
            elif target.shape[0] == 4:  # 齐次坐标
                return self.buf @ target
            else:
                raise ValueError("目标点必须是3D或4D向量")

        elif target.ndim == 2:  # 点集
            if target.shape[1] == 3:  # (N,3)非齐次坐标
                # 转换为齐次坐标，添加一列1
                points = np.column_stack([target, np.ones(target.shape[0])])
                transformed = (self.buf @ points.T).T
                return transformed[:, :3]  # 返回非齐次坐标

            elif target.shape[0] == 3:  # (3,N)非齐次坐标
                # 转换为齐次坐标，添加一行1
                points = np.vstack([target, np.ones(target.shape[1])])
                transformed = self.buf @ points
                return transformed[:3, :]  # 返回非齐次坐标

            elif target.shape[1] == 4:  # (N,4)齐次坐标
                return (self.buf @ target.T).T

            elif target.shape[0] == 4:  # (4,N)齐次坐标
                return self.buf @ target

            else:
                raise ValueError("点集形状必须是(N,3), (N,4), (3,N)或(4,N)")

        else:
            raise ValueError("目标数组维度必须是1或2")

    def numpy(self):
        return self.buf

    def inv(self):
        return type(self)(np.linalg.inv(self.numpy()))
