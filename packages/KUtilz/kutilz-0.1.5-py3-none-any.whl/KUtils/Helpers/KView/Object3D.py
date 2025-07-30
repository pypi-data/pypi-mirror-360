import functools

import numpy as np
import trimesh
from KUtils import SimpleUniqueIDGenerator, TreeNodeMixin
from KUtils.Typing import *
from .Transform3D import Transform3D
from .VisualizeMixin import VisParamsMixin
import open3d as o3d

O3D_IDs = SimpleUniqueIDGenerator('Object3DIDGenerator')
UniqueIDMixin = O3D_IDs.Mixin()

class Object3D(
    UniqueIDMixin,
    TreeNodeMixin,
    VisParamsMixin
):
    def as_open3d(self, as_global: bool = True) -> o3d.t.geometry.TriangleMesh:
        vertices = self.mesh.vertices
        triangles = self.mesh.faces

        # Create Open3D TriangleMesh
        o3d_mesh = o3d.t.geometry.TriangleMesh()

        # Set vertices and triangles
        o3d_mesh.vertex.positions = o3d.core.Tensor(vertices, dtype=o3d.core.float32)
        o3d_mesh.triangle.indices = o3d.core.Tensor(triangles, dtype=o3d.core.int32)

        # Apply transformation if needed
        if as_global and self.matrix_world is not None:
            # Convert the transformation matrix to Open3D format
            transform = o3d.core.Tensor(self.matrix_world.numpy(), dtype=o3d.core.float32)
            o3d_mesh.transform(transform)

        return o3d_mesh

    @classmethod
    @functools.cache
    def __designator__(cls):
        from KUtils import stru
        return stru.camel_to_snake(cls.__name__)

    def __init__(self,
                 mesh: 'trimesh.Geometry' = None,
                 transform: Transform3D | np.ndarray = None,
                 name: str = None):
        self.initialize_id()
        self.__transform = None

        self.trimesh: trimesh.Trimesh = mesh
        if transform is None:
            transform = np.eye(4)
        self.trs = Transform3D(transform)

    @property
    def trs(self) -> Transform3D:
        return self.__transform

    @trs.setter
    def trs(self, x):
        self.__transform = Transform3D(x)

    @property
    def matrix_world(self) -> Transform3D:
        if self.parent is None:
            return self.trs
        else:
            return self.parent.matrix_world @ self.trs

    def centroid(self, world: bool = True):
        pt = self.trimesh.centroid
        if world:
            pt = self.matrix_world.apply(pt)
        return pt

    def rendered_mesh(self):
        geo = self.trimesh
        if self.trimesh is None:
            return None

        obj = self
        if obj.vparams.color is not None:
            geo = obj.trimesh.copy()
            from KUtils import meshu
            if getattr(geo, 'faces', None) is None:
                pass
                # meshu.color_vertices(geo, obj.vparams.color.rgba())
            else:
                meshu.color_faces(geo, obj.vparams.color.rgba())

        return geo

    def scene(self) -> trimesh.Scene:
        all = [self, *self.descendents]

        scene = trimesh.Scene()

        for obj in all:
            geo = obj.rendered_mesh()

            if geo is None:
                continue

            scene.add_geometry(
                geometry=geo,
                transform=obj.matrix_world.numpy(),
                geom_name=str(obj.id)
            )


        return scene

    def __project_onto__(self, target):
        raise NotImplementedError()
    
    def __dist_point__(self, point: np.ndarray, signed: bool = True):
        point = self.matrix_world.inv().apply(point)

        from .helpers import point_mesh_signed_distance
        return point_mesh_signed_distance(
            self.trimesh,
            point
        )
    

    @final
    def dist(self, other: 'Object3D', signed: bool = True) -> float:
        name = other.__designator__()
        meth_name = f'__dist_{name}__'
        assert hasattr(self, meth_name), f'Shape {self.__designator__()} has not method {meth_name}'

        return getattr(self, meth_name)(other, signed=signed)

    def projects(self, *objs: 'Object3D') -> Tuple['Object3D', ...]:
        return tuple(map(self.__project_onto__, objs))

    def vertices(self, world: bool = True):
        v = self.trimesh.vertices
        if world:
            v = self.trs.apply(v)
        return v