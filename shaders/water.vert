#version 330 core

layout (location = 0) in vec2 in_tex_coord;
layout (location = 1) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform float u_time;

out vec2 uv;


void main() {
    vec3 pos = in_position;
    pos.y += 0.02 * sin(u_time * 0.6 + pos.x * 0.03 + pos.z * 0.03);
    uv = in_tex_coord;
    gl_Position = m_proj * m_view * vec4(pos, 1.0);
}