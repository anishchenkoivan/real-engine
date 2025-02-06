from math import radians

from graphics import *
from OpenGL.GL import *
import config
import engine
from pyglm import glm


def main():
    engine_instance = engine.Engine()
    vertex_shader = Shader("../shaders/simple-sphere.vert")
    fragment_shader = Shader("../shaders/simple-sphere.frag")
    shader = ShaderProgram(vertex_shader, fragment_shader)
    logic_provider = SimpleSphereLogicProvider(shader)

    # Cube vertices (positions + colors)
    vertices = np.array([
        -1.0, -1.0,
        1.0, -1.0,
        1.0, 1.0,

        1.0, 1.0,
        -1.0, 1.0,
        -1.0, -1.0,
    ], dtype=np.float32)

    mesh = VerticesMesh(vertices)
    renderer = Renderer(shader, MeshGroup(mesh), logic_provider)
    mouse_event_handler = MouseEventHandler(0.001, shader)
    engine_instance.mouse_event_handler = mouse_event_handler
    engine_instance.run(renderer)


class SimpleSphereLogicProvider(LogicProvider):
    def __init__(self, shader: ShaderProgram):
        super().__init__()
        self.shader = shader

    def render(self):
        glUniform2f(glGetUniformLocation(self.shader.program, "resolution"), config.RESOLUTION[0], config.RESOLUTION[1])


class VerticesMesh(Mesh):
    def __init__(self, attribute: np.array):
        super().__init__(attribute)

    def setup_vao(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.attribute, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * 4, None)
        glEnableVertexAttribArray(0)

    def draw(self):
        glDrawArrays(GL_TRIANGLES, 0, 6)


class MouseEventHandler:
    def __init__(self, sensitivity, shader: ShaderProgram):
        self.sensitivity = sensitivity
        self.shader = shader
        self.rotation_matrix = glm.mat3(1.0)

    def handle(self, movement):
        yaw, pitch = movement
        yaw *= self.sensitivity
        pitch *= self.sensitivity
        yaw_matrix = glm.rotate(glm.mat4(1.0), yaw, glm.vec3(0, 1, 0))
        pitch_matrix = glm.rotate(glm.mat4(1.0), pitch, glm.vec3(1, 0, 0))
        roll_matrix = glm.rotate(glm.mat4(1.0), 0.0, glm.vec3(0, 0, 1))
        self.rotation_matrix *= glm.mat3(yaw_matrix * pitch_matrix * roll_matrix)
        glUniformMatrix3fv(glGetUniformLocation(self.shader.program, "rotationMatrix"), 1, GL_FALSE, glm.value_ptr(self.rotation_matrix))
