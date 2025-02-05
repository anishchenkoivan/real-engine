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

    # Cube vertices (positions + colors)
    vertices = np.array([
        # Front Face
        -0.5, -0.5, 0.5, 1, 0, 0,  # Bottom-left (red)
        0.5, -0.5, 0.5, 0, 1, 0,  # Bottom-right (green)
        0.5, 0.5, 0.5, 0, 0, 1,  # Top-right (blue)
        -0.5, 0.5, 0.5, 1, 1, 0,  # Top-left (yellow)

        # Back Face
        -0.5, -0.5, -0.5, 1, 0, 1,
        0.5, -0.5, -0.5, 0, 1, 1,
        0.5, 0.5, -0.5, 1, 1, 1,
        -0.5, 0.5, -0.5, 0, 0, 0,
    ], dtype=np.float32)

    # Indices for cube faces
    indices = np.array([
        0, 1, 2, 2, 3, 0,  # Front
        4, 5, 6, 6, 7, 4,  # Back
        0, 3, 7, 7, 4, 0,  # Left
        1, 5, 6, 6, 2, 1,  # Right
        3, 2, 6, 6, 7, 3,  # Top
        0, 1, 5, 5, 4, 0,  # Bottom
    ], dtype=np.uint32)

    mesh = Mesh(vertices, indices)
    renderer = Renderer(shader, mesh, rotating_cube_logic)
    engine.run(renderer)
