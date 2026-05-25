from settings import *
from world_objects.chunk import Chunk
from terrain_gen import get_height
from voxel_handler import VoxelHandler

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)

    def _report_loading(self, progress, detail):
        if hasattr(self.app, 'loading_screen') and self.app.loading_screen:
            self.app.loading_screen.draw(progress, 'Generating world', detail)

    def update(self):
        self.voxel_handler.update()

    def is_water_body_at(self, x, z):
        return get_height(int(x), int(z)) < WATER_LINE

    def build_chunks(self):
        total = WORLD_VOL
        built = 0
        for x in range(WORLD_W):
            for y in range(WORLD_H):
                for z in range(WORLD_D):
                    chunk = Chunk(self, position=(x, y, z))

                    chunk_index = x + WORLD_W * z + WORLD_AREA * y
                    self.chunks[chunk_index] = chunk

                    self.voxels[chunk_index] = chunk.build_voxels()

                    chunk.voxels = self.voxels[chunk_index]

                    built += 1
                    if built % 12 == 0 or built == total:
                        progress = 0.35 + 0.40 * (built / total)
                        self._report_loading(progress, 'Building terrain')

    def build_chunk_mesh(self):
        total = len(self.chunks)
        for index, chunk in enumerate(self.chunks, start=1):
            chunk.build_mesh()
            if index % 12 == 0 or index == total:
                progress = 0.75 + 0.23 * (index / total)
                self._report_loading(progress, 'Uploading chunk meshes')

    def render(self):
        for chunk in self.chunks:
            chunk.render()