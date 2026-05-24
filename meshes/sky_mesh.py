import numpy as np

from meshes.base_mesh import BaseMesh

class SkyMesh(BaseMesh):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.sky
        self.vbo_format = '2f'
        self.attrs = ('in_position',)
        self.vao = self.get_vao()

    def get_vertex_data(self):
        vertices = [
            (-1.0, -1.0),
            (1.0, -1.0),
            (1.0, 1.0),
            (-1.0, -1.0),
            (1.0, 1.0),
            (-1.0, 1.0),
        ]
        return np.array(vertices, dtype='float32')