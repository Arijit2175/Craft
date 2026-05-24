from settings import *

class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.player = app.player
        self.chunk = self.get_program(shader_name='chunk')
        self.quad = self.get_program(shader_name='quad')
        self.sky = self.get_program(shader_name='sky')
        self.crosshair = self.get_program(shader_name='crosshair')
        self.voxel_marker = self.get_program(shader_name='voxel_marker')
        self.water = self.get_program('water')
        self.clouds = self.get_program('clouds')
        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        self.chunk['m_proj'].write(self.player.m_proj)
        self.chunk['m_model'].write(glm.mat4())
        self.chunk['u_texture_array_0'] = 1
        self.chunk['bg_color'].write(BG_COLOR)
        self.chunk['light_level'] = 1.0
        self.chunk['underwater_color'].write(UNDERWATER_FOG_COLOR)
        self.chunk['underwater'] = 0
        self.chunk['underwater_fog_density'] = UNDERWATER_FOG_DENSITY

        self.voxel_marker['m_proj'].write(self.player.m_proj)
        self.voxel_marker['m_model'].write(glm.mat4())
        self.voxel_marker['u_texture_0'] = 0

        self.water['m_proj'].write(self.player.m_proj)
        self.water['m_view'].write(self.player.m_view)
        self.water['u_texture_0'] = 2
        self.water['u_time'] = 0.0

        self.clouds['m_proj'].write(self.player.m_proj)
        self.clouds['center'] = CENTER_XZ
        self.clouds['bg_color'].write(BG_COLOR)
        self.clouds['daylight'] = 1.0
        self.clouds['cloud_scale'] = CLOUD_SCALE

        self.sky['time_of_day'] = 0.25
        self.sky['daylight'] = 1.0
        self.sky['u_time'] = 0.0
        self.sky['sky_color'].write(BG_COLOR)
        self.sky['night_color'].write(NIGHT_SKY_COLOR)
        self.sky['dawn_color'].write(DAWN_SKY_COLOR)

    def update(self):
        scene = self.app.scene
        self.chunk['bg_color'].write(scene.sky_color)
        self.chunk['light_level'] = scene.daylight
        self.chunk['m_view'].write(self.player.m_view)
        self.chunk['underwater'] = 1 if self.player.get_water_state() == 2 else 0
        self.voxel_marker['m_view'].write(self.player.m_view)
        self.water['m_view'].write(self.player.m_view)
        self.water['daylight'] = scene.daylight
        self.water['u_time'] = self.app.time
        self.clouds['bg_color'].write(scene.sky_color)
        self.clouds['daylight'] = scene.daylight
        self.clouds['m_view'].write(self.player.m_view)
        self.sky['time_of_day'] = scene.time_of_day
        self.sky['daylight'] = scene.daylight
        self.sky['u_time'] = self.app.time
        self.sky['sky_color'].write(scene.sky_color)

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program