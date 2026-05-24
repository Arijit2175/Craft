from meshes.sky_mesh import SkyMesh


class Sky:
    def __init__(self, app):
        self.app = app
        self.mesh = SkyMesh(app)

    def render(self):
        self.mesh.render()