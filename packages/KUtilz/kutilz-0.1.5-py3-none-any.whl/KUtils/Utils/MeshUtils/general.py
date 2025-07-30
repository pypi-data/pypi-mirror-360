from KUtils.Typing import *
import numpy as np
if TYPE_CHECKING:
    from trimesh import Trimesh

def color_vertices(mesh: 'Trimesh', color, mask = None) -> None:

    if mask is None:
        mask = np.ones(len(mesh.vertices), dtype=bool)

    vertex_colors = mesh.visual.vertex_colors

    color = np.asanyarray(color)
    if color.shape == (3,):
        color = np.append(color, 255)  # assume opaque if alpha not provided

    mask = np.asanyarray(mask, dtype=bool)

    if len(mask) != len(mesh.vertices):
        raise ValueError("Mask length must match vertex count")

    vertex_colors[mask] = color

    mesh.visual.vertex_colors = vertex_colors

def color_faces(mesh: 'Trimesh', color, mask = None) -> None:
    if mask is None:
        mask = np.ones(len(mesh.faces), dtype=bool)

    face_colors = mesh.visual.face_colors

    color = np.asanyarray(color)
    if color.shape == (3,):
        color = np.append(color, 255)  # assume opaque if alpha not provided

    mask = np.asarray(mask, dtype=bool)

    if len(mask) != len(mesh.faces):
        raise ValueError("Mask length must match face count")

    face_colors[mask] = color
    mesh.visual.face_colors = face_colors
