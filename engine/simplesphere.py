from graphics import *
from OpenGL.GL import *
import config
import engine
import typing
from scene import *


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
    movement_event_handler = MovementEventHandler(shader, 0.05, 0.05)
    engine_instance.movement_event_handler = movement_event_handler
    engine_instance.run(renderer)


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        self.mt2 = Material(Color(1.0, 0.0, 1.0), Color(0.1, 0.1, 0.1), self)
        self.mt1 = Material(Color(1.0, 0.0, 1.0), Color(0.3, 0.3, 0.3), self)
        self.mt3 = Material(Color(0.4, 0.4, 0.4), Color(0.4, 0.4, 0.4), self)
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


class SimpleSphereLogicProvider(LogicProvider):
    def __init__(self, shader: ShaderProgram):
        super().__init__()
        self.shader = shader
        self.scene_loader = ExampleSceneLoader(shader)

    def render(self):
        self.scene_loader.render()
        glUniform2f(glGetUniformLocation(self.shader.program,
                    "resolution"), config.RESOLUTION[0], config.RESOLUTION[1])


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
