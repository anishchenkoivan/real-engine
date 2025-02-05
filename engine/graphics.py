import OpenGL.GL.shaders
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
    def __init__(self, vertices, indices):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)
        self.vertices = vertices
        self.indices = indices
        self.setup_vao()

    def setup_vao(self):
        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def bind_vao(self):
        glBindVertexArray(self.VAO)

    def unbind_vao(self):
        glBindVertexArray(0)

    def draw(self):
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)


class LogicProvider:
    def __init__(self):
        pass

    def render(self):
        pass


class Renderer:
    def __init__(self, shader_program, mesh, logic_provider=None):
        self.shader = shader_program
        self.mesh = mesh
        self.logic_provider = logic_provider

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.shader.use()
        self.mesh.bind_vao()
        self.logic_provider.render()
        self.mesh.draw()
        self.mesh.unbind_vao()
