import numpy as np

from meshes.base_mesh import BaseMesh
from terrain_gen import get_height
from settings import *

class WaterSurfaceMesh(BaseMesh):
    def __init__(self, world):
        super().__init__()
        self.world = world
        self.app = world.app
        self.ctx = self.app.ctx
        self.program = self.app.shader_program.water

        self.vbo_format = '2f 3f'
        self.attrs = ('in_tex_coord', 'in_position')
        self.vao = self.get_vao()

    def rebuild(self):
        self.vao = self.get_vao()

    def get_vertex_data(self):
        vertices = []
        world_width = WORLD_W * CHUNK_SIZE
        world_depth = WORLD_D * CHUNK_SIZE
        mask = np.zeros((world_width, world_depth), dtype=np.uint8)
        visited = np.zeros((world_width, world_depth), dtype=np.uint8)

        for x in range(world_width):
            for z in range(world_depth):
                mask[x, z] = 1 if get_height(x, z) < WATER_LINE else 0

        for z in range(world_depth):
            x = 0
            while x < world_width:
                if not mask[x, z] or visited[x, z]:
                    x += 1
                    continue

                x_end = x + 1
                while x_end < world_width and mask[x_end, z] and not visited[x_end, z]:
                    x_end += 1

                z_end = z + 1
                can_grow = True
                while z_end < world_depth and can_grow:
                    for ix in range(x, x_end):
                        if not mask[ix, z_end] or visited[ix, z_end]:
                            can_grow = False
                            break
                    if can_grow:
                        z_end += 1

                for ix in range(x, x_end):
                    visited[ix, z:z_end] = 1

                y = WATER_SURFACE_Y
                u0 = x * WATER_UV_SCALE
                v0 = z * WATER_UV_SCALE
                u1 = x_end * WATER_UV_SCALE
                v1 = z_end * WATER_UV_SCALE

                vertices.extend([
                    u0, v0, x, y, z,
                    u1, v0, x_end, y, z,
                    u1, v1, x_end, y, z_end,
                    u0, v0, x, y, z,
                    u1, v1, x_end, y, z_end,
                    u0, v1, x, y, z_end,
                ])

                x = x_end

        if not vertices:
            return np.zeros(5, dtype='float32')

        return np.array(vertices, dtype='float32')