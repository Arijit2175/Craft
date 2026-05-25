from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from scene import Scene
from player import Player
from textures import Textures
from sounds import play_background_music
from loading_screen import LoadingScreen

class VoxelEngine:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, NUM_SAMPLES)

        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()
        self.loading_screen = LoadingScreen(self)
        self.loading_screen.draw(0.03, 'Generating world', 'Initializing engine')

        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
        except pg.error:
            pass

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.is_running = True
        self.on_init()

    def on_init(self):
        self.loading_screen.draw(0.10, 'Generating world', 'Loading textures')
        self.textures = Textures(self)

        self.loading_screen.draw(0.18, 'Generating world', 'Preparing player')
        self.player = Player(self)

        self.loading_screen.draw(0.24, 'Generating world', 'Loading audio')
        from sounds import MovementAudio
        self.movement_audio = MovementAudio(self)
        play_background_music()

        self.loading_screen.draw(0.30, 'Generating world', 'Compiling shaders')
        self.shader_program = ShaderProgram(self)

        self.loading_screen.draw(0.35, 'Generating world', 'Building terrain')
        self.scene = Scene(self)
        self.loading_screen.draw(1.0, 'Generating world', 'Done')
        self.loading_screen = None

    def update(self):
        self.delta_time = self.clock.tick() * 0.001
        self.time = pg.time.get_ticks() * 0.001

        self.player.update()
        self.shader_program.update()
        self.scene.update()
        pg.display.set_caption(f'{self.clock.get_fps() :.0f}')

    def render(self):
        self.ctx.clear(color=tuple(self.scene.sky_color))
        self.scene.render()
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            self.player.handle_event(event=event)

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    app = VoxelEngine()
    app.run()