from collections import namedtuple
import typing
from enum import Enum
from graphics import LogicProvider, ShaderProgram

import OpenGL.GL.shaders
import numpy as np
from OpenGL.GL import *
from pyglm import glm
from ctypes import *


class Buffers(Enum):
    MATERIAlS = 0
    SPHERES = 1
    PLANES = 2
    TRIANGLES = 3


class LoadableObject:
    def __init__(self):
        pass

    def as_array(self):
        raise NotImplementedError()

    def as_c_type(self):
        raise NotImplementedError()

    def as_tuple(self):
        raise NotImplementedError()


class Vector(LoadableObject):
    class c_vector(Structure):
        _fields_ = [
            ("x", c_float),
            ("y", c_float),
            ("z", c_float),
        ]

    class vector_tuple(typing.NamedTuple):
        x: c_float
        y: c_float
        z: c_float

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @typing.override
    def as_array(self):
        return [self.x, self.y, self.z, 0.0]

    @typing.override
    def as_c_type(self):
        return Vector.c_vector(x=self.x, y=self.y, z=self.z)

    @typing.override
    def as_tuple(self):
        return Vector.vector_tuple(
            x=c_float(self.x),
            y=c_float(self.y),
            z=c_float(self.z)
        )


class Color(Vector):
    def __init__(self, red, green, blue):
        super().__init__(red, green, blue)

    @property
    def red(self):
        return self.x

    @property
    def green(self):
        return self.y

    @property
    def blue(self):
        return self.z


class Material(LoadableObject):
    class c_material(Structure):
        _fields_ = [
            ("color", Vector.c_vector),
            ("refllose", Vector.c_vector),
        ]

    class material_tuple(typing.NamedTuple):
        color: Color.vector_tuple
        refllose: Color.vector_tuple

    def __init__(self, color: Color, refllose: Color, scene_loader):
        super().__init__()
        self.color = color
        self.refllose = refllose
        self.index = scene_loader.new_material_index()

    @typing.override
    def as_array(self):
        res = [
            self.color.red, self.color.green, self.color.blue, 0.0,
            self.refllose.red, self.refllose.green, self.refllose.blue, 0.0,
        ]
        return res

    @typing.override
    def as_c_type(self):
        return Material.c_material(
            color=Vector.c_vector(
                self.color.red, self.color.green, self.color.blue),
            refllose=Vector.c_vector(self.refllose.red,
                                     self.refllose.green, self.refllose.blue)
        )

    @typing.override
    def as_tuple(self):
        return Material.material_tuple(
            color=Vector.vector_tuple(
                self.color.red, self.color.green, self.color.blue),
            refllose=Vector.vector_tuple(self.refllose.red,
                                         self.refllose.green, self.refllose.blue)
        )


class GraphicalPrimitive(LoadableObject):
    def __init__(self, material: Material):
        super().__init__()
        self.material_index = material.index


class Sphere(GraphicalPrimitive):
    class c_sphere(Structure):
        _fields_ = [
            ("centre", Vector.c_vector),
            ("radius", c_float),
            ("material", c_int32)
        ]

    class sphere_tuple(typing.NamedTuple):
        centre: Vector.vector_tuple
        radius: c_float
        material: c_int

    def __init__(self, centre: Vector, radius, material: Material):
        super().__init__(material)
        self.centre = centre
        self.radius = radius

    @typing.override
    def as_array(self):
        print(self.material_index)
        return [
            self.centre.x, self.centre.y, self.centre.z,
            self.radius, self.material_index, 0.0, 0.0, 0.0
        ]

    @typing.override
    def as_c_type(self):
        return Sphere.c_sphere(
            color=Vector.c_vector(self.centre.x, self.centre.y, self.centre.z),
            radius=c_float(self.radius),
            material=c_int(self.material_index)
        )

    @typing.override
    def as_tuple(self):
        return Sphere.c_sphere(
            color=Vector.vector_tuple(
                self.centre.x, self.centre.y, self.centre.z),
            radius=c_float(self.radius),
            material=c_int(self.material_index)
        )


class Plane(GraphicalPrimitive):
    class c_plane(Structure):
        _fields_ = [
            ("a", c_float),
            ("b", c_float),
            ("c", c_float),
            ("d", c_float),
            ("material", c_int32)
        ]

    class plane_tuple(typing.NamedTuple):
        a: c_float
        b: c_float
        c: c_float
        d: c_float
        material: c_int

    def __init__(self, a: float, b: float, c: float, d: float, material: Material):
        super().__init__(material)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    @typing.override
    def as_array(self):
        print(self.material_index)
        return [
            self.a, self.b, self.c, self.d,
            self.material_index,
            0.0, 0.0, 0.0  # padding
        ]

    @typing.override
    def as_c_type(self):
        return Plane.c_plane(
            a=c_float(self.a),
            b=c_float(self.b),
            c=c_float(self.c),
            d=c_float(self.d),
            material=c_int(self.material_index)
        )

    @typing.override
    def as_tuple(self):
        return Plane.plane_tuple(
            a=c_float(self.a),
            b=c_float(self.b),
            c=c_float(self.c),
            d=c_float(self.d),
            material=c_int(self.material_index)
        )


