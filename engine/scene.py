import typing
from graphics import LogicProvider, Renderer, ShaderProgram, MeshGroup

import OpenGL.GL.shaders
import numpy as np
from OpenGL.GL import *
from pyglm import glm


class Material(typing.NamedTuple):
    color: glm.vec3
    refllose: glm.vec3


class Sphere(typing.NamedTuple):
    centre: glm.vec3
    radius: float
    material_idx: int


class Plane(typing.NamedTuple):
    a: float
    b: float
    c: float
    d: float
    material_idx: int


class Triangle(typing.NamedTuple):
    a: glm.vec3
    b: glm.vec3
    c: glm.vec3
    material_idx: int


class SceneLoader(LogicProvider):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__()

        self.shader = shader_program
        self.materials = self.define_materials_list()

        self.materials_SSBO = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.materials_SSBO)
        glBufferData(GL_SHADER_STORAGE_BUFFER, len(self.materials), self.materials, GL_STATIC_DRAW)
        index = glGetProgramResourceIndex(self.shader.program, GL_SHADER_STORAGE_BLOCK, "MaterialsBlock")
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, index, self.materials_SSBO)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0);


    @typing.final
    def render(self):
        super().render()

        spheres = self.spawn_spheres()
        planes = self.spawn_planes()
        triangles = self.spawn_triangles()

        glUniform1ui(glGetUniformLocation(
            self.shader.program, "materialsCount"), 1, GL_FALSE, glm.uint32(len(self.materials)))
        glUniform1ui(glGetUniformLocation(
            self.shader.program, "spheresCount"), 1, GL_FALSE, glm.uint32(len(spheres)))
        glUniform1ui(glGetUniformLocation(
            self.shader.program, "planesCount"), 1, GL_FALSE, glm.uint32(len(planes)))
        glUniform1ui(glGetUniformLocation(
            self.shader.program, "trianglesCount"), 1, GL_FALSE, glm.uint32(len(triangles)))

        # index = glGetUniformBlockIndex(self.shader.program, "materials")
        # print(index)
        # glBindBuffer(GL_UNIFORM_BUFFER, index)
        # glBufferData(index, self.materials, GL_UNIFORM_BUFFER)

        # uboExampleBlock = np.array([0], dtype=np.int32)
        # glGenBuffers(1, uboExampleBlock)
        # glBindBuffer(GL_UNIFORM_BUFFER, uboExampleBlock)
        # glBufferData(GL_UNIFORM_BUFFER, 152, None, GL_STATIC_DRAW)
        # glBindBuffer(GL_UNIFORM_BUFFER, 0)


    def define_materials_list(self):
        raise NotImplementedError()

    def spawn_spheres(self):
        return []

    def spawn_planes(self):
        return []

    def spawn_triangles(self):
        return []


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        arr = []

        for _ in range(200):
            arr.append(Material(glm.vec3(1.0, 1.0, 1.0), glm.vec3(1.0, 1.0, 1.0)))

        return np.array(arr)


    @typing.override
    def spawn_spheres(self):
        return []

    @typing.override
    def spawn_planes(self):
        return []

    @typing.override
    def spawn_triangles(self):
        return []
