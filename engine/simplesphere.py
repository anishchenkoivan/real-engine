from graphics import *
from OpenGL.GL import *
import config
import engine


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
    mouse_event_handler = MouseEventHandler(0.05, shader)
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
