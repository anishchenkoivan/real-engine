import OpenGL.GL.shaders
import numpy as np
from OpenGL.GL import *
import ctypes

class Shader:
    shader_type = {
        "vert": GL_VERTEX_SHADER,
        "frag": GL_FRAGMENT_SHADER,
    }

    def __init__(self, shader_src_path, shader_type=None):
        if shader_type is None:
            shader_type = self.shader_type[shader_src_path.split(".")[-1]]

        with open(shader_src_path, 'r') as f:
            shader_src = f.read()
        self.shader = OpenGL.GL.shaders.compileShader(shader_src, shader_type)


class ShaderProgram:
    def __init__(self, *shaders: Shader):
        self.shaders = shaders
        self.program = OpenGL.GL.shaders.compileProgram(*[shader.shader for shader in shaders])

    def use(self):
        glUseProgram(self.program)


class Mesh:
    def __init__(self, attribute: np.array):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)
        self.attribute = attribute
        glBindVertexArray(self.VAO)
        self.setup_vao()

    def setup_vao(self):
        pass

    def draw(self):
        pass


class MeshGroup:
    def __init__(self, *meshes: Mesh):
        self.meshes = meshes

    def draw(self):
        for mesh in self.meshes:
            mesh.draw()


class LogicProvider:
    def __init__(self):
        pass

    def render(self):
        pass


class Renderer:
    def __init__(self, shader_program: ShaderProgram, mesh: MeshGroup, logic_provider=None):
        self.shader = shader_program
        self.mesh = mesh
        self.logic_provider = logic_provider

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        self.logic_provider.render()
        self.mesh.draw()


class EventHandler:
    def __init__(self):
        pass

    def handle_event(self, event):
        pass