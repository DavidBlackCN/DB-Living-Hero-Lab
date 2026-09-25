#version 300 es
precision highp float;
in vec2 v_uv;
uniform sampler2D u_source;
uniform sampler2D u_gate;
uniform sampler2D u_scene;
uniform sampler2D u_bloom0;
uniform sampler2D u_bloom1;
uniform sampler2D u_bloom2;
uniform sampler2D u_bloom3;
uniform sampler2D u_edgeTone;
uniform vec2 u_texel;
uniform vec4 u_artworkRect;
uniform int u_mode;
uniform int u_preview;
uniform float u_sceneExposure;
uniform float u_postExposure;
uniform float u_threshold;
uniform float u_knee;
uniform float u_bloomStrength;
uniform float u_nightWeight;
uniform float u_saturation;
uniform float u_contrast;
uniform vec3 u_tint;
out vec4 outColor;
vec4 encodeHDR(vec3 color) {
  color = clamp(color, vec3(0.0), vec3(16.0));
  float multiplier = clamp(ceil(max(max(color.r, color.g), color.b) * (255.0 / 16.0)) / 255.0, 1.0 / 255.0, 1.0);
  return vec4(color / (multiplier * 16.0), multiplier);
}
vec3 decodeHDR(vec4 pixel) { return pixel.rgb * pixel.a * 16.0; }
vec3 sampleSource(vec2 offset) { return decodeHDR(texture(u_source, v_uv + offset * u_texel)); }
vec3 aces(vec3 color) {
  return clamp((color * (2.51 * color + 0.03)) / (color * (2.43 * color + 0.59) + 0.14), 0.0, 1.0);
}
vec3 linearToSrgb(vec3 color) {
  return mix(color * 12.92, 1.055 * pow(max(color, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055,
    step(vec3(0.0031308), color));
}
vec3 glow() {
  return decodeHDR(texture(u_bloom0, v_uv)) * 0.42
    + decodeHDR(texture(u_bloom1, v_uv)) * 0.30
    + decodeHDR(texture(u_bloom2, v_uv)) * 0.19
    + decodeHDR(texture(u_bloom3, v_uv)) * 0.09;
}
void main() {
  if (u_mode == 0 || u_mode == 1) {
    vec3 color = (sampleSource(vec2(-0.5, -0.5)) + sampleSource(vec2(0.5, -0.5))
      + sampleSource(vec2(-0.5, 0.5)) + sampleSource(vec2(0.5, 0.5))) * 0.25;
    if (u_mode == 0) {
      float eligibility = texture(u_gate, v_uv).r;
      float brightness = max(max(color.r, color.g), color.b) * u_sceneExposure * u_postExposure;
      float knee = max(u_threshold * u_knee, 0.001);
      float soft = clamp(brightness - u_threshold + knee, 0.0, 2.0 * knee);
      soft = soft * soft / (4.0 * knee);
      color *= max(brightness - u_threshold, soft) / max(brightness, 0.00001) * eligibility;
    }
    outColor = encodeHDR(color);
    return;
  }
  if (u_mode == 2) {
    vec3 color = sampleSource(vec2(0.0)) * 0.227027;
    color += (sampleSource(vec2(1.384615, 0.0)) + sampleSource(vec2(-1.384615, 0.0))
      + sampleSource(vec2(0.0, 1.384615)) + sampleSource(vec2(0.0, -1.384615))) * 0.158108;
    color += (sampleSource(vec2(3.230769, 0.0)) + sampleSource(vec2(-3.230769, 0.0))
      + sampleSource(vec2(0.0, 3.230769)) + sampleSource(vec2(0.0, -3.230769))) * 0.035135;
    outColor = encodeHDR(color);
    return;
  }
  vec2 artwork = (v_uv - u_artworkRect.xy) / u_artworkRect.zw;
  if (any(lessThan(artwork, vec2(0.0))) || any(greaterThan(artwork, vec2(1.0)))) {
    outColor = vec4(0.08, 0.075, 0.075, 1.0);
    return;
  }
  vec3 scene = decodeHDR(texture(u_scene, v_uv)) * u_sceneExposure * u_postExposure;
  vec3 bloom = glow() * u_bloomStrength;
  if (u_preview == 1) {
    outColor = vec4(linearToSrgb(aces(decodeHDR(texture(u_source, v_uv)) * u_sceneExposure)), 1.0);
    return;
  }
  if (u_preview == 2) {
    outColor = vec4(linearToSrgb(aces(bloom * 8.0)), 1.0);
    return;
  }
  vec3 color = linearToSrgb(aces(scene + bloom));
  if (u_preview != 3) {
    float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
    color = mix(vec3(luma), color, u_saturation);
    color = (color - 0.5) * u_contrast + 0.5;
    color *= u_tint;
  }
  // Frozen registered foreground edge tone remains a display-space correction.
  float edge = texture(u_edgeTone, vec2(artwork.x, 1.0 - artwork.y)).a * u_nightWeight;
  outColor = vec4(clamp(color * (1.0 - edge), 0.0, 1.0), 1.0);
}
