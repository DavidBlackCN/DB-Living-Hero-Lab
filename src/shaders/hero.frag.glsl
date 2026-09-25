#version 300 es
precision highp float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform sampler2D u_sky[4];
uniform sampler2D u_skyEdgeTone;
uniform sampler2D u_hairMask;
uniform sampler2D u_materialMask;
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
uniform float u_directionalStrength;
uniform float u_upperSceneAttenuation;
uniform float u_breathPhase;
uniform float u_breathStrength;
uniform int u_breathOverlay;
uniform float u_hairTime;
uniform float u_hairStrength;
uniform float u_headMassStrength;
uniform float u_headHairStrength;
uniform int u_hairOverlay;
uniform int u_detailEnabled;
uniform int u_sceneLinear;
layout(location = 0) out vec4 outColor;
layout(location = 1) out vec4 outBloomGate;
vec4 encodeHDR(vec3 color) {
  color = clamp(color, vec3(0.0), vec3(16.0));
  float multiplier = clamp(ceil(max(max(color.r, color.g), color.b) * (255.0 / 16.0)) / 255.0, 1.0 / 255.0, 1.0);
  return vec4(color / (multiplier * 16.0), multiplier);
}
// Inverse of the existing ACES fit, used only to register already display-referred Sky plates.
vec3 inverseAces(vec3 target) {
  vec3 y = clamp(target, vec3(0.0), vec3(0.98));
  vec3 a = y * 2.43 - 2.51;
  vec3 b = y * 0.59 - 0.03;
  vec3 c = y * 0.14;
  return max((-b - sqrt(max(b * b - 4.0 * a * c, vec3(0.0)))) / (2.0 * a), vec3(0.0));
}
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
vec3 filteredFaceNormal(vec2 uv, vec2 texel, vec3 centerEncoded) {
  vec3 encoded = centerEncoded * 3.0;
  float weight = 3.0;
  for (int index = 0; index < 4; index++) {
    vec2 offset = index == 0 ? vec2(4.0, 0.0) : index == 1 ? vec2(-4.0, 0.0)
      : index == 2 ? vec2(0.0, 4.0) : vec2(0.0, -4.0);
    vec2 neighbor = uv + offset * texel;
    float sameFace = texture(u_materialMask, neighbor).r;
    encoded += texture(u_normal, neighbor).rgb * sameFace;
    weight += sameFace;
  }
  vec3 decoded = encoded / weight * 2.0 - 1.0;
  return normalize(vec3(decoded.x * 2.8, -decoded.y * 2.8, max(decoded.z, 0.001)));
}
float crownRibbon(vec2 sourcePixel) {
  float x = (sourcePixel.x - 1165.0) / 105.0;
  float curveY = 132.0 + 26.0 * x * x + 4.0 * x;
  float width = mix(11.0, 5.0, clamp(abs(x), 0.0, 1.0));
  float offset = (sourcePixel.y - curveY) / width;
  float strandBreakup = 0.76 + 0.24 * sin(sourcePixel.x * 0.17 + sourcePixel.y * 0.07);
  return exp(-offset * offset * 1.25) * strandBreakup;
}
float irisGlint(vec2 sourcePixel, vec2 center, vec3 lightDirection) {
  vec2 highlight = center + vec2(lightDirection.x * 1.7, -1.0);
  vec2 delta = (sourcePixel - highlight) / vec2(3.0, 2.6);
  return exp(-dot(delta, delta) * 1.2);
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
  vec4 material = u_detailEnabled != 0 ? texture(u_materialMask, sampleUv) : vec4(0.0);
  vec3 baseLinear = srgbToLinear(base.rgb);
  // Skin is a slightly warmer reflectance, never a light source.
  baseLinear *= mix(vec3(1.0), vec3(1.005, 0.965, 0.945), material.r);
  vec3 decodedNormal = normalColor * 2.0 - 1.0;
  vec3 normal = normalize(vec3(decodedNormal.x, -decodedNormal.y, decodedNormal.z));
  vec2 texel = 1.0 / vec2(textureSize(u_normal, 0));
  vec3 faceNormal = normal;
  if (material.r > 0.001) {
    faceNormal = filteredFaceNormal(sampleUv, texel, normalColor);
    normal = normalize(mix(normal, faceNormal, material.r * 0.82));
  }
  vec3 lightDirection = normalize(u_lightDirection);
  float ndotl = dot(normal, lightDirection);
  float wrapped = clamp((ndotl + u_diffuseWrap) / (1.0 + u_diffuseWrap), 0.0, 1.0);
  float diffuse = smoothstep(u_diffuseThreshold - u_diffuseSoftness, u_diffuseThreshold + u_diffuseSoftness, wrapped);
  vec3 broadEncoded = normalColor * 4.0
    + texture(u_normal, sampleUv + vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, sampleUv - vec2(texel.x * 5.0, 0.0)).rgb
    + texture(u_normal, sampleUv + vec2(0.0, texel.y * 5.0)).rgb
    + texture(u_normal, sampleUv - vec2(0.0, texel.y * 5.0)).rgb;
  vec3 broadDecoded = broadEncoded / 8.0 * 2.0 - 1.0;
  vec3 broadNormal = normalize(vec3(broadDecoded.x, -broadDecoded.y, broadDecoded.z));
  float broadFacing = dot(broadNormal, lightDirection);
  float paintedBand = bandResponse(broadFacing);
  if (material.r > 0.001) {
    vec3 faceLight = normalize(vec3(lightDirection.x, lightDirection.y * 0.78, lightDirection.z));
    float faceFacing = dot(faceNormal, faceLight);
    float faceSoftness = max(0.15, u_bandSoftness * 0.80);
    float faceBand = smoothstep(u_bandThreshold - faceSoftness, u_bandThreshold + faceSoftness, faceFacing);
    paintedBand = mix(paintedBand, faceBand, material.r);
  }
  float bandDiffuse = mix(0.20, 0.66, paintedBand);
  bandDiffuse = mix(bandDiffuse, mix(0.12, 0.72, paintedBand), material.r);
  float bandWeight = mix(u_bandStrength, max(u_bandStrength, 0.62), material.r);
  float shapedDiffuse = mix(diffuse, bandDiffuse, bandWeight);
  vec3 illumination = u_ambientColor * u_ambientIntensity
    + u_lightColor * (shapedDiffuse * u_lightIntensity);
  // Broad solar separation follows the existing continuous sun direction. Low
  // daylight angles reveal side-facing planes; overhead sun softens them and
  // the night key fades out before it can cast a false solar shadow.
  float solarPresence = smoothstep(0.25, 0.48, u_lightIntensity);
  float lowSun = 1.0 - smoothstep(0.54, 0.89, lightDirection.z);
  float solarResponse = u_directionalStrength * solarPresence * (0.15 + 0.85 * lowSun);
  vec2 directionalSlope = broadDecoded.xy;
  if (material.r > 0.001) {
    directionalSlope = mix(directionalSlope, faceNormal.xy / 2.8, material.r * 0.48);
  }
  // Center the new band on the horizontal slope instead of the upward Z
  // component. Otherwise low Sun merely darkens both morning and evening.
  float solarFacing = directionalSlope.x * lightDirection.x * 11.0
    + directionalSlope.y * lightDirection.y * 2.5;
  float solarBand = smoothstep(-0.42, 0.42, solarFacing);
  // Flat painted masonry carries almost no XY slope in Normal v3. A weak,
  // broad spatial falloff lets the side light read across the composition.
  float paintedSide = clamp((0.5 - v_uv.x) * lightDirection.x * 0.60, -0.20, 0.20);
  solarResponse *= 1.0 - material.r * 0.18;
  illumination *= 1.0 + ((solarBand - 0.5) * 1.10 + paintedSide) * solarResponse;
  float upperSceneMask = 1.0 - smoothstep(0.28, 0.68, v_uv.y);
  float upperSceneFactor = 1.0 - upperSceneMask * clamp(u_upperSceneAttenuation, 0.0, 1.0);
  illumination *= upperSceneFactor;
  vec3 relitLinear = max(baseLinear * illumination, vec3(0.0));
  if (material.g > 0.001) {
    float dayVisibility = smoothstep(0.22, 0.48, u_lightIntensity);
    float facing = 0.35 + 0.65 * smoothstep(-0.10, 0.75, broadFacing);
    float paintedStrand = mix(0.52, 1.0, smoothstep(0.055, 0.24, baseLinear.r));
    float sheen = material.g * crownRibbon(sampleUv * vec2(1672.0, 941.0))
      * facing * paintedStrand * dayVisibility * u_lightIntensity * 0.155;
    relitLinear += u_lightColor * sheen;
  }
  if (material.b > 0.001 && u_blinkClosed == 0) {
    vec2 sourcePixel = sampleUv * vec2(1672.0, 941.0);
    float glint = max(irisGlint(sourcePixel, vec2(1123.0, 219.0), lightDirection),
      irisGlint(sourcePixel, vec2(1187.0, 238.0), lightDirection));
    float dayVisibility = smoothstep(0.22, 0.48, u_lightIntensity);
    vec3 reflection = u_lightColor * u_lightIntensity * (0.075 * dayVisibility)
      + u_ambientColor * u_ambientIntensity * (0.012 * (1.0 - dayVisibility));
    relitLinear += reflection * glint * material.b;
  }
  vec3 blendedLinear = mix(baseLinear, relitLinear, clamp(u_relightStrength, 0.0, 1.0));
  if (u_sceneLinear != 0) {
    float skyAlpha = 0.0;
    vec3 sceneLinear = blendedLinear;
    if (u_skyEnabled != 0) {
      vec4 sky = mix(sampleSky(u_skyPhaseA), sampleSky(u_skyPhaseB), clamp(u_skyMix, 0.0, 1.0));
      skyAlpha = clamp(sky.a, 0.0, 1.0);
      // The frozen Sky RGB is display-referred. Place its inverse display value
      // in the linear scene so the one Post ACES pass recovers the same plate.
      vec3 skyLinear = inverseAces(srgbToLinear(sky.rgb)) / exp2(u_exposure);
      sceneLinear = mix(sceneLinear, skyLinear, skyAlpha);
    }
    outColor = encodeHDR(sceneLinear);
    vec2 sourcePixel = sampleUv * vec2(1672.0, 941.0);
    float shirtArea = smoothstep(850.0, 950.0, sourcePixel.x)
      * (1.0 - smoothstep(1490.0, 1570.0, sourcePixel.x))
      * smoothstep(270.0, 340.0, sourcePixel.y)
      * (1.0 - smoothstep(650.0, 720.0, sourcePixel.y));
    float whiteFabric = smoothstep(0.60, 0.84, min(min(base.rgb.r, base.rgb.g), base.rgb.b));
    outBloomGate = vec4((1.0 - skyAlpha) * (1.0 - 0.82 * shirtArea * whiteFabric), 0.0, 0.0, 1.0);
    return;
  }
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
