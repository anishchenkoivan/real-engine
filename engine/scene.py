import typing
from enum import Enum
from graphics import LogicProvider, ShaderProgram

from OpenGL.GL import *
from pyglm import glm
from struct import pack, unpack


class Buffers(Enum):
    MATERIAlS = 0
    SPHERES = 1
    PLANES = 2
    TRIANGLES = 3
    LENSES = 4


class Converter:
    @staticmethod
    def to_int(data):
        if data is None:
            return 0
        if isinstance(data, int):
            return data
        if isinstance(data, float):
            data = pack('f', data)
            return unpack('i', data)[0]
        if isinstance(data, bool):
            return float(data)

        raise NotImplementedError()

    @staticmethod
    def to_glm_array(arr):
        arr = [Converter.to_int(item) for item in arr]
        return glm.array(glm.int32, *arr)


class LoadableObject:
    def __init__(self):
        pass

    def as_array(self):
        raise NotImplementedError()


class Vector(LoadableObject):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @typing.override
    def as_array(self):
        return [self.x, self.y, self.z, None]


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
    def __init__(self, color: Color, roughness: float, scene_loader, transparent: bool = False, optical_density : float = 1):
        super().__init__()
        self.color = color
        self.roughness = roughness
        self.transparent = transparent
        self.optical_density = optical_density
        self.index = scene_loader.new_material_index()

    @typing.override
    def as_array(self):
        res = [
            self.color.red, self.color.green, self.color.blue,
            self.roughness,
            self.optical_density,
            self.transparent,
            None, None
        ]
        return res


class GraphicalPrimitive(LoadableObject):
    def __init__(self, material: Material):
        super().__init__()
        self.material_index = material.index


class Sphere(GraphicalPrimitive):
    def __init__(self, center: Vector, radius, material: Material):
        super().__init__(material)
        self.center = center
        self.radius = radius

    @typing.override
    def as_array(self):
        return [
            self.center.x, self.center.y, self.center.z,
            self.radius, self.material_index,
            None, None, None # padding
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
            self.a, self.b, self.c, self.d,
            self.material_index,
            None, None, None  # padding
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
            self.a.x, self.a.y, self.a.z, None,
            self.b.x, self.b.y, self.b.z, None,
            self.c.x, self.c.y, self.c.z,
            self.material_index
        ]


class Lens(GraphicalPrimitive):
    def __init__(self, sphere: Sphere, plane: Plane, material: Material, direction: Vector):
        super().__init__(material)
        self.sphere = sphere
        self.plane = plane
        self.direction = direction

    @typing.override
    def as_array(self):
        return self.sphere.as_array() + self.plane.as_array()[:-3] + [self.material_index, None, None] + self.direction.as_array()


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
        lenses = self.spawn_lenses()

        self.load_SSBO(self.materials, Buffers.MATERIAlS.value)
        self.load_SSBO(spheres, Buffers.SPHERES.value)
        self.load_SSBO(planes, Buffers.PLANES.value)
        self.load_SSBO(triangles, Buffers.TRIANGLES.value)
        self.load_SSBO(lenses, Buffers.LENSES.value)

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
            arr += i.as_array()

        return Converter.to_glm_array(arr)

    def define_materials_list(self):
        raise NotImplementedError()

    def spawn_spheres(self):
        return glm.array(glm.float32)

    def spawn_planes(self):
        return glm.array(glm.float32)

    def spawn_triangles(self):
        return glm.array(glm.float32)

    def spawn_lenses(self):
        return glm.array(glm.float32)

    def sky_config(self):
        return SkyConfig(Vector(0.4, 0.3, 1.0), 0.05, Color(1.0, 1.0, 0.0), Color(0.67, 0.84, 0.89))
