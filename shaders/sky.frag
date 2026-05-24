#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform float time_of_day;
uniform float daylight;
uniform float u_time;
uniform vec3 sky_color;
uniform vec3 night_color;
uniform vec3 dawn_color;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

float star_field(vec2 p) {
    vec2 grid = floor(p * 260.0);
    vec2 cell = fract(p * 260.0) - 0.5;
    float rnd = hash(grid);
    float star = smoothstep(0.025, 0.0, length(cell));
    star *= step(0.975, rnd);
    star *= 0.55 + 0.45 * sin(u_time * 6.0 + rnd * 50.0);
    return star;
}

void main() {
    float t = clamp(daylight, 0.0, 1.0);
    float horizon = smoothstep(0.0, 0.55, uv.y);

    vec3 zenith = mix(night_color, sky_color, t);
    vec3 horizon_color = mix(night_color * 0.45, sky_color, t);
    vec3 col = mix(horizon_color, zenith, horizon * horizon);
    float stars = star_field(uv) * (1.0 - t) * smoothstep(0.15, 0.85, uv.y);
    vec3 star_color = vec3(0.95, 0.96, 1.0);

    col += stars * star_color * 0.95;

    float dawn_band = smoothstep(0.0, 0.4, 1.0 - abs(time_of_day - 0.25) * 4.0)
                    + smoothstep(0.0, 0.4, 1.0 - abs(time_of_day - 0.75) * 4.0);
    col = mix(col, dawn_color, clamp(dawn_band * 0.15, 0.0, 0.25));

    fragColor = vec4(col, 1.0);
}