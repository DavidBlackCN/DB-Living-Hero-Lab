#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform int u_view;
uniform int u_lightingEnabled;
uniform float u_exposure;
uniform float u_relightStrength;
uniform vec3 u_lightDirection;
uniform float u_lightIntensity;
uniform vec3 u_lightColor;
uniform float u_ambientIntensity;
uniform vec3 u_ambientColor;
uniform float u_diffuseWrap;
uniform float u_diffuseThreshold;
uniform float u_diffuseSoftness;
uniform float u_bandStrength;
uniform float u_bandThreshold;
uniform float u_bandSoftness;
out vec4 outColor;
vec3 srgbToLinear(vec3 color) {
  vec3 low = color / 12.92;
  vec3 high = pow((color + 0.055) / 1.055, vec3(2.4));
  return mix(low, high, step(vec3(0.04045), color));
}
vec3 linearToSrgb(vec3 color) {
  vec3 low = color * 12.92;
  vec3 high = 1.055 * pow(max(color, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055;
  return mix(low, high, step(vec3(0.0031308), color));
}
float bandResponse(float facing) {
  float edge = max(u_bandSoftness, 0.001);
  return smoothstep(u_bandThreshold - edge, u_bandThreshold + edge, facing);
}
void main() {
  vec4 base = texture(u_base, v_uv);
  if (u_view == 0) { outColor = base; return; }
  vec3 normalColor = texture(u_normal, v_uv).rgb;
  if (u_view == 1) { outColor = vec4(normalColor, 1.0); return; }
  if (u_lightingEnabled == 0) { outColor = base; return; }
  vec3 baseLinear = srgbToLinear(base.rgb);
  vec3 decodedNormal = normalColor * 2.0 - 1.0;
  vec3 normal = normalize(vec3(decodedNormal.x, -decodedNormal.y, decodedNormal.z));
  vec3 lightDirection = normalize(u_lightDirection);
  float ndotl = dot(normal, lightDirection);
  float wrapped = clamp((ndotl + u_diffuseWrap) / (1.0 + u_diffuseWrap), 0.0, 1.0);
  float diffuse = smoothstep(u_diffuseThreshold - u_diffuseSoftness, u_diffuseThreshold + u_diffuseSoftness, wrapped);
  vec2 texel = 1.0 / vec2(textureSize(u_normal, 0));
  vec3 broadEncoded = normalColor * 4.0
    + texture(u_normal, v_uv + vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, v_uv - vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, v_uv + vec2(0.0, texel.y * 5.0)).rgb
    + texture(u_normal, v_uv - vec2(0.0, texel.y * 5.0)).rgb;
  vec3 broadDecoded = broadEncoded / 8.0 * 2.0 - 1.0;
  vec3 broadNormal = normalize(vec3(broadDecoded.x, -broadDecoded.y, broadDecoded.z));
  float broadFacing = dot(broadNormal, lightDirection);
  float paintedBand = bandResponse(broadFacing);
  float bandDiffuse = mix(0.20, 0.66, paintedBand);
  float shapedDiffuse = mix(diffuse, bandDiffuse, u_bandStrength);
  vec3 illumination = u_ambientColor * u_ambientIntensity
    + u_lightColor * (shapedDiffuse * u_lightIntensity);
  vec3 relitLinear = max(baseLinear * illumination * u_exposure, vec3(0.0));
  vec3 blendedLinear = mix(baseLinear, relitLinear, clamp(u_relightStrength, 0.0, 1.0));
  outColor = vec4(clamp(linearToSrgb(blendedLinear), 0.0, 1.0), base.a);
}
