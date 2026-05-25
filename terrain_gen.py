from numba import njit
from noise import noise2, noise3
from random import random
import math
import settings as cfg

SNOW_LVL = int(cfg.SNOW_LVL)
STONE_LVL = int(cfg.STONE_LVL)
DIRT_LVL = int(cfg.DIRT_LVL)
GRASS_LVL = int(cfg.GRASS_LVL)
SAND_LVL = int(cfg.SAND_LVL)
SAND = int(cfg.SAND)
GRASS = int(cfg.GRASS)
DIRT = int(cfg.DIRT)
STONE = int(cfg.STONE)
SNOW = int(cfg.SNOW)
LEAVES = int(cfg.LEAVES)
ALT_LEAVES = int(cfg.ALT_LEAVES)
WOOD = int(cfg.WOOD)
ROCK = int(cfg.ROCK)
COAL_ORE = int(cfg.COAL_ORE)
IRON_ORE = int(cfg.IRON_ORE)
BEDROCK = int(cfg.BEDROCK)
CENTER_XZ = int(cfg.CENTER_XZ)
CENTER_Y = int(cfg.CENTER_Y)
CHUNK_SIZE = int(cfg.CHUNK_SIZE)
CHUNK_AREA = int(cfg.CHUNK_AREA)
TREE_PROBABILITY = float(cfg.TREE_PROBABILITY)
CHERRY_LEAF_VARIANT_CHANCE = float(cfg.CHERRY_LEAF_VARIANT_CHANCE)
TREE_WIDTH = int(cfg.TREE_WIDTH)
TREE_HEIGHT = int(cfg.TREE_HEIGHT)
TREE_H_WIDTH = int(cfg.TREE_H_WIDTH)
TREE_H_HEIGHT = int(cfg.TREE_H_HEIGHT)
CAVE_SURFACE_BUFFER = float(cfg.CAVE_SURFACE_BUFFER)
CAVE_FREQUENCY = float(cfg.CAVE_FREQUENCY)
CAVE_THRESHOLD = float(cfg.CAVE_THRESHOLD)
CAVE_MOUTH_FREQUENCY = float(cfg.CAVE_MOUTH_FREQUENCY)
CAVE_MOUTH_THRESHOLD = float(cfg.CAVE_MOUTH_THRESHOLD)
CAVE_MOUTH_DEPTH = int(cfg.CAVE_MOUTH_DEPTH)
CAVE_MOUTH_DEPTH_BONUS = int(cfg.CAVE_MOUTH_DEPTH_BONUS)
CAVE_MOUTH_MOUNTAIN_BONUS = float(cfg.CAVE_MOUTH_MOUNTAIN_BONUS)
CAVE_COVER_THICKNESS = int(cfg.CAVE_COVER_THICKNESS)
ORE_FREQUENCY = float(cfg.ORE_FREQUENCY)
ORE_CLUSTER_FREQUENCY = float(cfg.ORE_CLUSTER_FREQUENCY)
ORE_CLUSTER_THRESHOLD = float(cfg.ORE_CLUSTER_THRESHOLD)
ORE_COAL_THRESHOLD = float(cfg.ORE_COAL_THRESHOLD)
ORE_IRON_THRESHOLD = float(cfg.ORE_IRON_THRESHOLD)
ORE_MIN_DEPTH = int(cfg.ORE_MIN_DEPTH)
ORE_CAVE_BONUS = float(cfg.ORE_CAVE_BONUS)
ROCK_DEPTH = int(cfg.ROCK_DEPTH)
ROCK_FREQUENCY = float(cfg.ROCK_FREQUENCY)
ROCK_THRESHOLD = float(cfg.ROCK_THRESHOLD)
BEDROCK_LAYER = int(cfg.BEDROCK_LAYER)
BASE_ROCK_LAYER = int(cfg.BASE_ROCK_LAYER)
BASE_ROCK_LAYER = int(cfg.BASE_ROCK_LAYER)


@njit
def get_height(x, z):
    island = 1 / (pow(0.0025 * math.hypot(x - CENTER_XZ, z - CENTER_XZ), 20) + 0.0001)
    island = min(island, 1)

    a1 = CENTER_Y
    a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125

    f1 = 0.005
    f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8

    if noise2(0.1 * x, 0.1 * z) < 0:
        a1 /= 1.07

    height = 0
    height += noise2(x * f1, z * f1) * a1 + a1
    height += noise2(x * f2, z * f2) * a2 - a2
    height += noise2(x * f4, z * f4) * a4 + a4
    height += noise2(x * f8, z * f8) * a8 - a8

    height = max(height,  noise2(x * f8, z * f8) + 2)
    height *= island

    return int(height)


@njit
def get_index(x, y, z):
    return x + CHUNK_SIZE * z + CHUNK_AREA * y

@njit
def get_cave_value(wx, wy, wz):
    cave = noise3(wx * CAVE_FREQUENCY, wy * CAVE_FREQUENCY, wz * CAVE_FREQUENCY)
    cave += 0.5 * noise3(wx * CAVE_FREQUENCY * 1.8, wy * CAVE_FREQUENCY * 1.8, wz * CAVE_FREQUENCY * 1.8)
    return cave

@njit
def get_cave_mouth_value(wx, wz):
    mouth = noise2(wx * CAVE_MOUTH_FREQUENCY, wz * CAVE_MOUTH_FREQUENCY)
    mouth += 0.42 * noise2(wx * CAVE_MOUTH_FREQUENCY * 2.11, wz * CAVE_MOUTH_FREQUENCY * 2.11)
    return mouth


