import numpy as np

from meshes.base_mesh import BaseMesh

class CrosshairMesh(BaseMesh):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.crosshair
        self.vbo_format = '2f 3f'
        self.attrs = ('in_position', 'in_color')
        self.vao = self.get_vao()

    def get_vertex_data(self):
        size = 0.016
        thickness = 0.003
        color = (1.0, 1.0, 1.0)

        vertices = [
            # horizontal bar
            (-size, -thickness, *color),
            ( size, -thickness, *color),
            ( size,  thickness, *color),
            (-size, -thickness, *color),
            ( size,  thickness, *color),
            (-size,  thickness, *color),

            # vertical bar
            (-thickness, -size, *color),
            ( thickness, -size, *color),
            ( thickness,  size, *color),
            (-thickness, -size, *color),
            ( thickness,  size, *color),
            (-thickness,  size, *color),
        ]

        return np.array(vertices, dtype='float32')