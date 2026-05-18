from settings import *

class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.quad = self.get_program("quad")

        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        pass

    def update(self):
        pass

    def get_program(self, shader_name):
        with open(f"shaders/{shader_name}.vert") as f:
            vertex_shader = f.read()
        with open(f"shaders/{shader_name}.frag") as f:
            fragment_shader = f.read()
        
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program