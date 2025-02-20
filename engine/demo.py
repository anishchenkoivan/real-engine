from scene import *


class ExampleSceneLoader(SceneLoader):
    def __init__(self, shader_program: ShaderProgram):
        super().__init__(shader_program)

    @typing.override
    def define_materials_list(self):
        self.mt1 = Material(Color(0.9, 0.0, 0.0), 0.02, self)
        self.mt2 = Material(Color(0.9, 0.9, 0.9), 0.02, self)
        self.mt3 = Material(Color(0.4, 0.4, 0.4), 0.2, self)
        self.mt4 = Material(Color(0.8, 0.8, 0.9), 0.0, self, transparent=True,
                            optical_density=1.4, dispersion_coefficient=0.01)
        self.light = Material(Color(1.0, 1.0, 1.0), 0.0, self, light=True)

    @typing.override
    def spawn_spheres(self):
        return [
            Sphere(Vector(1.0, -1.2, 13.0), 1.25, self.light),
            Sphere(Vector(-2.0, -1.0, -13.0), 1.5, self.light)
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
                     Vector(-1.0, -1.0, 9.0), self.mt3),
        ]

    @typing.override
    def spawn_lenses(self):
        return [
            Lens(
                Sphere(Vector(1.0, 1.0, 20.0), 1.0, self.mt4),
                Plane(0.0, 0.0, 1.0, -20.0, self.mt4),
                self.mt4,
            ),
            Lens(
                Sphere(Vector(1.0, 1.0, 5.0), 1.0, self.mt4),
                Plane(0.0, 0.0, -1.0, 5.0, self.mt4),
                self.mt4,
            )
        ]

    @typing.override
    def spawn_lights(self):
        return [
            Light(Color(1.0, 1.0, 1.0), Vector(-2.0, 1.0, 13.0))
        ]

    # @typing.override
    # def sky_config(self):
    #     return SkyConfig(Vector(1.0, 1.0, 1.0), 0.0, Color(0.0, 0.0, 0.0), Color(0.0, 0.0, 0.0))
