from meshes.water_surface_mesh import WaterSurfaceMesh

class Water:
    def __init__(self, world):
        self.world = world
        self.app = world.app
        self.mesh = WaterSurfaceMesh(world)

    def render(self):
        self.mesh.render()