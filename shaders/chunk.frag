#version 330 core

layout (location = 0) out vec4 fragColor;

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1 / gamma;

uniform sampler2DArray u_texture_array_0;
uniform vec3 bg_color;
uniform vec3 underwater_color;
uniform int underwater;
uniform float underwater_fog_density;
uniform float light_level;
uniform float water_line;

in vec2 uv;
in float shading;
in vec3 frag_world_pos;

flat in int face_id;
flat in int voxel_id;


void main() {
    vec2 face_uv = uv;
    face_uv.x = uv.x / 3.0 - min(face_id, 2) / 3.0;

    vec3 tex_col = texture(u_texture_array_0, vec3(face_uv, voxel_id)).rgb;
    tex_col = pow(tex_col, gamma);

    tex_col *= shading * light_level;

    float cave_darkness = 1.0 - smoothstep(18.0, 44.0, frag_world_pos.y);
    tex_col *= mix(1.0, 0.42, cave_darkness);

    //fog
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    vec3 fog_color = underwater > 0 ? underwater_color : bg_color;
    float fog_density = underwater > 0 ? underwater_fog_density : 0.00001;
    if (underwater > 0) {
        tex_col = mix(tex_col, fog_color, 0.32);
    }
    tex_col = mix(tex_col, fog_color, (1.0 - exp2(-fog_density * fog_dist * fog_dist)));

    tex_col = pow(tex_col, inv_gamma);
    fragColor = vec4(tex_col, 1.0);
}