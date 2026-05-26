from settings import WIN_RES
import moderngl as mgl
import pygame as pg
import numpy as np
import os
from resource_utils import resource_path

class LoadingScreen:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.width = int(WIN_RES.x)
        self.height = int(WIN_RES.y)

        self.bg_color = (0.118, 0.094, 0.075)
        self.bar_bg_color = (0.22, 0.22, 0.22)
        self.bar_fill_color = (0.34, 0.83, 0.34)
        self.bar_border_color = (0.84, 0.84, 0.84)

        self._init_title_resources()

    def _init_title_resources(self):
        vertex_shader = '''
#version 330 core
layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_uv;
out vec2 uv;
void main() {
    uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
'''
        fragment_shader = '''
#version 330 core
layout (location = 0) out vec4 fragColor;
in vec2 uv;
uniform sampler2D u_text;
void main() {
    fragColor = texture(u_text, uv);
}
'''

        self.title_program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        self.title_program['u_text'] = 0

        pixelify_candidates = (
            resource_path('assets/font/static/PixelifySans-Bold.ttf'),
            resource_path('assets/font/PixelifySans-VariableFont_wght.ttf'),
            resource_path('assets/font/static/PixelifySans-SemiBold.ttf'),
            resource_path('assets/font/static/PixelifySans-Regular.ttf'),
            resource_path('assets/PixelifySans-Regular.ttf'),
            resource_path('assets/PixelifySans-VariableFont_wght.ttf'),
        )
        pixelify_path = next((path for path in pixelify_candidates if os.path.exists(path)), None)
        if pixelify_path:
            font = pg.font.Font(pixelify_path, 86)
        else:
            font = pg.font.SysFont('Arial', 86, bold=True)
        title_surface = font.render('Welcome', True, (245, 237, 208))

        self.title_tex_w, self.title_tex_h = title_surface.get_size()
        self.title_texture = self.ctx.texture(
            size=(self.title_tex_w, self.title_tex_h),
            components=4,
            data=pg.image.tostring(title_surface, 'RGBA', True),
        )
        self.title_texture.filter = (mgl.LINEAR, mgl.LINEAR)

        bar_y = int(self.height * 0.60)
        title_center_x = self.width // 2
        title_center_y = bar_y - int(self.height * 0.08)

        x0 = title_center_x - self.title_tex_w // 2
        y0 = title_center_y - self.title_tex_h // 2
        x1 = x0 + self.title_tex_w
        y1 = y0 + self.title_tex_h

        l = x0 / self.width * 2.0 - 1.0
        r = x1 / self.width * 2.0 - 1.0
        t = 1.0 - y0 / self.height * 2.0
        b = 1.0 - y1 / self.height * 2.0

        title_vertices = np.array([
            (r, t, 1.0, 1.0),
            (l, t, 0.0, 1.0),
            (l, b, 0.0, 0.0),
            (r, t, 1.0, 1.0),
            (l, b, 0.0, 0.0),
            (r, b, 1.0, 0.0),
        ], dtype='f4')

        self.title_vbo = self.ctx.buffer(title_vertices.tobytes())
        self.title_vao = self.ctx.vertex_array(self.title_program, [(self.title_vbo, '2f 2f', 'in_position', 'in_uv')])

    def _draw_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        gl_y = self.height - (y + h)
        self.ctx.scissor = (int(x), int(gl_y), int(w), int(h))
        self.ctx.clear(*color)

    def draw(self, progress, title='Generating world', detail='Building terrain'):
        progress = max(0.0, min(1.0, float(progress)))
        pg.event.pump()

        self.ctx.disable(mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.enable(mgl.BLEND)
        self.ctx.scissor = None
        self.ctx.clear(*self.bg_color)

        bar_w = int(self.width * 0.42)
        bar_h = max(10, int(self.height * 0.02))
        bar_x = (self.width - bar_w) // 2
        bar_y = int(self.height * 0.60)

        self._draw_rect(bar_x, bar_y, bar_w, bar_h, self.bar_bg_color)
        fill_w = int((bar_w - 4) * progress)
        self._draw_rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4, self.bar_fill_color)

        self._draw_rect(bar_x, bar_y, bar_w, 1, self.bar_border_color)
        self._draw_rect(bar_x, bar_y + bar_h - 1, bar_w, 1, self.bar_border_color)
        self._draw_rect(bar_x, bar_y, 1, bar_h, self.bar_border_color)
        self._draw_rect(bar_x + bar_w - 1, bar_y, 1, bar_h, self.bar_border_color)

        self.ctx.scissor = None
        self.title_texture.use(location=0)
        self.title_vao.render()

        self.ctx.scissor = None
        pg.display.set_caption(f'{title} - {detail} ({int(progress * 100)}%)')
        pg.display.flip()