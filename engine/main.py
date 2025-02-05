import engine
from simplesphere import *


if __name__ == "__main__":
    engine = engine.Engine()
    vertex_shader = Shader("../shaders/vertex-shader.vert")
    fragment_shader = Shader("../shaders/fragment-shader.frag")
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
    engine.run(renderer)