class Triangle(GraphicalPrimitive):
    class c_triangle(Structure):
        _fields_ = [
            ("a", Vector.c_vector),
            ("padding1", c_float),

            ("b", Vector.c_vector),
            ("padding2", c_float),

            ("c", Vector.c_vector),
            ("material", c_int32)
        ]

    class triangle_tuple(typing.NamedTuple):
        a: Vector.vector_tuple
        padding1: c_int32

        b: Vector.vector_tuple
        padding2: c_int32

        c: Vector.vector_tuple
        material: c_int32

    def __init__(self, a: Vector, b: Vector, c: Vector, material: Material):
        super().__init__(material)
        self.a = a
        self.b = b
        self.c = c

    @typing.override
    def as_array(self):
        print(self.material_index)
        return [
            self.a.x, self.a.y, self.a.z, 0,
            self.b.x, self.b.y, self.b.z, 0,
            self.c.x, self.c.y, self.c.z,
            self.material_index
        ]

    @typing.override
    def as_c_type(self):
        return Sphere.c_sphere(
            a=self.a.as_c_type(),
            b=self.b.as_c_type(),
            c=self.c.as_c_type(),
            material=c_int(self.material_index)
        )

    @typing.override
    def as_tuple(self):
        return Triangle.triangle_tuple(
            a=self.a.as_tuple(),
            padding1=c_int32(0),
            b=self.b.as_tuple(),
            padding2=c_int32(0),
            c=self.c.as_tuple(),
            material=c_int32(self.material_index)
        )


class SkyConfig(typing.NamedTuple):
    sunPosition: Vector
    sunRadius: float
    sunColor: Color
    skyColor: Color


class SceneLoader(LogicProvider):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__()
        self.shader = shader_program
        self.__initialized = False

        self.last_material_index = 0
        materials = self.define_materials_list()
        self.materials = sorted(materials, key=lambda mat: mat.index)

    @typing.final
    def render(self):
        if not self.__initialized:
            self.initialize()
            self.__initialized = True

        super().render()

    def new_material_index(self):
        self.last_material_index += 1
        return self.last_material_index - 1

    def initialize(self):
        spheres = self.spawn_spheres()
        planes = self.spawn_planes()
        triangles = self.spawn_triangles()

        self.load_SSBO(self.materials, Buffers.MATERIAlS.value)
        self.load_SSBO(spheres, Buffers.SPHERES.value)
        self.load_SSBO(planes, Buffers.PLANES.value)
        self.load_SSBO(triangles, Buffers.TRIANGLES.value)

        self.load_sky_config(self.sky_config())

    def load_SSBO(self, data, index):
        if len(data) == 0:
            return

        data = SceneLoader.to_glm_array(data)
        size = len(data) * 4
        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, size, None, GL_STATIC_DRAW)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, size, data.ptr)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, index, ssbo)

    def load_sky_config(self, conf: SkyConfig):
        glUniform3f(glGetUniformLocation(self.shader.program,
                    "sunPosition"), conf.sunPosition.x, conf.sunPosition.y, conf.sunPosition.z)
        glUniform1f(glGetUniformLocation(self.shader.program,
                    "sunRadius"), conf.sunRadius)

        glUniform3f(glGetUniformLocation(self.shader.program,
                                         f"sunColor"), conf.sunColor.red, conf.sunColor.green, conf.sunColor.blue)
        glUniform3f(glGetUniformLocation(self.shader.program,
                                         f"skyColor"), conf.skyColor.red, conf.skyColor.green, conf.skyColor.blue)

    @staticmethod
    def to_glm_array(data: list[LoadableObject]):
        if len(data) == 0:
            return None

        arr = []

        for i in data:
            arr.append(i.as_tuple())

        print(arr)
        return glm.array(arr)

    def define_materials_list(self):
        raise NotImplementedError()

    def spawn_spheres(self):
        return glm.array(glm.float32)

    def spawn_planes(self):
        return glm.array(glm.float32)

    def spawn_triangles(self):
        return glm.array(glm.float32)

    def sky_config(self):
        return SkyConfig(Vector(0.4, 0.3, 1.0), 0.05, Color(1.0, 1.0, 0.0), Color(0.67, 0.84, 0.89))


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        self.mt2 = Material(Color(0.0, 1.0, 0.0), Color(1.0, 1.0, 1.0), self)
        self.mt1 = Material(Color(0.0, 0.0, 1.0), Color(1.0, 1.0, 1.0), self)
        self.mt3 = Material(Color(1.0, 0.0, 0.0), Color(1.0, 1.0, 1.0), self)
        print(self.mt1, self.mt2, self.mt3)
        return [self.mt1, self.mt2, self.mt3]

    @typing.override
    def spawn_spheres(self):
        return [
            Sphere(Vector(-2.0, 1.0, 13.0), 1.5, self.mt1),
            Sphere(Vector(1.0, -1.2, 13.0), 1.25, self.mt2),
        ]

    @typing.override
    def spawn_planes(self):
        return [
            Plane(0.0, 1.0, 0.0, 2.0, self.mt3)
        ]

    @typing.override
    def spawn_triangles(self):
        return [
            Triangle(Vector(-1.0, 0.0, 10.0), Vector(-1.0, 1.0, 11.0),
                     Vector(3.0, 1.0, 10.0), self.mt3),
            Triangle(Vector(-1.0, 1.0, 11.0), Vector(-1.0, 2.0, 10.0),
                     Vector(3.0, 1.0, 10.0), self.mt3),
            Triangle(Vector(-1.0, 2.0, 10.0), Vector(-1.0, -1.0, 9.0),
                     Vector(3.0, 1.0, 10.0), self.mt3),
            Triangle(Vector(-1.0, -1.0, 9.0), Vector(-1.0, 0.0, 10.0),
                     Vector(3.0, 1.0, 10.0), self.mt3),
            Triangle(Vector(-1.0, 2.0, 10.0), Vector(-1.0, 1.0, 11.0),
                     Vector(-1.0, -1.0, 9.0), self.mt3)
        ]
