import numpy as np
from meshes.base_mesh import BaseMesh
from settings import *

class HudInventoryMesh(BaseMesh):
    def __init__(self, app, slots=3):
        super().__init__()
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.hud
        self.color_program = app.shader_program.hud_color
        self.slots = slots
        self.slot_size = 0.14
        self.spacing = 0.036
        self.bottom = -0.85
        self.frame_pad = 0.012
        self.bar_pad_x = 0.05
        self.bar_pad_y = 0.04

        self.vaos = []
        self.frame_vaos = []
        self.selected_border_vaos = []
        self.selected_fill_vaos = []
        self.bar_vao = None
        self._build_vaos()

    def _make_colored_quad_vao(self, cx, cy, half_w, half_h):
        verts = [
            (cx + half_w, cy + half_h),
            (cx - half_w, cy + half_h),
            (cx - half_w, cy - half_h),
            (cx + half_w, cy + half_h),
            (cx - half_w, cy - half_h),
            (cx + half_w, cy - half_h),
        ]
        vertex_data = np.array(verts, dtype='f4')
        vbo = self.ctx.buffer(vertex_data.tobytes())
        return self.ctx.vertex_array(self.color_program, [(vbo, '2f', 'in_position')])

    def _make_textured_quad_vao(self, cx, cy, half_w, half_h):
        verts = [
            (cx + half_w, cy + half_h, 1.0, 1.0),
            (cx - half_w, cy + half_h, 0.0, 1.0),
            (cx - half_w, cy - half_h, 0.0, 0.0),
            (cx + half_w, cy + half_h, 1.0, 1.0),
            (cx - half_w, cy - half_h, 0.0, 0.0),
            (cx + half_w, cy - half_h, 1.0, 0.0),
        ]
        vertex_data = np.array(verts, dtype='f4')
        vbo = self.ctx.buffer(vertex_data.tobytes())
        return self.ctx.vertex_array(self.program, [(vbo, '2f 2f', 'in_position', 'in_tex_coord_0')])

    def _build_vaos(self):
        total_width = self.slots * self.slot_size + (self.slots - 1) * self.spacing
        left = -total_width * 0.5 + self.slot_size * 0.5

        self.bar_vao = self._make_colored_quad_vao(
            cx=0.0,
            cy=self.bottom,
            half_w=total_width * 0.5 + self.bar_pad_x,
            half_h=self.slot_size * 0.5 + self.bar_pad_y,
        )

        for i in range(self.slots):
            cx = left + i * (self.slot_size + self.spacing)
            half = self.slot_size * 0.5
            self.vaos.append(self._make_textured_quad_vao(cx, self.bottom, half, half))
            self.frame_vaos.append(self._make_colored_quad_vao(cx, self.bottom, half + self.frame_pad, half + self.frame_pad))

            selected_border = self._make_colored_quad_vao(
                cx,
                self.bottom,
                half + self.frame_pad + 0.005,
                half + self.frame_pad + 0.005,
            )
            self.selected_border_vaos.append(selected_border)
            self.selected_fill_vaos.append(self._make_colored_quad_vao(cx, self.bottom, half, half))

    def render(self, inventory_ids, selected_index):
        self.app.ctx.enable(self.app.ctx.BLEND)

        self.color_program['u_color'].value = (0.04, 0.04, 0.04, 0.58)
        self.bar_vao.render()

        self.color_program['u_color'].value = (0.14, 0.14, 0.14, 0.95)
        for frame_vao in self.frame_vaos:
            frame_vao.render()

        if 0 <= selected_index < len(self.selected_border_vaos):
            self.color_program['u_color'].value = (0.97, 0.88, 0.32, 1.0)
            self.selected_border_vaos[selected_index].render()

        for i, vao in enumerate(self.vaos):
            voxel_id = int(inventory_ids[i])
            self.program['voxel_id'].value = voxel_id
            vao.render()

        if 0 <= selected_index < len(self.selected_fill_vaos):
            self.color_program['u_color'].value = (1.0, 0.95, 0.45, 0.22)
            self.selected_fill_vaos[selected_index].render()