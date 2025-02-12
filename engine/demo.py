from scene import *


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        self.mt1 = Material(Color(0.9, 0.0, 0.0), Color(0.0, 0.0, 0.0), self)
        self.mt2 = Material(Color(0.9, 0.9, 0.9), Color(0.5, 0.5, 0.5), self)
        self.mt3 = Material(Color(0.4, 0.4, 0.4), Color(0.2, 0.2, 0.2), self)
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


