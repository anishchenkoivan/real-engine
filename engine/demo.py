from scene import *


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        self.mirror = Material(Color(0.9, 0.0, 0.0), 0.02, self)
        self.metal = Material(Color(0.9, 0.9, 0.9), 0.02, self)
        self.black_metal = Material(Color(0.4, 0.4, 0.4), 0.02, self)
        self.glass = Material(Color(0.8, 0.8, 0.9), 0.0, self, transparent=True, optical_density=1.4, dispersion_coefficient=0.02)
        self.red_material = Material(Color(0.1, 0.8, 0.1), 0.0, self)

    @typing.override
    def spawn_spheres(self):
        return [
            Sphere(Vector(-2.0, 1.0, 13.0), 1.5, self.mirror),
            Sphere(Vector(1.0, -1.2, 13.0), 1.25, self.metal),
            Sphere(Vector(-6.0, 1.5, 13.0), 0.5, self.red_material),
        ]

    @typing.override
    def spawn_planes(self):
        return [
            Plane(0.0, 1.0, 0.0, 2.0, self.black_metal),
        ]

    @typing.override
    def spawn_triangles(self):
        return [
            Triangle(Vector(-1.0, 0.0, 10.0), Vector(-1.0, 1.0, 11.0),
                     Vector(3.0, 1.0, 10.0), self.black_metal),
            Triangle(Vector(-1.0, 1.0, 11.0), Vector(-1.0, 2.0, 10.0),
                     Vector(3.0, 1.0, 10.0), self.black_metal),
            Triangle(Vector(-1.0, 2.0, 10.0), Vector(-1.0, -1.0, 9.0),
                     Vector(3.0, 1.0, 10.0), self.black_metal),
            Triangle(Vector(-1.0, -1.0, 9.0), Vector(-1.0, 0.0, 10.0),
                     Vector(3.0, 1.0, 10.0), self.black_metal),
            Triangle(Vector(-1.0, 2.0, 10.0), Vector(-1.0, 1.0, 11.0),
                     Vector(-1.0, -1.0, 9.0), self.black_metal),

            # Kaleidoscope
            Triangle(Vector(-5.0, 0.0, 15.0), Vector(-5.0, 0.0, 11.0), Vector(-20.0, 0.0, 15.0), self.metal),
            Triangle(Vector(-20.0, 0.0, 15.0), Vector(-20.0, 0.0, 11.0), Vector(-5.0, 0.0, 11.0), self.metal),
            Triangle(Vector(-5.0, 0.0, 15.0), Vector(-20.0, 0.0, 15.0), Vector(-20.0, 3.46410161514, 13.0), self.metal),
            Triangle(Vector(-5.0, 0.0, 15.0), Vector(-5.0, 3.46410161514, 13.0), Vector(-20.0, 3.46410161514, 13.0), self.metal),
            Triangle(Vector(-5.0, 0.0, 11.0), Vector(-20.0, 0.0, 11.0), Vector(-20.0, 3.46410161514, 13.0), self.metal),
            Triangle(Vector(-5.0, 0.0, 11.0), Vector(-5.0, 3.46410161514, 13.0), Vector(-20.0, 3.46410161514, 13.0), self.metal),
        ]

    @typing.override
    def spawn_lenses(self):
        return [
            Lens(
                Sphere(Vector(1.0, 1.0, 20.0), 1.0, self.glass),
                Plane(0.0, 0.0, 1.0, -20.0, self.glass),
                self.glass,
            ),
            Lens(
                Sphere(Vector(1.0, 1.0, 5.0), 1.0, self.glass),
                Plane(0.0, 0.0, -1.0, 5.0, self.glass),
                self.glass,
            )
        ]

