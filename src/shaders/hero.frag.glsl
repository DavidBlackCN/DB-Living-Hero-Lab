#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform int u_view;
uniform int u_lightingEnabled;
uniform vec3 u_lightDirection;
uniform float u_lightIntensity;
uniform vec3 u_lightColor;
uniform float u_ambientIntensity;
uniform vec3 u_ambientColor;
uniform float u_diffuseWrap;
uniform float u_diffuseThreshold;
uniform float u_diffuseSoftness;
out vec4 outColor;
void main() {
  vec4 base = texture(u_base, v_uv);
  if (u_view == 0) { outColor = base; return; }
  vec3 normalColor = texture(u_normal, v_uv).rgb;
  if (u_view == 1) { outColor = vec4(normalColor, 1.0); return; }
  if (u_lightingEnabled == 0) { outColor = base; return; }
  vec3 normal = normalize(normalColor * 2.0 - 1.0);
  vec3 lightDirection = normalize(u_lightDirection);
  float ndotl = dot(normal, lightDirection);
  float wrapped = clamp((ndotl + u_diffuseWrap) / (1.0 + u_diffuseWrap), 0.0, 1.0);
  float diffuse = smoothstep(u_diffuseThreshold - u_diffuseSoftness, u_diffuseThreshold + u_diffuseSoftness, wrapped);
  float neutralWrapped = clamp((lightDirection.z + u_diffuseWrap) / (1.0 + u_diffuseWrap), 0.0, 1.0);
  float neutralDiffuse = smoothstep(u_diffuseThreshold - u_diffuseSoftness, u_diffuseThreshold + u_diffuseSoftness, neutralWrapped);
  float directionalResponse = diffuse - neutralDiffuse;
  vec3 illumination = vec3(1.0) + u_ambientColor * u_ambientIntensity + u_lightColor * (directionalResponse * u_lightIntensity);
  outColor = vec4(clamp(base.rgb * illumination, 0.0, 1.0), base.a);
}
