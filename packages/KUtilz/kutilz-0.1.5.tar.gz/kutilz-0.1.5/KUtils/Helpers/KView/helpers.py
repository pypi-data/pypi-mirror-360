import numpy as np
from scipy.spatial.transform import Rotation

from math import sqrt

import math
from KUtils.Typing import *
import trimesh


POINT2D = Tuple[float, float]
LINE2D = Tuple[POINT2D, POINT2D]

def angle_ppp(p0, p1, p2, degrees: bool = True) -> float:
    # 计算向量v1和v2（从p1指向p0和p2）
    v1_x = p0[0] - p1[0]
    v1_y = p0[1] - p1[1]
    v2_x = p2[0] - p1[0]
    v2_y = p2[1] - p1[1]

    # 计算点积和模长
    dot = v1_x * v2_x + v1_y * v2_y
    norm1 = math.hypot(v1_x, v1_y)
    norm2 = math.hypot(v2_x, v2_y)

    # 处理零向量（若p0或p2与p1重合）
    if norm1 == 0 or norm2 == 0:
        raise ValueError("Points cannot coincide (resulting in zero vector).")

    # 计算余弦值并限制浮点精度范围
    cos_theta = dot / (norm1 * norm2)
    cos_theta = max(min(cos_theta, 1.0), -1.0)  # 避免因精度问题超出范围

    # 计算弧度并转换为角度
    radians = math.acos(cos_theta)
    return math.degrees(radians) if degrees else radians

def angle_ll(l1, l2):
    def dot(vA, vB):
        return vA[0] * vB[0] + vA[1] * vB[1]

    lineA = l1
    lineB = l2
    # Get nicer vector form
    vA = [(lineA[0][0] - lineA[1][0]), (lineA[0][1] - lineA[1][1])]
    vB = [(lineB[0][0] - lineB[1][0]), (lineB[0][1] - lineB[1][1])]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA) ** 0.5
    magB = dot(vB, vB) ** 0.5
    # Get cosine value
    cos_ = dot_prod / magA / magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod / magB / magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle) % 360

    if ang_deg - 180 >= 0:
        # As in if statement
        return 360 - ang_deg
    else:

        return ang_deg

def line_len(p0, p1) -> float:
    return np.linalg.norm(np.subtract(p1, p0))

def dist_lp(line, p) -> float:
    p1, p2 = np.array(line).reshape(2, -1)
    p3 = np.array(p).reshape(-1)
    from numpy.linalg import norm
    d = norm(np.cross(p2-p1, p1-p3))/norm(p2-p1)
    return d


def horizontal_dist_lp(line, p) -> float:
    """
    Compute the horizontal distance from point p to the line.

    Args:
        line: A line defined by two points [(x1, y1), (x2, y2)]
        p: A point (x, y)

    Returns:
        The horizontal distance from p to the line (always positive)
    """
    # Convert inputs to numpy arrays
    p1, p2 = np.array(line).reshape(2, 2)
    p3 = np.array(p).reshape(2)

    # If line is vertical, horizontal distance is simply the x-difference
    if p1[0] == p2[0]:
        return abs(p3[0] - p1[0])

    # Calculate the x-coordinate where a horizontal line through p would intersect our line
    # Line equation: (y2-y1)(x-x1) = (y-y1)(x2-x1)
    # For horizontal line through p: y = p3[1]
    x_intersect = ((p3[1] - p1[1]) * (p2[0] - p1[0])) / (p2[1] - p1[1]) + p1[0]

    # Horizontal distance is the difference in x-coordinates
    return  (p3[0] - x_intersect)

def signed_dist_lp(line, p) -> float:
    from numpy.linalg import norm
    p1, p2 = np.asarray(line, dtype=float).reshape(2, 2)
    p3 = np.asarray(p,    dtype=float).reshape(2)

    # --- direction vector of the line & its clockwise normal -----------------
    v = p2 - p1                      # direction  p1 → p2
    n = np.array([v[1], -v[0]])      # rotate clockwise by 90°

    # Choose the *up / right*–pointing normal.
    #   If the x-component is negative, or x==0 but y is negative, flip it.
    if n[0] < 0 or (np.isclose(n[0], 0) and n[1] < 0):
        n = -n

    n /= norm(v)                     # we only need length ||v|| for scaling

    # --- signed distance -----------------------------------------------------
    d_signed = np.dot(p3 - p1, n)
    return d_signed


def from_to_rotation(vec1, vec2) -> np.ndarray:
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def dot_product(x, y):
    return sum([x[i] * y[i] for i in range(len(x))])

