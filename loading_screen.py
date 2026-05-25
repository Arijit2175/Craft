from settings import WIN_RES
import moderngl as mgl
import pygame as pg

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
        self.ctx.scissor = None
        self.ctx.clear(*self.bg_color)

        bar_w = int(self.width * 0.42)
        bar_h = max(10, int(self.height * 0.02))
        bar_x = (self.width - bar_w) // 2
        bar_y = int(self.height * 0.60)

        self._draw_rect(bar_x, bar_y, bar_w, bar_h, self.bar_bg_color)
        fill_w = int((bar_w - 4) * progress)
        self._draw_rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4, self.bar_fill_color)

        # Border around the progress bar
        self._draw_rect(bar_x, bar_y, bar_w, 1, self.bar_border_color)
        self._draw_rect(bar_x, bar_y + bar_h - 1, bar_w, 1, self.bar_border_color)
        self._draw_rect(bar_x, bar_y, 1, bar_h, self.bar_border_color)
        self._draw_rect(bar_x + bar_w - 1, bar_y, 1, bar_h, self.bar_border_color)

        self.ctx.scissor = None
        pg.display.set_caption(f'{title} - {detail} ({int(progress * 100)}%)')
        pg.display.flip()
