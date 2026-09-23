#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform int u_view;
uniform vec2 u_lightDirection;
uniform float u_testStrength;
out vec4 outColor;
void main() {
  vec4 base = texture(u_base, v_uv);
  if (u_view == 0) { outColor = base; return; }
  vec3 normalColor = texture(u_normal, v_uv).rgb;
  if (u_view == 1) { outColor = vec4(normalColor, 1.0); return; }
  vec3 normal = normalize(normalColor * 2.0 - 1.0);
  vec3 light = normalize(vec3(u_lightDirection, 0.75));
  float response = dot(normal, light) - light.z;
  outColor = vec4(clamp(base.rgb * (1.0 + response * u_testStrength), 0.0, 1.0), base.a);
}
