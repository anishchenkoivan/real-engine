from graphics import LogicProvider, ShaderProgram
from pyglm import glm
from OpenGL.GL import *


class RotatingCubeLogic(LogicProvider):
    def __init__(self, shader: ShaderProgram):
        super().__init__()
        self.shader = shader

        self.projection = glm.perspective(glm.radians(45), 1920 / 1080, 0.1, 10.0)
        self.view = glm.translate(glm.mat4(1), glm.vec3(0, 0, -3))
        self.angle = 0

    def render(self):
        self.angle += 1
        model = glm.rotate(glm.mat4(1), glm.radians(self.angle), glm.vec3(0, 1, 0))

        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "projection"), 1, GL_FALSE, glm.value_ptr(self.projection))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "view"), 1, GL_FALSE, glm.value_ptr(self.view))
