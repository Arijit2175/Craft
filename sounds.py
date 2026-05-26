import pygame as pg
import math
import glm
from settings import *
from resource_utils import resource_path

class MovementAudio:
    LOOP_FADE_MS = 140

    def __init__(self, app):
        self.app = app
        self.enabled = pg.mixer.get_init() is not None
        self.last_surface_key = None
        self.current_loop_key = None
        self.step_channel = None
        self.swim_channel = None
        self.land_channel = None

        self.sounds = {}
        if self.enabled:
            pg.mixer.set_num_channels(max(pg.mixer.get_num_channels(), 8))
            self.sounds = {
                'grass': self.load('walking_grass.mp3', 0.55),
                'stone': self.load('walking_stone.mp3', 0.55),
                'sand': self.load('walking_sand.mp3', 0.55),
                'snow': self.load('walking_snow.mp3', 0.55),
                'swim': self.load('swimming.mp3', 0.45),
            }
            self.step_channel = pg.mixer.Channel(0)
            self.swim_channel = pg.mixer.Channel(1)
            self.land_channel = pg.mixer.Channel(2)

    def load(self, file_name, volume):
        sound = pg.mixer.Sound(resource_path(f'assets/{file_name}'))
        sound.set_volume(volume)
        return sound

    def play(self, key):
        if not self.enabled:
            return
        sound = self.sounds.get(key)
        if sound:
            if key == 'land':
                self.land_channel.play(sound)

    def start_loop(self, key):
        if not self.enabled:
            return

        channel = self.swim_channel if key == 'swim' else self.step_channel
        if self.current_loop_key == key and channel.get_busy():
            return

        sound = self.sounds.get(key)
        if not sound:
            return

        if self.current_loop_key == 'swim' and self.swim_channel.get_busy():
            self.swim_channel.fadeout(self.LOOP_FADE_MS)
        elif self.current_loop_key != 'swim' and self.step_channel.get_busy():
            self.step_channel.fadeout(self.LOOP_FADE_MS)

        channel.play(sound, loops=-1, fade_ms=self.LOOP_FADE_MS)
        self.current_loop_key = key

    def stop_loop(self):
        if not self.enabled:
            return

        if self.step_channel.get_busy():
            self.step_channel.fadeout(self.LOOP_FADE_MS)
        if self.swim_channel.get_busy():
            self.swim_channel.fadeout(self.LOOP_FADE_MS)
        self.current_loop_key = None

    def update(self, player, delta_time, was_on_ground, pre_move_vertical_velocity, movement_input_active):
        if not self.enabled:
            return

        current_water_state = player.get_water_state()

        if not movement_input_active:
            self.last_surface_key = None
            self.stop_loop()
            if (not was_on_ground and player.on_ground and pre_move_vertical_velocity < -0.15 and current_water_state == 0):
                self.play('land')
            return

        if current_water_state > 0:
            self.start_loop('swim')
            self.last_surface_key = 'swim'
        else:
            surface_key = self.get_surface_key(player)
            if surface_key != self.last_surface_key:
                self.last_surface_key = surface_key
                self.start_loop(surface_key)
            elif self.current_loop_key != surface_key:
                self.start_loop(surface_key)

            if (not was_on_ground and player.on_ground and pre_move_vertical_velocity < -0.15 and current_water_state == 0):
                self.play('land')

    def get_surface_key(self, player):
        world = self.app.scene.world
        x = int(math.floor(player.position.x))
        z = int(math.floor(player.position.z))
        feet_y = int(math.floor(player.position.y - player.PLAYER_HEIGHT - 0.08))

        for offset in range(0, 4):
            y = feet_y - offset
            if y < 0:
                break

            voxel_id = self.get_voxel_id(world, x, y, z)
            if voxel_id == 0:
                continue
            if voxel_id in (GRASS, DIRT):
                return 'grass'
            if voxel_id in (SAND,):
                return 'sand'
            if voxel_id in (SNOW,):
                return 'snow'
            if voxel_id in (STONE, ROCK, COAL_ORE, IRON_ORE, BEDROCK):
                return 'stone'
            return 'stone'

        return 'stone'

    def get_voxel_id(self, world, wx, wy, wz):
        max_world_x = WORLD_W * CHUNK_SIZE
        max_world_y = WORLD_H * CHUNK_SIZE
        max_world_z = WORLD_D * CHUNK_SIZE
        if wx < 0 or wy < 0 or wz < 0 or wx >= max_world_x or wy >= max_world_y or wz >= max_world_z:
            return 0

        cx = wx // CHUNK_SIZE
        cy = wy // CHUNK_SIZE
        cz = wz // CHUNK_SIZE
        chunk_index = cx + WORLD_W * cz + WORLD_AREA * cy
        chunk_voxels = world.voxels[chunk_index]

        lx = wx % CHUNK_SIZE
        ly = wy % CHUNK_SIZE
        lz = wz % CHUNK_SIZE
        voxel_index = lx + CHUNK_SIZE * lz + CHUNK_AREA * ly
        return int(chunk_voxels[voxel_index])


def play_background_music(file_name='bg_music.ogg', volume=0.18):
    if pg.mixer.get_init() is None:
        return

    try:
        pg.mixer.music.load(resource_path(f'assets/{file_name}'))
        pg.mixer.music.set_volume(volume)
        pg.mixer.music.play(-1)
    except pg.error:
        pass