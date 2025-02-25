from typing import override
from buffers import Buffers
from graphics import *
from OpenGL.GL import *
import config
import engine
from scene import *
import random


def main(scene_loader):
    engine_instance = engine.Engine()
    vertex_shader = Shader("../shaders/render.vert")
    fragment_shader = Shader("../shaders/render.frag")
    shader = ShaderProgram(vertex_shader, fragment_shader)
    logic_provider = LogicProviderImpl(shader, scene_loader)

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
    movement_event_handler_wrapper = MovementEventHandlerWrapper(movement_event_handler, logic_provider)
    engine_instance.movement_event_handler = movement_event_handler_wrapper
    engine_instance.run(renderer)


class LogicProviderImpl(LogicProvider):
    def __init__(self, shader: ShaderProgram, scene_loader):
        super().__init__()
        self.shader = shader
        self.scene_loader = scene_loader(shader)
        self.prev_frame_ssbo = glGenBuffers(1)
        self.mixed_frames = 0

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.prev_frame_ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, config.RESOLUTION[0] * config.RESOLUTION[1] * 4 * 4, None, GL_DYNAMIC_DRAW)  # Allocate memory
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, Buffers.FRAME_BUFFER.value, self.prev_frame_ssbo)

    def render(self):
        self.scene_loader.render()
        glUniform2f(glGetUniformLocation(self.shader.program,
                                         "resolution"), config.RESOLUTION[0], config.RESOLUTION[1])
        glUniform1f(glGetUniformLocation(
            self.shader.program, "rand1"), random.random())
        glUniform1f(glGetUniformLocation(
            self.shader.program, "rand2"), random.random())
        glUniform1f(glGetUniformLocation(
            self.shader.program, "blending_alpha"), self.blending_alpha)
        self.mixed_frames += 1

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.prev_frame_ssbo)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)  # Ensure synchronization

    def drop_mixed_frames(self):
        self.mixed_frames = 0

    @property
    def blending_alpha(self):
        return float(self.mixed_frames) / float(self.mixed_frames + 1)


class MovementEventHandlerWrapper(MovementEventHandler):
    def __init__(self, event_handler, logic_provider):
        self.event_handler = event_handler
        self.logic_provider = logic_provider

    @override
    def handle_mouse_event(self, movement):
        self.event_handler.handle_mouse_event(movement)
        self.logic_provider.drop_mixed_frames()

    @override
    def handle_keydown_event(self):
        self.event_handler.handle_mouse_event()
        self.logic_provider.drop_mixed_frames()


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
