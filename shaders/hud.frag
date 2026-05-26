#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2DArray u_texture_array_0;
uniform int voxel_id;

void main() {
    vec3 col = texture(u_texture_array_0, vec3(uv, voxel_id)).rgb;
    fragColor = vec4(col, 1.0);
}