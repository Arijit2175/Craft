#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

in vec2 uv;

uniform sampler2D u_texture_0;
uniform float daylight;


void main() {
    vec3 tex_col = texture(u_texture_0, uv).rgb;
    tex_col = pow(tex_col, gamma);
    vec3 day_tint = vec3(0.15, 0.45, 1.0);
    vec3 night_tint = vec3(0.05, 0.12, 0.22);
    tex_col = mix(tex_col, mix(night_tint, day_tint, daylight), 0.2);
    tex_col = pow(tex_col, inv_gamma);
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    float alpha = mix(0.72, 0.45, 1.0 - exp(-0.000002 * fog_dist * fog_dist));
    fragColor = vec4(tex_col, alpha);
}