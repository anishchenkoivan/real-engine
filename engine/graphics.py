import OpenGL.GL.shaders
import numpy as np
import pygame
from OpenGL.GL import *
from pygame.event import Event
from pyglm import glm

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


class MovementEventHandler:
    def __init__(self, shader, mouse_sensitivity, keyboard_sensitivity):
        self.sensitivity = mouse_sensitivity
        self.shader = shader
        self.rotation_quat = glm.quat(1, 0, 0, 0)

        self.keyboard_sensitivity = keyboard_sensitivity
        self.position_vec = glm.vec3(0, 0, -1)

    def handle_mouse_event(self, movement):
        yaw, pitch = movement
        yaw *= self.sensitivity
        pitch *= self.sensitivity
        yaw = glm.radians(yaw)
        pitch = glm.radians(pitch)

        yaw_quat = glm.angleAxis(yaw, glm.vec3(0, 1, 0))
        self.rotation_quat = yaw_quat * self.rotation_quat
        right_vector = glm.normalize(self.rotation_quat * glm.vec3(1, 0, 0))
        pitch_quat = glm.angleAxis(pitch, right_vector)
        self.rotation_quat = pitch_quat * self.rotation_quat

        rotation_matrix = glm.mat3_cast(self.rotation_quat)
        glUniformMatrix3fv(glGetUniformLocation(self.shader.program, "rotationMatrix"), 1, GL_FALSE, glm.value_ptr(rotation_matrix))

    def handle_keydown_event(self, event: Event):
        forward = glm.normalize(self.rotation_quat * glm.vec3(0, 0, 1))
        right = glm.normalize(self.rotation_quat * glm.vec3(1, 0, 0))
        up = glm.vec3(0, 1, 0)

        if event.key == pygame.K_w:
            self.position_vec += forward * self.keyboard_sensitivity
        elif event.key == pygame.K_s:
            self.position_vec -= forward * self.keyboard_sensitivity
        elif event.key == pygame.K_a:
            self.position_vec -= right * self.keyboard_sensitivity
        elif event.key == pygame.K_d:
            self.position_vec += right * self.keyboard_sensitivity
        elif event.key == pygame.K_SPACE:
            self.position_vec += up * self.keyboard_sensitivity
        elif event.key == pygame.K_LSHIFT:
            self.position_vec -= up * self.keyboard_sensitivity

        glUniform3fv(glGetUniformLocation(self.shader.program, "position"), 1, glm.value_ptr(self.position_vec))
