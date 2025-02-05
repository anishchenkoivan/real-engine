import numpy as np
import engine
from graphics import *
from rotatingcube import RotatingCubeLogic


if __name__ == "__main__":
    engine = engine.Engine()
    vertex_shader = Shader("../shaders/vertex-shader.vert")
    fragment_shader = Shader("../shaders/fragment-shader.frag")
    shader = ShaderProgram(vertex_shader, fragment_shader)
    rotating_cube_logic = RotatingCubeLogic(shader)

    vertices = np.array([
        -0.5, -0.5, 0.0,  # Bottom-left
        0.5, -0.5, 0.0,  # Bottom-right
        0.5, 0.5, 0.0,  # Top-right
        -0.5, 0.5, 0.0  # Top-left
    ], dtype=np.float32)

    indices = np.array([
        0, 1, 2,  # First triangle
        2, 3, 0  # Second triangle
    ], dtype=np.uint32)

    mesh = Mesh(vertices, indices)
    renderer = Renderer(shader, mesh, rotating_cube_logic)
    engine.run(renderer)
