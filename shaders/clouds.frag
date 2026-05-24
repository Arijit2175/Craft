#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 cloud_color = vec3(1);

uniform vec3 bg_color;
uniform float daylight;

void main() {
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    vec3 lit_cloud_color = mix(cloud_color * 0.18, cloud_color, daylight);
    vec3 col = mix(lit_cloud_color, bg_color, 1.0 - exp(-0.000001 * fog_dist * fog_dist));

    float alpha = mix(0.18, 0.8, daylight);
    fragColor = vec4(col, alpha);
}