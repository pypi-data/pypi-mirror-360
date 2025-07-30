import typing

import numpy as np
import trimesh
from open3d.examples.geometry.point_cloud_transformation import transform

from .helpers import *

if typing.TYPE_CHECKING:
    from . import *


def _create_camera_on_plane(normal, distance=5.0):
    """
    Create a trimesh scene with camera positioned on a plane
    and oriented to look along the plane's normal

    Args:
        normal (np.array): 3D plane normal vector
        distance (float): Camera distance from origin along plane

    Returns:
        trimesh.Scene: Configured scene with camera
    """
    # Normalize input vector
    normal = normal / np.linalg.norm(normal)

    # Find orthogonal vector for camera position
    up_ref = np.array([0, 0, 1])

    rotation = from_to_rotation(up_ref, normal)

    scene = trimesh.Scene()
    from lib_3d import Transform3D
    mat = Transform3D.TRS(rotation=rotation, translation=up_ref * distance).numpy()

    scene.camera_transform = mat

    return scene

def vis(
        *shapes: 'Object3D',
        include_children: bool = False,
        world: bool = True,
        show: bool = True,
        camera_direction: np.ndarray = None,
        transform = None
):
    objects: list['Object3D'] = []
    for root in shapes:
        if include_children:
            objects.extend([root, *root.descendents])
        else:
            objects.append(root)

    # Build the scene
    if camera_direction is not None:
        scene = _create_camera_on_plane(camera_direction, 5)
    else:
        scene = trimesh.Scene()
    for obj in objects:
        geo = obj.rendered_mesh()
        if geo is None:
            continue               # skip empties / placeholders

        if hasattr(geo, 'faces') and geo.faces is not None:
            from KUtils import meshu
            meshu.color_faces(geo, obj.vparams.color)

        scene.add_geometry(
            geometry=geo,
            transform=obj.matrix_world.numpy() if world else np.eye(4),
            geom_name=str(obj.id)
        )

    if len(scene.geometry) == 0:
        return None

    if transform is not None:
        scene.apply_transform(np.array(transform))


    if show:
        scene.show()

    return scene