def norm(x):
    return sqrt(dot_product(x, x))

def normalize(x):
    return [x[i] / norm(x) for i in range(len(x))]

def project_onto_plane(x, n):
    d = dot_product(x, n) / norm(n)
    p = [d * normalize(n)[i] for i in range(len(n))]
    return [x[i] - p[i] for i in range(len(x))]

def cast_to_2d(*obj: np.ndarray, target_normal: np.ndarray):
    rotation = from_to_rotation(target_normal, np.array([0, 0, 1]))

    res = []
    for ob in obj:
        ob = ob.reshape(3, -1)
        ob = rotation @ ob
        ob = ob[:2, :]
        res.append(ob.reshape(-1, 2))

    return tuple(res)

def intersection_2d(
        point: np.ndarray,
        line_segment: np.ndarray,
        direction: np.ndarray
) -> float:
    line_segment = line_segment.reshape(-1, 2)
    point = np.array(point).reshape(2)
    direction = np.array(direction).reshape(2)
    A, B = line_segment[0], line_segment[1]

    # Unpack segment points (A, B), point (P), and direction vector (D)
    P = point
    D = direction
    Ax, Ay = A
    Bx, By = B
    Px, Py = P
    Dx, Dy = D

    seg_vec_x = Bx - Ax
    seg_vec_y = By - Ay

    # Calculate determinant for line intersection
    denominator = Dy * seg_vec_x - Dx * seg_vec_y

    if denominator == 0:
        # Handle parallel lines (colinear check)
        APx = Ax - Px
        APy = Ay - Py
        if APx * Dy != APy * Dx:
            return float('inf')  # Parallel but not colinear

        # Calculate parametric values for segment endpoints along ray
        tA = (Ax - Px) / Dx if Dx != 0 else (Ay - Py) / Dy
        tB = (Bx - Px) / Dx if Dx != 0 else (By - Py) / Dy

        t_min, t_max = sorted([tA, tB])
        overlap_start = max(t_min, 0)

        if overlap_start > t_max or (Dx == 0 and Dy == 0):
            return float('inf')  # No valid intersection

        # Calculate closest intersection point
        closest_t = overlap_start
        intersect_x = Px + closest_t * Dx
        intersect_y = Py + closest_t * Dy
        return ((intersect_x - Px) ** 2 + (intersect_y - Py) ** 2) ** 0.5
    else:
        # Calculate parameters for potential intersection
        t_numerator = (Ax - Px) * (-seg_vec_y) + seg_vec_x * (Ay - Py)
        s_numerator = Dx * (Ay - Py) - Dy * (Ax - Px)
        t = t_numerator / denominator
        s = s_numerator / denominator

        if t >= 0 and 0 <= s <= 1:
            # Valid intersection found
            intersect_x = Px + t * Dx
            intersect_y = Py + t * Dy
            return ((intersect_x - Px) ** 2 + (intersect_y - Py) ** 2) ** 0.5

    return float('inf')  # No valid intersection

def intersection_2d_both_direction(
        point: np.ndarray,
        line_segment: np.ndarray,
        direction: np.ndarray
) -> float:
    pos = intersection_2d(point, line_segment, direction)
    neg = intersection_2d(point, line_segment, -direction)
    if neg != float('inf'):
        neg = -neg

    if neg != float('inf') and pos != float('inf') and (pos >= 1e-2 or neg >= 1e-2):

        raise RuntimeError('WTF')

    return min(pos, neg)

def cast_up(points):
    """
    Convert 2D point(s) to 3D by adding z=0 coordinate.

    Args:
        points: Either:
                - A single 2D point as array-like of shape (2,), or
                - Multiple 2D points as array-like of shape (n, 2)

    Returns:
        - For single input: 3D point as numpy array of shape (3,)
        - For multiple inputs: 3D points as numpy array of shape (n, 3)
    """
    points = np.asarray(points)

    if points.ndim == 1:  # Single point (2,)
        return np.append(points, 0)
    elif points.ndim == 2:  # Multiple points (n, 2)
        return np.column_stack([points, np.zeros(len(points))])
    else:
        raise ValueError("Input must be either (2,) or (n, 2) shape")

