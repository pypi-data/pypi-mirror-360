import math

import numpy as np
import trimesh
import open3d as o3d

from .Object3D import *

class PointCloud(Object3D):
    def __init__(self,
                 vertices: np.ndarray):
        super().__init__(
            trimesh.PointCloud(vertices=vertices.reshape(-1, 3))
        )

class Ball(Object3D):
    def __init__(self,
                 centre: np.ndarray,
                 radius: float = 1):
        super().__init__(
            trimesh.creation.uv_sphere(
                radius=radius,
                transform=Transform3D.TRS(translation=centre)
            )
        )

Point = Ball

class ParametricLine(Object3D):
    def __init__(self, start: np.ndarray, direction: np.ndarray):
        self.start = start
        self.direction = direction
        super().__init__()

    def sample(self, d: float = 2):
        return np.array([
            self.start,
            self.start + self.direction * d
        ])

class Line(Object3D):
    @classmethod
    def FromDirectionAndLength(cls, start: np.ndarray, direction: np.ndarray, length: float) -> Self:
        # Normalize the direction vector
        direction_normalized = direction / np.linalg.norm(direction)
        # Calculate end point by moving `length` units along the direction from `start`
        end = start + direction_normalized * length
        # Return a new Line instance
        return cls(start, end)

    @classmethod
    def Parametric(cls, start, direction, d) -> Self:
        direction_normalized = direction / np.linalg.norm(direction)
        # Calculate end point by moving `length` units along the direction from `start`
        end = start + direction_normalized * d
        # Return a new Line instance
        return cls(start, end)

    def rendered_mesh(self):
        import trimesh.path
        from trimesh.path.entities import Line
        vertices = np.array([self.start, self.end]).reshape(2, 3)
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("`self._joints` must be an (N, 3) array of XYZ points")

        if len(vertices) < 2:
            raise ValueError("Need at least two joints to form a segment")

        # 2.  One Line entity per consecutive pair of points
        entities = [Line([0, 1])]
        colors = [self.vparams.color for _ in entities]
        # 3.  Build the path
        path = trimesh.path.Path3D(entities=entities,
                                   vertices=vertices,
                                   colors=colors)


        return path


    def __init__(self, start: np.ndarray | tuple | list, end: np.ndarray | tuple | list):
        self.start = np.array(start).reshape(1, 3)
        self.end = np.array(end).reshape(1, 3)
        super().__init__()

    def __dist_point__(self, point: np.ndarray, vec: bool = True) -> np.ndarray:

        v = np.array(self.end - self.start).reshape(3)
        w = np.array(point - self.start).reshape(3)

        _vec = None

        c1 = np.dot(w, v)
        if c1 <= 0:  # Before start point
            _vec = point - self.start

        c2 = np.dot(v, v)
        if c2 <= c1:  # After end point
            _vec = point - self.end

        # Projection falls on the segment
        _vec = w - (c1 / c2) * v

        if vec:
            return _vec
        else:
            return np.linalg.norm(_vec)

class Polyline(Object3D):
    def __init__(self, vertices: np.ndarray):
        self._joints = vertices
        super().__init__()

    def rendered_mesh(self):
        import trimesh.path
        from trimesh.path.entities import Line
        vertices = np.asarray(self._joints, dtype=float)
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("`self._joints` must be an (N, 3) array of XYZ points")

        if len(vertices) < 2:
            raise ValueError("Need at least two joints to form a segment")

        # 2.  One Line entity per consecutive pair of points
        entities = [Line([i, i + 1]) for i in range(len(vertices) - 1)]
        colors = [self.vparams.color for _ in entities]
        # 3.  Build the path
        path = trimesh.path.Path3D(entities=entities,
                                   vertices=vertices,
                                   colors=colors)


        return path

    def segments(self) -> Iterable[Line]:
        for i in range(len(self._joints) - 1):
            yield Line(self._joints[i], self._joints[i+1])

    def length(self):
        total_ = 0.0
        len_ = len(self._joints)

        for i_a, i_b in [(i, i+1) for i in range(0, len_ - 1)]:
            a = self._joints[i_a]
            b = self._joints[i_b]

            total_ += np.linalg.norm(b - a)

        return total_

    def extended(self, length: int = 100) -> Self:
        if len(self._joints) < 2:
            return self  # Can't extend if there's only one point

        # Get direction vectors for first and last segments
        first_segment_dir = self._joints[1] - self._joints[0]
        last_segment_dir = self._joints[-1] - self._joints[-2]

        # Normalize direction vectors
        first_segment_dir = first_segment_dir / np.linalg.norm(first_segment_dir)
        last_segment_dir = last_segment_dir / np.linalg.norm(last_segment_dir)

        # Calculate new endpoints
        new_first_point = self._joints[0] - first_segment_dir * length
        new_last_point = self._joints[-1] + last_segment_dir * length

        # Create new vertices array with extended points
        extended_vertices = np.vstack([
            [new_first_point],
            self._joints,
            [new_last_point]
        ])

        return Polyline(extended_vertices)

    def __dist_point__(self, point: np.ndarray, vec: bool = True) -> np.ndarray:

        vecs = [segment.__dist_point__(point, vec=True) for segment in self.segments()]
        dists = np.linalg.norm(vecs, axis=1)

        argmin = np.argmin(dists)
        _vec = vecs[argmin]
        if vec:
            return _vec
        else:
            return np.linalg.norm(_vec)
