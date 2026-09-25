#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform sampler2D u_sky[4];
uniform sampler2D u_skyEdgeTone;
uniform sampler2D u_hairMask;
uniform sampler2D u_blinkLeft;
uniform sampler2D u_blinkRight;
uniform int u_view;
uniform int u_lightingEnabled;
uniform int u_skyEnabled;
uniform int u_blinkClosed;
uniform int u_skyPhaseA;
uniform int u_skyPhaseB;
uniform float u_skyMix;
uniform float u_skyNightWeight;
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
uniform float u_upperSceneAttenuation;
uniform float u_breathPhase;
uniform float u_breathStrength;
uniform int u_breathOverlay;
uniform float u_hairTime;
uniform float u_hairStrength;
uniform float u_headMassStrength;
uniform float u_headHairStrength;
uniform int u_hairOverlay;
out vec4 outColor;
float softEllipse(vec2 p, vec2 center, vec2 radius) {
  return 1.0 - smoothstep(0.30, 1.0, length((p - center) / radius));
}
vec3 breathRegions(vec2 sourcePixel) {
  float core = softEllipse(sourcePixel, vec2(1152.0, 461.0), vec2(103.0, 137.0));
  float shoulder = softEllipse(sourcePixel, vec2(1151.0, 385.0), vec2(145.0, 93.0));
  float protected = max(
    softEllipse(sourcePixel, vec2(1154.0, 229.0), vec2(177.0, 135.0)),
    max(softEllipse(sourcePixel, vec2(987.0, 501.0), vec2(87.0, 194.0)),
        softEllipse(sourcePixel, vec2(1318.0, 520.0), vec2(79.0, 207.0)))
  );
  protected = max(protected, softEllipse(sourcePixel, vec2(1050.0, 433.0), vec2(44.0, 160.0)));
  protected = max(protected, softEllipse(sourcePixel, vec2(1282.0, 444.0), vec2(50.0, 169.0)));
  return vec3(core, shoulder, protected);
}
vec3 showBreathRegions(vec3 color, vec3 regions) {
  if (u_breathOverlay == 0) return color;
  vec3 tint = mix(vec3(0.14, 0.69, 0.90), vec3(0.24, 1.0, 0.58), regions.x);
  vec3 shaded = mix(color, tint, max(regions.x, regions.y * 0.55) * 0.56);
  return mix(shaded, vec3(1.0, 0.22, 0.37), regions.z * 0.36);
}
vec3 showMotionRegions(vec3 color, vec3 breath, vec4 hair) {
  color = showBreathRegions(color, breath);
  if (u_hairOverlay == 0) return color;
  color = mix(color, vec3(0.15, 0.70, 1.0), hair.b * 0.35);
  color = mix(color, vec3(1.0, 0.20, 0.72), hair.a * 0.55);
  color = mix(color, vec3(1.0, 0.12, 0.69), hair.x * 0.60);
  color = mix(color, vec3(1.0, 0.79, 0.06), hair.y * 0.60);
  return color;
}
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
vec3 toneMapAces(vec3 color) {
  const float a = 2.51;
  const float b = 0.03;
  const float c = 2.43;
  const float d = 0.59;
  const float e = 0.14;
  return clamp((color * (a * color + b)) / (color * (c * color + d) + e), 0.0, 1.0);
}
vec4 sampleSky(int phase) {
  if (phase == 0) return texture(u_sky[0], v_uv);
  if (phase == 1) return texture(u_sky[1], v_uv);
  if (phase == 2) return texture(u_sky[2], v_uv);
  return texture(u_sky[3], v_uv);
}
float bandResponse(float facing) {
  float edge = max(u_bandSoftness, 0.001);
  return smoothstep(u_bandThreshold - edge, u_bandThreshold + edge, facing);
}
void main() {
  vec3 regions = breathRegions(v_uv * vec2(1672.0, 941.0));
  float weight = max(regions.x, regions.y * 0.42) * (1.0 - regions.z);
  vec2 sampleUv = v_uv;
  if (u_breathStrength > 0.0) {
    float inhale = 0.5 - 0.5 * cos(u_breathPhase);
    sampleUv.y += inhale * weight * u_breathStrength / 941.0;
    sampleUv.x -= inhale * weight * (v_uv.x * 1672.0 - 1152.0) / 103.0 * u_breathStrength * 0.30 / 1672.0;
  }
  vec4 hairRegion = texture(u_hairMask, v_uv);
  if (u_headMassStrength > 0.0 || u_headHairStrength > 0.0) {
    vec2 p = v_uv * vec2(1672.0, 941.0);
    float primary = 6.2831853 * u_hairTime / 6.4;
    float secondary = 6.2831853 * u_hairTime / 9.1;
    float breathLink = u_breathStrength > 0.0 ? sin(u_breathPhase - 0.35) : 0.0;
    vec2 headPx = vec2(
      0.66 * sin(primary + 0.45) + 0.22 * sin(secondary + 1.05) + 0.12 * breathLink,
      0.34 * sin(secondary + 0.85) + 0.12 * breathLink
    ) * u_headMassStrength;
    vec2 headCandidate = sampleUv + headPx / vec2(1672.0, 941.0);
    float headProtect = min(hairRegion.b, texture(u_hairMask, headCandidate).b);
    sampleUv += headPx * headProtect / vec2(1672.0, 941.0);

    float side = smoothstep(1150.0, 1230.0, p.x);
    float leftDrift = 0.70 * sin(primary + p.y * 0.018 + 1.1)
      + 0.25 * sin(secondary + p.x * 0.013 + 2.3);
    float rightDrift = 0.72 * sin(primary + p.y * 0.016 + 0.3)
      + 0.26 * sin(secondary + p.x * 0.011 + 1.5);
    vec2 strandPx = vec2(mix(leftDrift, rightDrift, side),
      0.15 * cos(secondary + p.y * 0.014 + side)) * u_headHairStrength;
    vec2 strandCandidate = sampleUv + strandPx / vec2(1672.0, 941.0);
    float strandProtect = min(hairRegion.a, texture(u_hairMask, strandCandidate).a);
    sampleUv += strandPx * strandProtect / vec2(1672.0, 941.0);
  }
  if (u_hairStrength > 0.0) {
    vec2 p = v_uv * vec2(1672.0, 941.0);
    float primary = 6.2831853 * u_hairTime / 6.4;
    float secondary = 6.2831853 * u_hairTime / 9.1;
    float rightSway = 0.72 * sin(primary + p.y * 0.013)
      + 0.28 * sin(secondary + p.y * 0.022 + 1.3);
    float leftSway = 0.67 * sin(primary + p.y * 0.011 + 0.95)
      + 0.25 * sin(secondary + p.x * 0.010 + 2.1);
    vec2 flowPx = vec2(rightSway * hairRegion.y + leftSway * hairRegion.x * 0.83,
      0.12 * cos(secondary + p.x * 0.018) * hairRegion.y
      + 0.09 * cos(primary + p.y * 0.009 + 0.8) * hairRegion.x);
    vec2 candidate = sampleUv + flowPx * u_hairStrength / vec2(1672.0, 941.0);
    vec2 candidateRegion = texture(u_hairMask, candidate).rg;
    float protection = min(1.0, (candidateRegion.x + candidateRegion.y) / max(hairRegion.x + hairRegion.y, 0.001));
    sampleUv += flowPx * protection * u_hairStrength / vec2(1672.0, 941.0);
  }
  vec4 base = texture(u_base, sampleUv);
  // Closed-eye sprites replace local Albedo before the existing Normal-driven
  // lighting transform. Base inspection retains its registered DOM overlay.
  if ((u_view == 2 || (u_view == 0 && u_headMassStrength > 0.0)) && u_blinkClosed != 0) {
    vec2 sourcePixel = sampleUv * vec2(1672.0, 941.0);
    if (sourcePixel.x >= 1080.0 && sourcePixel.x < 1172.0 && sourcePixel.y >= 177.0 && sourcePixel.y < 250.0) {
      vec4 closedEye = texture(u_blinkLeft, (sourcePixel - vec2(1080.0, 177.0)) / vec2(92.0, 73.0));
      base.rgb = mix(base.rgb, closedEye.rgb, closedEye.a);
    }
    if (sourcePixel.x >= 1152.0 && sourcePixel.x < 1244.0 && sourcePixel.y >= 195.0 && sourcePixel.y < 273.0) {
      vec4 closedEye = texture(u_blinkRight, (sourcePixel - vec2(1152.0, 195.0)) / vec2(92.0, 78.0));
      base.rgb = mix(base.rgb, closedEye.rgb, closedEye.a);
    }
  }
  if (u_view == 0) { outColor = vec4(showMotionRegions(base.rgb, regions, hairRegion), base.a); return; }
  vec3 normalColor = texture(u_normal, sampleUv).rgb;
  if (u_view == 1) { outColor = vec4(showMotionRegions(normalColor, regions, hairRegion), 1.0); return; }
  if (u_lightingEnabled == 0) { outColor = vec4(showMotionRegions(base.rgb, regions, hairRegion), base.a); return; }
  vec3 baseLinear = srgbToLinear(base.rgb);
  vec3 decodedNormal = normalColor * 2.0 - 1.0;
  vec3 normal = normalize(vec3(decodedNormal.x, -decodedNormal.y, decodedNormal.z));
  vec3 lightDirection = normalize(u_lightDirection);
  float ndotl = dot(normal, lightDirection);
  float wrapped = clamp((ndotl + u_diffuseWrap) / (1.0 + u_diffuseWrap), 0.0, 1.0);
  float diffuse = smoothstep(u_diffuseThreshold - u_diffuseSoftness, u_diffuseThreshold + u_diffuseSoftness, wrapped);
  vec2 texel = 1.0 / vec2(textureSize(u_normal, 0));
  vec3 broadEncoded = normalColor * 4.0
    + texture(u_normal, sampleUv + vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, sampleUv - vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, sampleUv + vec2(0.0, texel.y * 5.0)).rgb
    + texture(u_normal, sampleUv - vec2(0.0, texel.y * 5.0)).rgb;
  vec3 broadDecoded = broadEncoded / 8.0 * 2.0 - 1.0;
  vec3 broadNormal = normalize(vec3(broadDecoded.x, -broadDecoded.y, broadDecoded.z));
  float broadFacing = dot(broadNormal, lightDirection);
  float paintedBand = bandResponse(broadFacing);
  float bandDiffuse = mix(0.20, 0.66, paintedBand);
  float shapedDiffuse = mix(diffuse, bandDiffuse, u_bandStrength);
  vec3 illumination = u_ambientColor * u_ambientIntensity
    + u_lightColor * (shapedDiffuse * u_lightIntensity);
  float upperSceneMask = 1.0 - smoothstep(0.28, 0.68, v_uv.y);
  float upperSceneFactor = 1.0 - upperSceneMask * clamp(u_upperSceneAttenuation, 0.0, 1.0);
  illumination *= upperSceneFactor;
  vec3 relitLinear = max(baseLinear * illumination, vec3(0.0));
  vec3 blendedLinear = mix(baseLinear, relitLinear, clamp(u_relightStrength, 0.0, 1.0));
  vec3 exposedLinear = blendedLinear * exp2(u_exposure);
  vec3 displayLinear = toneMapAces(exposedLinear);
  if (u_skyEnabled != 0) {
    vec4 skyA = sampleSky(u_skyPhaseA);
    vec4 skyB = sampleSky(u_skyPhaseB);
    vec4 sky = mix(skyA, skyB, clamp(u_skyMix, 0.0, 1.0));
    vec3 skyLinear = srgbToLinear(sky.rgb);
    displayLinear = mix(displayLinear, skyLinear, clamp(sky.a, 0.0, 1.0));
  }
  vec3 displayColor = linearToSrgb(displayLinear);
  if (u_skyEnabled != 0) {
    // Registered edge material shades only the bright foreground bordering
    // Night sky. Its alpha is zero across open sky and the main artwork.
    float edgeTone = texture(u_skyEdgeTone, v_uv).a * u_skyNightWeight;
    displayColor *= 1.0 - edgeTone;
  }
  outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);
}