@njit
def get_rock_value(wx, wy, wz):
    rock = noise3(wx * ROCK_FREQUENCY, wy * ROCK_FREQUENCY, wz * ROCK_FREQUENCY)
    rock += 0.4 * noise3(wx * ROCK_FREQUENCY * 2.1, wy * ROCK_FREQUENCY * 2.1, wz * ROCK_FREQUENCY * 2.1)
    return rock

@njit
def get_ore_value(wx, wy, wz):
    return noise3(wx * ORE_FREQUENCY, wy * ORE_FREQUENCY, wz * ORE_FREQUENCY)


@njit
def get_ore_cluster_value(wx, wy, wz):
    cluster = noise3(wx * ORE_CLUSTER_FREQUENCY, wy * ORE_CLUSTER_FREQUENCY, wz * ORE_CLUSTER_FREQUENCY)
    cluster += 0.45 * noise3(wx * ORE_CLUSTER_FREQUENCY * 1.87, wy * ORE_CLUSTER_FREQUENCY * 1.87, wz * ORE_CLUSTER_FREQUENCY * 1.87)
    return cluster

@njit
def set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height, cave_mouth, mountain_factor):
    voxel_id = BEDROCK if wy <= BEDROCK_LAYER else ROCK if wy <= BASE_ROCK_LAYER else 0

    if voxel_id:
        voxels[get_index(x, y, z)] = voxel_id
        return

    if wy < world_height - 1:
        depth = world_height - wy
        cave_value = get_cave_value(wx, wy, wz)
        cave_depth_limit = CAVE_MOUTH_DEPTH + int(mountain_factor * CAVE_MOUTH_DEPTH_BONUS)
        cave_threshold = CAVE_MOUTH_THRESHOLD - mountain_factor * CAVE_MOUTH_MOUNTAIN_BONUS
        near_surface_cave = cave_mouth > cave_threshold and depth <= cave_depth_limit
        cave_body_threshold = CAVE_THRESHOLD - mountain_factor * 0.08
        depth_falloff = 1.0 - min(1.0, depth / max(cave_depth_limit, 1))
        cave_profile = cave_value + depth_falloff * (0.55 + mountain_factor * 0.18)

        if depth > CAVE_SURFACE_BUFFER and depth > CAVE_COVER_THICKNESS and cave_profile > cave_body_threshold:
            voxel_id = 0
        elif depth > ROCK_DEPTH:
            voxel_id = ROCK if get_rock_value(wx, wy, wz) > ROCK_THRESHOLD else STONE

            ore_cluster = get_ore_cluster_value(wx, wy, wz)
            ore_value = get_ore_value(wx, wy, wz) + ore_cluster * 0.35
            ore_bonus = ORE_CAVE_BONUS if abs(cave_profile - cave_body_threshold) < 0.18 else 0.0
            if depth > ORE_MIN_DEPTH and ore_cluster > ORE_CLUSTER_THRESHOLD - ore_bonus:
                if ore_value > ORE_COAL_THRESHOLD - ore_bonus:
                    voxel_id = COAL_ORE
                elif ore_value < -ORE_IRON_THRESHOLD + ore_bonus:
                    voxel_id = IRON_ORE

            if voxel_id == STONE and cave_profile > cave_body_threshold and ore_cluster > ORE_CLUSTER_THRESHOLD - 0.08:
                voxel_id = ROCK
        else:
            voxel_id = STONE
    else:
        rng = int(7 * random())
        ry = wy - rng
        if SNOW_LVL <= ry < world_height:
            voxel_id = SNOW

        elif STONE_LVL <= ry < SNOW_LVL:
            voxel_id = STONE

        elif DIRT_LVL <= ry < STONE_LVL:
            voxel_id = DIRT

        elif GRASS_LVL <= ry < DIRT_LVL:
            voxel_id = GRASS

        else:
            voxel_id = SAND

    voxels[get_index(x, y, z)] = voxel_id

    if wy < DIRT_LVL:
        place_tree(voxels, x, y, z, voxel_id)


@njit
def place_tree(voxels, x, y, z, voxel_id):
    rnd = random()
    if voxel_id != GRASS or rnd > TREE_PROBABILITY:
        return None
    if y + TREE_HEIGHT >= CHUNK_SIZE:
        return None
    if x - TREE_H_WIDTH < 0 or x + TREE_H_WIDTH >= CHUNK_SIZE:
        return None
    if z - TREE_H_WIDTH < 0 or z + TREE_H_WIDTH >= CHUNK_SIZE:
        return None

    voxels[get_index(x, y, z)] = DIRT
    leaf_id = ALT_LEAVES if random() < CHERRY_LEAF_VARIANT_CHANCE else LEAVES

    m = 0
    for n, iy in enumerate(range(TREE_H_HEIGHT, TREE_HEIGHT - 1)):
        k = iy % 2
        rng = int(random() * 2)
        for ix in range(-TREE_H_WIDTH + m, TREE_H_WIDTH - m * rng):
            for iz in range(-TREE_H_WIDTH + m * rng, TREE_H_WIDTH - m):
                if (ix + iz) % 4:
                    voxels[get_index(x + ix + k, y + iy, z + iz + k)] = leaf_id
        m += 1 if n > 0 else 3 if n > 1 else 0

    for iy in range(1, TREE_HEIGHT - 2):
        voxels[get_index(x, y + iy, z)] = WOOD

    voxels[get_index(x, y + TREE_HEIGHT - 2, z)] = leaf_id