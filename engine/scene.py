import typing
from buffers import Buffers
from graphics import LogicProvider, ShaderProgram

from OpenGL.GL import *
from pyglm import glm
from struct import pack, unpack
from simplejpeg import decode_jpeg


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
    def __init__(self, color: Color, roughness: float, scene_loader, transparent: bool = False, optical_density: float = 1, dispersion_coefficient: float = 0.01):
        super().__init__()
        self.color = color
        self.roughness = roughness
        self.transparent = transparent
        self.optical_density = optical_density
        self.dispersion_coefficient = dispersion_coefficient
        self.index = scene_loader.new_material_index()

    @typing.override
    def as_array(self):
        res = [
            self.color.red, self.color.green, self.color.blue,
            self.roughness,
            self.optical_density,
            self.transparent,
            self.dispersion_coefficient,
            None
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
            None, None, None  # padding
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
    def __init__(self, sphere: Sphere, plane: Plane, material: Material):
        super().__init__(material)
        self.sphere = sphere
        self.plane = plane

    @typing.override
    def as_array(self):
        return self.sphere.as_array() + self.plane.as_array()[:-3] + [self.material_index, None, None]


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
            self.__initialize()
            self.__initialized = True

        super().render()

    def new_material_index(self):
        self.last_material_index += 1
        return self.last_material_index - 1

    def __initialize(self):
        spheres = self.spawn_spheres()
        planes = self.spawn_planes()
        triangles = self.spawn_triangles()
        lenses = self.spawn_lenses()

        self.__load_SSBO(self.materials, Buffers.MATERIAlS.value)
        self.__load_SSBO(spheres, Buffers.SPHERES.value)
        self.__load_SSBO(planes, Buffers.PLANES.value)
        self.__load_SSBO(triangles, Buffers.TRIANGLES.value)
        self.__load_SSBO(lenses, Buffers.LENSES.value)

        self.__load_skybox()

    def __load_SSBO(self, data, index):
        if len(data) == 0:
            return

        data = SceneLoader.to_glm_array(data)
        size = len(data) * 4
        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, size, None, GL_STATIC_DRAW)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, size, data.ptr)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, index, ssbo)

    def __load_skybox(self):
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

        for i, j in enumerate(self.spawn_skybox_textures()):
            self.__load_skybox_side(i, j)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        glUniform1i(glGetUniformLocation(self.shader.program, "skybox"), 0)


    def __load_skybox_side(self, idx, path):
        with open(path, 'rb') as texture_file:
            texture_bytes = texture_file.read()
        texture_data = decode_jpeg(texture_bytes)
        width, height, _ = texture_data.shape
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + idx,
                         0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data
            );


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

    def spawn_skybox_textures(self):
        return [
            "../media/bluecloud_ft.jpg",
            "../media/bluecloud_bk.jpg",
            "../media/bluecloud_up.jpg",
            "../media/bluecloud_dn.jpg",
            "../media/bluecloud_rt.jpg",
            "../media/bluecloud_lf.jpg",
        ]