def distance_point_to_polyline_on_plane_at_direction(
        point: np.ndarray,
        polyline: np.ndarray,
        axis_vector: np.ndarray,
        plane_normal: np.ndarray
) -> float:

    proj_point = cast_to_2d(point, target_normal=plane_normal)[0]
    proj_polyline = np.array([cast_to_2d(p, target_normal=plane_normal) for p in polyline]).reshape(-1, 2)

    # 投影方向向量到平面
    proj_axis = cast_to_2d(axis_vector, target_normal=plane_normal)[0]
    if np.linalg.norm(proj_axis) < 1e-6:
        raise RuntimeError("Axis vector is orthogonal to plane")
    ray_dir = proj_axis / np.linalg.norm(proj_axis)

    plane_point = np.array((0, 0, 0))


    # 2D射线与线段相交检测
    closest_t = float('inf')
    for i in range(len(proj_polyline) - 1):
        segment = np.array([
            proj_polyline[i], proj_polyline[i + 1]
        ])

        dist = intersection_2d_both_direction(proj_point, segment, ray_dir)
        if abs(dist) < abs(closest_t):
            closest_t = dist


    return closest_t #* np.linalg.norm(proj_axis)

def dist_3d_pp_on_vector(
        pt0: np.ndarray,
        pt1: np.ndarray,
        vec: np.ndarray
) -> float:
    if np.allclose(vec, 0):
        raise ValueError("Direction vector `vec` must not be zero.")

    # Normalize direction vector
    unit_vec = vec / np.linalg.norm(vec)

    # Compute vector between points
    delta = pt1 - pt0

    # Project delta onto unit_vec
    distance_along_vec = np.dot(delta, unit_vec)

    return distance_along_vec

def distance_point_to_polyline_at_1d(
        point: np.ndarray,
        polyline: np.ndarray,
        axis_vector: np.ndarray
):
    # 归一化轴向量以获取单位方向向量[3,5](@ref)
    axis_norm = np.linalg.norm(axis_vector)
    if axis_norm == 0:
        raise ValueError("Axis vector cannot be a zero vector")
    axis_unit = axis_vector / axis_norm

    # 计算多段线顶点在轴上的投影标量值[3,5](@ref)
    polyline_projections = np.dot(polyline, axis_unit)
    proj_min = np.min(polyline_projections)
    proj_max = np.max(polyline_projections)

    # 计算点的投影标量值[3,14](@ref)
    point_projection = np.dot(point, axis_unit)

    # 判断投影点是否在多段线投影区间外并计算距离[5,14](@ref)
    if point_projection < proj_min:
        return proj_min - point_projection
    elif point_projection > proj_max:
        return - (point_projection - proj_max)
    else:
        return 0.0

def plane_intersection(
        plane_0_normal: np.ndarray,
        plane_1_normal: np.ndarray,
        point: np.ndarray
):
    return np.cross(plane_0_normal, plane_1_normal)
    #computes the intersection of two planes that crosses a given point
    pass

def point_mesh_signed_distance(
        mesh: trimesh.Trimesh,
        point: np.ndarray) -> float:
    closest = trimesh.proximity.closest_point(mesh, [point])
    distance = closest[1][0]
    closest_point = closest[0][0]

    # Check if point is inside mesh using ray casting
    is_inside = mesh.contains([point])[0]

    # Calculate sign (inside: negative, outside: positive)
    sign = -1 if is_inside else 1

    # Calculate vector to closest point and validate direction
    to_surface = closest_point - point
    surface_normal = mesh.face_normals[closest[2][0]]

    # Verify normal direction matches containment result
    if sign * np.dot(surface_normal, to_surface) < 0:
        return sign * distance

    # Handle ambiguous cases using ray containment
    return sign * distance

def extreme_smooth_curve_3d(pts: List[np.ndarray], final_count_multiplier=40):
    n = len(pts)

    from scipy.interpolate import splprep, splev
    pts_array = np.array(pts)
    diff = np.diff(pts_array, axis=0)
    dist = np.sqrt(np.sum(diff ** 2, axis=1))
    u0 = np.zeros(n)
    u0[1:] = np.cumsum(dist)
    if u0[-1] == 0:
        u0 = np.linspace(0, 1, n)
    else:
        u0 = u0 / u0[-1]

    k = min(3, n - 1)
    s_value = n + np.sqrt(2 * n)

    current_pts = pts_array.copy()
    for _ in range(3):
        tck, *_ = splprep(current_pts.T, u=u0, s=s_value, k=k)
        smoothed_coords = splev(u0, tck)
        current_pts = np.column_stack(smoothed_coords)

    u_new = np.linspace(0, 1, n * final_count_multiplier)
    upsampled_coords = splev(u_new, tck)
    result = np.column_stack(upsampled_coords)

    from .Shapes import Polyline
    return Polyline(result)