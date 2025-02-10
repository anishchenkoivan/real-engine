import typing
from enum import Enum
from graphics import LogicProvider, ShaderProgram

import OpenGL.GL.shaders
import numpy as np
from OpenGL.GL import *
from pyglm import glm


class Buffers(Enum):
    MATERIAlS = 0
    SPHERES = 1
    PLANES = 2
    TRIANGLES = 3


class Color(typing.NamedTuple):
    red: float
    green: float
    blue: float


class Vector(typing.NamedTuple):
    x: float
    y: float
    z: float


class SkyConfig(typing.NamedTuple):
    sunPosition: Vector
    sunRadius: float
    sunColor: Color
    skyColor: Color


class LoadableObject:
    def __init__(self):
        pass

    def as_array(self):
        raise NotImplementedError()


class Material(LoadableObject):
    def __init__(self, color: Color, refllose: Color, scene_loader):
        super().__init__()
        self.color = color
        self.refllose = refllose
        self.index = scene_loader.new_material_index()

    @typing.override
    def as_array(self):
        return [
            self.color.red, self.color.green, self.color.blue, 0.0,
            self.refllose.red, self.refllose.green, self.refllose.blue, 0.0
        ]


class GraphicalPrimitive(LoadableObject):
    def __init__(self, material: Material):
        super().__init__()
        self.material_index = material.index


class Sphere(GraphicalPrimitive):
    def __init__(self, centre: Vector, radius, material: Material):
        super().__init__(material)
        self.centre = centre
        self.radius = radius

    @typing.override
    def as_array(self):
        return [
            self.centre.x, self.centre.y, self.centre.z,
            self.radius, self.material_index,
            0.0, 0.0, 0.0  # padding
        ]


class Plane(GraphicalPrimitive):
    def __init__(self, a: float, b: float, c: float, d: float, material: Material):
        super().__init__(material)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    @typing.override
    def as_array(self):
        return [
            self.a, self.b, self.c, self.d, self.material_index,
            0.0, 0.0, 0.0  # padding
        ]


class Triangle(GraphicalPrimitive):
    def __init__(self, a: Vector, b: Vector, c: Vector, material: Material):
        super().__init__(material)
        self.a = a
        self.b = b
        self.c = c

    @typing.override
    def as_array(self):
        return [
            self.a.x, self.a.y, self.a.z, 0.0,
            self.b.x, self.b.y, self.b.z, 0.0,
            self.c.x, self.c.y, self.c.z,
            self.material_index
        ]


class SceneLoader(LogicProvider):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__()
        self.shader = shader_program
        self.__initialized = False

        self.last_material_index = 0
        self.materials = self.define_materials_list()
        self.materials = sorted(self.materials, key=lambda mat: mat.index)

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
        materials = self.define_materials_list()
        spheres = self.spawn_spheres()
        planes = self.spawn_planes()
        triangles = self.spawn_triangles()

        self.load_SSBO(materials, Buffers.MATERIAlS.value)
        self.load_SSBO(spheres, Buffers.SPHERES.value)
        self.load_SSBO(planes, Buffers.PLANES.value)
        self.load_SSBO(triangles, Buffers.TRIANGLES.value)

        self.load_sky_config(self.sky_config())

    def load_SSBO(self, data, index):
        if len(data) == 0:
            return

        size = len(data) * len(data[0].as_array()) * 4
        data = SceneLoader.to_glm_array(data)
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

        for i in range(3):
            glUniform1f(glGetUniformLocation(self.shader.program,
                        f"sunColor[{i}]"), conf.sunColor[i])

        for i in range(3):
            glUniform1f(glGetUniformLocation(self.shader.program,
                        f"skyColor[{i}]"), conf.skyColor[i])

    @staticmethod
    def to_glm_array(data: list[LoadableObject]):
        arr = []

        for i in data:
            arr += i.as_array()

        return glm.array(glm.float32, *arr)

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
        mt1 = Material(Color(1.0, 0.0, 1.0), Color(0.1, 0.1, 0.1), self)
        mt2 = Material(Color(1.0, 0.0, 1.0), Color(0.3, 0.3, 0.3), self)
        mt3 = Material(Color(0.4, 0.4, 0.4), Color(0.4, 0.4, 0.4), self)
        return [mt1, mt2, mt3]

    @typing.override
    def spawn_spheres(self):
        return [
            Sphere(Vector(-2.0, 1.0, 13.0), 1.5, self.materials[0]),
            Sphere(Vector(1.0, -1.2, 13.0), 1.25, self.materials[1]),
        ]

    @typing.override
    def spawn_planes(self):
        return [
            Plane(0.0, 1.0, 0.0, 2.0, self.materials[2])
        ]

    @typing.override
    def spawn_triangles(self):
        return [
            Triangle(Vector(-1.0, 0.0, 10.0), Vector(-1.0, 1.0, 11.0),
                     Vector(3.0, 1.0, 10.0), self.materials[2]),
        ]
