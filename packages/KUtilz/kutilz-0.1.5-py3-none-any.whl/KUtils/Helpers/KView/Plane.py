import numpy as np

from .Object3D import *

class Plane(Object3D):
    @classmethod
    def FromTriangle(cls, p0, p1, p2):
        # Calculate two vectors in the plane
        v1 = p1 - p0
        v2 = p2 - p0

        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)  # Normalize

        # Calculate d (distance from origin) using any of the points
        d = -np.dot(normal, p0)

        return cls(normal, d)

    @classmethod
    def FromNormalAndSomePoint(cls, normal: np.ndarray, point: np.ndarray) -> Self:
        normal = np.array(normal)
        point = np.array(point)
        d = -np.dot(normal, point)
        return cls(normal, d)

    def __init__(self, normal: np.ndarray, d: float = None):
        self.normal = np.array(normal).reshape(3)
        self.d = d
        super().__init__()

    def __project_point__(self, pt: np.ndarray, reduce_dim: bool = True) -> np.ndarray:
        raise NotImplementedError()

    def __dist_point__(self, pt: np.ndarray, signed: bool = True) -> float:
        """
        Calculate the distance from a point to the plane.

        Args:
            pt: The point coordinates as a numpy array (x, y, z)
            signed: If True, returns signed distance (positive if point is on the same side as normal)
                   If False, returns absolute distance

        Returns:
            The distance from the point to the plane
        """
        # Calculate the numerator: Ax + By + Cz + D
        # For our plane representation (normal, d), the equation is:
        # normal.x * x + normal.y * y + normal.z * z + d = 0
        numerator = np.dot(self.normal, pt) + self.d

        if not signed:
            numerator = abs(numerator)

        # The denominator is the magnitude of the normal vector (which is 1 since we normalized it)
        # So we can skip the division for efficiency
        return numerator

    @property
    def origin(self):
        return -self.d * self.normal

    def rendered_mesh(self):
        size = 10
        thickness = .2

        if self.d is None:
            raise ValueError("Plane offset (d) must be provided for positioning")

        # Create thin box aligned with XY plane
        box = trimesh.creation.box(extents=[size * 2, size * 2, thickness])

        # Calculate plane position from normal/d parameters
        origin = self.origin

        # Create transformation matrix
        rotation = trimesh.geometry.align_vectors([0, 0, 1], self.normal)
        transform = np.eye(4)
        transform[:3, :3] = rotation[:3, :3]
        transform[:3, 3] = origin

        # Apply transformation to box
        box.apply_transform(transform)

        return box