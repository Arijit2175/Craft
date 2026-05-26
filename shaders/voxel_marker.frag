#version 330 core

layout (location = 0) out vec4 fragColor;

in vec3 marker_color;
in vec2 uv;

uniform sampler2D u_texture_0;

void main() {
    // Draw only face edges so the marker appears as an outline, not a solid block.
    float edge = min(min(uv.x, uv.y), min(1.0 - uv.x, 1.0 - uv.y));
    float line_alpha = 1.0 - smoothstep(0.04, 0.085, edge);

    if (line_alpha < 0.01) {
        discard;
    }

    vec3 line_color = mix(vec3(1.0), marker_color, 0.85);
    fragColor = vec4(line_color, line_alpha);
}