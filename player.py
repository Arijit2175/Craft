import math
import pygame as pg
from camera import Camera
from settings import *

class Player(Camera):
    PLAYER_HEIGHT = 1.8
    PLAYER_RADIUS = 0.35
    GRAVITY = -25.0
    JUMP_SPEED = 8.0
    COLLISION_STEP = 0.15

    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        self.velocity = glm.vec3(0, 0, 0)
        self.on_ground = False
        self.jump_was_pressed = False
        super().__init__(position, yaw, pitch)

    def update(self):
        was_on_ground = self.on_ground
        self.on_ground = False
        self.keyboard_control(was_on_ground)
        self.apply_gravity()
        self.move_and_collide(self.velocity.x * self.app.delta_time, 0)
        self.move_and_collide(self.velocity.z * self.app.delta_time, 2)
        self.move_and_collide(self.velocity.y * self.app.delta_time, 1)
        self.mouse_control()
        super().update()

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self, was_on_ground):
        key_state = pg.key.get_pressed()
        move_dir = glm.vec3(0, 0, 0)
        speed = PLAYER_SPEED * (PLAYER_SPRINT_MULT if key_state[pg.K_LSHIFT] or key_state[pg.K_RSHIFT] else 1.0)

        if key_state[pg.K_w]:
            move_dir += self.forward
        if key_state[pg.K_s]:
            move_dir -= self.forward
        if key_state[pg.K_d]:
            move_dir += self.right
        if key_state[pg.K_a]:
            move_dir -= self.right

        move_dir.y = 0
        if glm.length(move_dir) > 0:
            move_dir = glm.normalize(move_dir) * speed

        self.velocity.x = move_dir.x
        self.velocity.z = move_dir.z

        jump_pressed = key_state[pg.K_SPACE]
        if jump_pressed and not self.jump_was_pressed and was_on_ground:
            self.velocity.y = self.JUMP_SPEED
        self.jump_was_pressed = jump_pressed

    def apply_gravity(self):
        self.velocity.y += self.GRAVITY * self.app.delta_time
        self.velocity.y = max(self.velocity.y, -50.0)

    def move_and_collide(self, amount, axis):
        if amount == 0:
            return

        steps = max(1, int(abs(amount) / self.COLLISION_STEP) + 1)
        step_amount = amount / steps

        for _ in range(steps):
            new_position = glm.vec3(self.position)
            if axis == 0:
                new_position.x += step_amount
            elif axis == 1:
                new_position.y += step_amount
            else:
                new_position.z += step_amount

            if self.collides_at(new_position):
                if axis == 1 and step_amount < 0:
                    self.on_ground = True

                if axis == 0:
                    self.velocity.x = 0
                elif axis == 1:
                    self.velocity.y = 0
                else:
                    self.velocity.z = 0
                return

            self.position = new_position

    def collides_at(self, position):
        world = self.app.scene.world
        max_world_x = WORLD_W * CHUNK_SIZE
        max_world_y = WORLD_H * CHUNK_SIZE
        max_world_z = WORLD_D * CHUNK_SIZE

        sample_x = (math.floor(position.x - self.PLAYER_RADIUS), math.floor(position.x), math.floor(position.x + self.PLAYER_RADIUS))
        sample_y = (math.floor(position.y - self.PLAYER_HEIGHT), math.floor(position.y))
        sample_z = (math.floor(position.z - self.PLAYER_RADIUS), math.floor(position.z), math.floor(position.z + self.PLAYER_RADIUS))

        for x in sample_x:
            for y in sample_y:
                for z in sample_z:
                    if x < 0 or y < 0 or z < 0 or x >= max_world_x or y >= max_world_y or z >= max_world_z:
                        return True

                    cx = x // CHUNK_SIZE
                    cy = y // CHUNK_SIZE
                    cz = z // CHUNK_SIZE
                    chunk_index = cx + WORLD_W * cz + WORLD_AREA * cy
                    chunk_voxels = world.voxels[chunk_index]

                    lx = x % CHUNK_SIZE
                    ly = y % CHUNK_SIZE
                    lz = z % CHUNK_SIZE
                    voxel_index = lx + CHUNK_SIZE * lz + CHUNK_AREA * ly
                    if chunk_voxels[voxel_index]:
                        return True
        return False

    def is_on_ground(self):
        probe = glm.vec3(self.position.x, self.position.y - 0.05, self.position.z)
        return self.collides_at(probe)