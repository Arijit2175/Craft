from settings import *
import moderngl as mgl
from world import World
from terrain_gen import get_height
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds

class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        spawn_y = get_height(int(CENTER_XZ), int(CENTER_XZ)) + 14
        self.app.player.position = glm.vec3(CENTER_XZ, spawn_y, CENTER_XZ)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water = Water(app)
        self.clouds = Clouds(app)

    def update(self):
        self.world.update()
        self.voxel_marker.update()
        self.clouds.update()

    def render(self):
        self.world.render()

        self.app.ctx.disable(mgl.CULL_FACE)
        self.clouds.render()
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        self.voxel_marker.render()