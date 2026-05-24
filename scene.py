from settings import *
import moderngl as mgl
import math
from world import World
from terrain_gen import get_height
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds
from world_objects.crosshair import Crosshair
from world_objects.sky import Sky

class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        spawn_y = get_height(int(CENTER_XZ), int(CENTER_XZ)) + 14
        self.app.player.position = glm.vec3(CENTER_XZ, spawn_y, CENTER_XZ)
        self.time_of_day = DAY_NIGHT_START_OFFSET
        self.daylight = 1.0
        self.sky_color = glm.vec3(BG_COLOR)
        self.sky = Sky(app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water = Water(self.world)
        self.clouds = Clouds(app)
        self.crosshair = Crosshair(app)

    def update_day_night(self):
        self.time_of_day = (self.app.time / DAY_NIGHT_CYCLE_SECONDS + DAY_NIGHT_START_OFFSET) % 1.0
        sun_angle = self.time_of_day * math.tau - (math.pi * 0.5)
        sun_height = math.sin(sun_angle)

        daylight = max(0.0, sun_height)
        twilight = max(0.0, 1.0 - abs(sun_height) * 3.0)

        day_sky = glm.vec3(BG_COLOR)
        night_sky = glm.vec3(NIGHT_SKY_COLOR)
        dawn_sky = glm.vec3(DAWN_SKY_COLOR)

        sky_color = glm.mix(night_sky, day_sky, daylight)
        sky_color = glm.mix(sky_color, dawn_sky, twilight)

        self.daylight = NIGHT_AMBIENT_LIGHT + (DAY_AMBIENT_LIGHT - NIGHT_AMBIENT_LIGHT) * (daylight ** 1.2)
        self.sky_color = sky_color

    def update(self):
        self.update_day_night()
        self.world.update()
        self.voxel_marker.update()
        self.clouds.update()

    def render(self):
        self.app.ctx.disable(mgl.DEPTH_TEST)
        self.sky.render()
        self.app.ctx.enable(mgl.DEPTH_TEST)

        self.world.render()

        self.app.ctx.disable(mgl.CULL_FACE)
        self.clouds.render()
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        self.voxel_marker.render()

        self.app.ctx.disable(mgl.DEPTH_TEST)
        self.crosshair.render()
        self.app.ctx.enable(mgl.DEPTH_TEST)