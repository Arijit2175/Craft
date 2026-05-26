import pygame as pg
import moderngl as mgl
import os
from settings import LEAVES, CHERRY_ALT_LEAVES_TEXTURE
from resource_utils import resource_path

class Textures:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.texture_0 = self.load('frame.png')
        self.texture_1 = self.load('water.png')
        self.texture_array_0 = self.load('tex_array_0.png', is_tex_array=True)

        self.texture_0.use(location=0)
        self.texture_array_0.use(location=1)
        self.texture_1.use(location=2)

    def load(self, file_name, is_tex_array=False):
        texture = pg.image.load(resource_path(f'assets/{file_name}')).convert_alpha()
        texture = pg.transform.flip(texture, flip_x=True, flip_y=False)

        if is_tex_array:
            texture = self.load_texture_array(texture)
        else:
            texture = self.ctx.texture(
                size=texture.get_size(),
                components=4,
                data=pg.image.tostring(texture, 'RGBA', False)
            )
        texture.anisotropy = 32.0
        texture.build_mipmaps()
        texture.filter = (mgl.NEAREST, mgl.NEAREST)
        return texture

    def load_texture_array(self, atlas_surface):
        layer_width = atlas_surface.get_width()
        layer_height = layer_width // 3
        num_layers = atlas_surface.get_height() // layer_height

        layer_data = []
        for layer_index in range(num_layers):
            rect = pg.Rect(0, layer_index * layer_height, layer_width, layer_height)
            layer_surface = pg.Surface((layer_width, layer_height), flags=pg.SRCALPHA)
            layer_surface.blit(atlas_surface, (0, 0), rect)
            layer_data.append(pg.image.tostring(layer_surface, 'RGBA', False))

        layer_data.extend(self.build_extra_texture_layers(atlas_surface, layer_width, layer_height))

        texture = self.app.ctx.texture_array(
            size=(layer_width, layer_height, len(layer_data)),
            components=4,
            data=b''.join(layer_data)
        )
        return texture

    def build_extra_texture_layers(self, atlas_surface, layer_width, layer_height):
        extra_layers = []
        tile_size = layer_height

        for file_name in ('rock.jpg', 'coal.jpeg', 'iron.jpeg', 'bedrock.png'):
            source = pg.image.load(resource_path(f'assets/{file_name}')).convert_alpha()
            source = pg.transform.flip(source, flip_x=True, flip_y=False)
            source = pg.transform.smoothscale(source, (tile_size, tile_size))

            layer_surface = pg.Surface((layer_width, layer_height), flags=pg.SRCALPHA)
            for column in range(3):
                layer_surface.blit(source, (column * tile_size, 0))

            extra_layers.append(pg.image.tostring(layer_surface, 'RGBA', False))

        # Add an alternate leaves layer for cherry-tree variety.
        # If the user texture is not present yet, reuse the existing leaves layer.
        alt_path = resource_path(f'assets/{CHERRY_ALT_LEAVES_TEXTURE}')
        if os.path.exists(alt_path):
            source = pg.image.load(alt_path).convert_alpha()
            source = pg.transform.flip(source, flip_x=True, flip_y=False)
            source = pg.transform.smoothscale(source, (tile_size, tile_size))

            layer_surface = pg.Surface((layer_width, layer_height), flags=pg.SRCALPHA)
            for column in range(3):
                layer_surface.blit(source, (column * tile_size, 0))
            extra_layers.append(pg.image.tostring(layer_surface, 'RGBA', False))
        else:
            leaf_rect = pg.Rect(0, LEAVES * layer_height, layer_width, layer_height)
            layer_surface = pg.Surface((layer_width, layer_height), flags=pg.SRCALPHA)
            layer_surface.blit(atlas_surface, (0, 0), leaf_rect)
            extra_layers.append(pg.image.tostring(layer_surface, 'RGBA', False))

        return extra_layers