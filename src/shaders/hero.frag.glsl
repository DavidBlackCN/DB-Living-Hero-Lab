#version 300 es
precision highp float;
in vec2 v_uv;
uniform sampler2D u_base;
uniform sampler2D u_normal;
uniform sampler2D u_sky[4];
uniform sampler2D u_skyEdgeReconstruction;
uniform sampler2D u_skyEdgeCoverage;
uniform sampler2D u_hairMask;
uniform sampler2D u_materialMask;
uniform sampler2D u_lampSource;
uniform sampler2D u_lampInfluence;
uniform sampler2D u_sceneDepth;
uniform sampler2D u_towerReceiver;
uniform float u_atmosphereProtection;
uniform sampler2D u_blinkLeft;
uniform sampler2D u_blinkRight;
uniform int u_view;
uniform int u_lightingEnabled;
uniform int u_skyEnabled;
uniform int u_skyRepairEnabled;
uniform float u_blinkAmount;
uniform int u_skyPhaseA;
uniform int u_skyPhaseB;
uniform float u_skyMix;
uniform float u_skyNightWeight;
uniform float u_exposure;
uniform float u_relightStrength;
uniform vec3 u_lightDirection;
uniform vec3 u_moonDirection;
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
uniform float u_hairSheenStrength;
uniform int u_hairOverlay;
uniform int u_detailEnabled;
uniform int u_sceneLinear;
uniform float u_lampWeight;
uniform int u_lampMaskView;
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
// Registered receiver geometry, not illumination masks. Frozen Normal v3 has
// almost neutral normals on these distant tower faces. Give the visible front
// and right planes coherent orientations while retaining shallow painted relief.
float masonryTower(vec2 p, vec4 bounds) {
  vec2 lower = smoothstep(bounds.xy, bounds.xy + vec2(4.0), p);
  vec2 upper = 1.0 - smoothstep(bounds.zw - vec2(4.0), bounds.zw, p);
  return lower.x * lower.y * upper.x * upper.y;
}
vec3 towerReceiver(vec2 p, float corner, float cornerWidth, vec3 broad) {
  float side = smoothstep(corner - cornerWidth, corner + cornerWidth, p.x);
  vec3 plane = mix(vec3(-0.32, 0.0, 0.95), vec3(0.72, 0.0, 0.69), side);
  return normalize(plane + vec3(broad.xy * 1.5, 0.0));
}
vec4 architectureReceiver(vec2 p, vec3 broad, vec3 pigment, float foregroundReceive) {
  vec3 receiver = normalize(vec3(broad.x * 14.0, -broad.y * 6.0, broad.z));
  // Stone planes only: russet foliage keeps its existing broad Normal.
  float chroma = max(abs(pigment.r - pigment.g), abs(pigment.g - pigment.b));
  float stone = 1.0 - smoothstep(0.08, 0.16, chroma);
  stone *= smoothstep(0.40, 0.65, max(max(pigment.r, pigment.g), pigment.b));
  vec4 towers[4] = vec4[4](vec4(910.0, -10.0, 1056.0, 350.0),
    vec4(1319.0, 158.0, 1394.0, 296.0), vec4(1442.0, 214.0, 1480.0, 354.0),
    vec4(1496.0, 173.0, 1544.0, 297.0));
  float corners[4] = float[4](997.0, 1358.0, 1461.0, 1523.0);
  // Pale shirts can match stone pigment. Material/garment coverage must win
  // over the architectural rectangle, including its soft boundary.
  stone *= 1.0 - smoothstep(0.03, 0.20, foregroundReceive);
  float masonry = 0.0;
  for (int index = 0; index < 4; index++) {
    float coverage = masonryTower(p, towers[index]) * stone;
    masonry = max(masonry, coverage);
    receiver = normalize(mix(receiver, towerReceiver(p, corners[index],
      clamp((towers[index].z - towers[index].x) * 0.05, 2.0, 7.0),
      vec3(broad.x, -broad.y, broad.z)), coverage));
  }
  return vec4(receiver, masonry);
}
vec3 breathRegions(vec2 sourcePixel) {
  float core = softEllipse(sourcePixel, vec2(1152.0, 461.0), vec2(103.0, 137.0));
  float shoulder = softEllipse(sourcePixel, vec2(1151.0, 385.0), vec2(155.0, 99.0));
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
vec4 sampleSky(int phase, vec2 uv) {
  if (phase == 0) return texture(u_sky[0], uv);
  if (phase == 1) return texture(u_sky[1], uv);
  if (phase == 2) return texture(u_sky[2], uv);
  return texture(u_sky[3], uv);
}
float bandResponse(float facing) {
  float edge = max(u_bandSoftness, 0.001);
  return smoothstep(u_bandThreshold - edge, u_bandThreshold + edge, facing);
}
vec3 filteredFaceNormal(vec2 uv, vec2 texel, vec3 centerEncoded) {
  vec3 encoded = centerEncoded * 3.0;
  float weight = 3.0;
  for (int index = 0; index < 4; index++) {
    vec2 offset = index == 0 ? vec2(7.0, 0.0) : index == 1 ? vec2(-7.0, 0.0)
      : index == 2 ? vec2(0.0, 7.0) : vec2(0.0, -7.0);
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
    float breathLink = u_breathStrength > 0.0 ? 1.0 : 0.0;
    float headInhale = 0.5 - 0.5 * cos(u_breathPhase - 0.24);
    vec2 headPx = vec2(
      breathLink * 0.32 * sin(u_breathPhase - 0.34)
        + 0.12 * sin(primary + 0.45) + 0.06 * sin(secondary + 1.05),
      breathLink * 0.74 * headInhale + 0.08 * sin(secondary + 0.85)
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
  if ((u_view == 2 || (u_view == 0 && u_headMassStrength > 0.0)) && u_blinkAmount > 0.0) {
    vec2 sourcePixel = sampleUv * vec2(1672.0, 941.0);
    if (sourcePixel.x >= 1080.0 && sourcePixel.x < 1172.0 && sourcePixel.y >= 177.0 && sourcePixel.y < 250.0) {
      vec4 closedEye = texture(u_blinkLeft, (sourcePixel - vec2(1080.0, 177.0)) / vec2(92.0, 73.0));
      base.rgb = mix(base.rgb, closedEye.rgb, closedEye.a * u_blinkAmount);
    }
    if (sourcePixel.x >= 1152.0 && sourcePixel.x < 1244.0 && sourcePixel.y >= 195.0 && sourcePixel.y < 273.0) {
      vec4 closedEye = texture(u_blinkRight, (sourcePixel - vec2(1152.0, 195.0)) / vec2(92.0, 78.0));
      base.rgb = mix(base.rgb, closedEye.rgb, closedEye.a * u_blinkAmount);
    }
  }
  if (u_view == 0) { outColor = vec4(showMotionRegions(base.rgb, regions, hairRegion), base.a); return; }
  vec3 normalColor = texture(u_normal, sampleUv).rgb;
  if (u_view == 1) { outColor = vec4(showMotionRegions(normalColor, regions, hairRegion), 1.0); return; }
  if (u_lightingEnabled == 0) { outColor = vec4(showMotionRegions(base.rgb, regions, hairRegion), base.a); return; }
  if (u_lampMaskView != 0) {
    vec2 channels = u_lampMaskView == 1 ? texture(u_lampSource, sampleUv).rg
      : texture(u_lampInfluence, sampleUv).rg;
    outColor = vec4(channels.r, channels.g, 0.0, 1.0);
    return;
  }
  // Recover foreground pigment from old-sky-contaminated edge pixels before
  // the regular lighting and Sky composition. No display-space edge shading.
  vec4 edgeRepair = texture(u_skyEdgeReconstruction, sampleUv);
  if (u_skyEnabled != 0 && u_skyRepairEnabled != 0) base.rgb = mix(base.rgb, edgeRepair.rgb, edgeRepair.a);
  vec4 edgeSkyfill = texture(u_skyEdgeCoverage, sampleUv);
  if (u_skyEnabled != 0 && u_skyRepairEnabled != 0) base.rgb = mix(base.rgb, edgeSkyfill.rgb, edgeSkyfill.a * u_skyNightWeight);
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
  // Sky sets the twilight window. The Sun can take over only once its key is
  // strong enough, preventing an early-Dawn dip while the Moon fades out.
  float skyNight = clamp(u_skyNightWeight, 0.0, 1.0);
  float solarReady = smoothstep(0.20, 0.53, u_lightIntensity);
  float solarPresence = (1.0 - skyNight) * solarReady;
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
  vec2 characterPixel = sampleUv * vec2(1672.0, 941.0);
  float whitePigment = smoothstep(0.38, 0.62, min(min(base.rgb.r, base.rgb.g), base.rgb.b))
    * (1.0 - smoothstep(0.09, 0.20, max(abs(base.rgb.r - base.rgb.g), abs(base.rgb.g - base.rgb.b))));
  float sleeves = max(softEllipse(characterPixel, vec2(971.0, 465.0), vec2(126.0, 205.0)),
    softEllipse(characterPixel, vec2(1327.0, 469.0), vec2(110.0, 214.0))) * whitePigment;
  float vestPigment = smoothstep(0.015, 0.065, base.rgb.r - base.rgb.g)
    * (1.0 - smoothstep(0.28, 0.48, base.rgb.g));
  float vest = softEllipse(characterPixel, vec2(1159.0, 459.0), vec2(150.0, 184.0)) * vestPigment;
  float garment = max(sleeves, vest);
  // Character Lighting Core: the figure shares the same Sun/Moon field.
  // The registered masks below change only how each material receives it.
  float directionalControl = clamp(u_directionalStrength, 0.0, 1.0);
  float morning = smoothstep(0.08, 0.50, lightDirection.x) * lowSun * solarPresence * directionalControl;
  float dusk = (1.0 - smoothstep(-0.48, -0.08, lightDirection.x)) * lowSun * solarPresence * directionalControl;
  float hairPigment = smoothstep(0.025, 0.08, base.rgb.r - base.rgb.g)
    * (1.0 - smoothstep(0.44, 0.68, base.rgb.g));
  // Core region registration stays active with R5 Detail OFF; that switch
  // controls the material polish, not whether the character receives light.
  vec4 responseMask = texture(u_materialMask, sampleUv);
  float faceEyes = max(softEllipse(characterPixel, vec2(1123.0, 219.0), vec2(35.0, 26.0)),
    softEllipse(characterPixel, vec2(1187.0, 238.0), vec2(34.0, 25.0)));
  float faceRegion = max(responseMask.r, faceEyes * 0.90);
  float hairRegionWeight = max(responseMask.g,
    max(max(hairRegion.r, hairRegion.g), max(hairRegion.a, hairRegion.b)))
    * hairPigment * (1.0 - faceRegion);
  float skirt = softEllipse(characterPixel, vec2(1172.0, 746.0), vec2(235.0, 285.0))
    * vestPigment;
  float clothing = max(garment, skirt);
  vec4 architectureField = architectureReceiver(characterPixel, broadDecoded, base.rgb,
    max(max(responseMask.r, responseMask.g), clothing));
  float accessory = hairRegion.b * (1.0 - max(faceRegion, hairRegionWeight));
  float character = max(max(faceRegion, hairRegionWeight), max(clothing, accessory));
  // Head-motion coverage intentionally includes a little background for UV
  // continuity. It is not a material mask: registered stone inside that envelope
  // must receive the building Moon key, not the character/accessory fill.
  character *= 1.0 - architectureField.a * skyNight;

  // One broad receiving plane for both solar and lunar character shading.
  // Wider taps calm individual painted strokes without changing the Normal asset.
  vec3 characterBroadDecoded = broadDecoded;
  if (character > 0.001) {
    vec3 characterBroad = broadEncoded
      + texture(u_normal, sampleUv + vec2(texel.x * 14.0, 0.0)).rgb
      + texture(u_normal, sampleUv - vec2(texel.x * 14.0, 0.0)).rgb
      + texture(u_normal, sampleUv + vec2(0.0, texel.y * 14.0)).rgb
      + texture(u_normal, sampleUv - vec2(0.0, texel.y * 14.0)).rgb;
    characterBroadDecoded = characterBroad / 12.0 * 2.0 - 1.0;
  }
  vec3 characterBroadNormal = normalize(vec3(characterBroadDecoded.x,
    -characterBroadDecoded.y, characterBroadDecoded.z));

  // A shared soft morning key lifts the receiving side across all materials.
  // It replaces the former hair/face/shirt-specific Dawn fill patches.
  float characterDiffuse = mix(shapedDiffuse, 0.54, morning * 0.32);
  // The broad painted back-facing hair normals should still receive a little
  // clear morning key; keep this tied to the shared light and hair material.
  characterDiffuse = mix(characterDiffuse, 0.61,
    hairRegionWeight * morning * 0.42);
  illumination = mix(illumination,
    u_ambientColor * u_ambientIntensity + u_lightColor * u_lightIntensity * characterDiffuse,
    character);
  // Face pass: broaden the shared key response across the whole face and both
  // eyes. There are no separately lit cheek, iris-underlay or eye-socket spots.
  float faceDiffuse = mix(shapedDiffuse, 0.53, morning * 0.80 + dusk * 0.22);
  illumination = mix(illumination,
    u_ambientColor * u_ambientIntensity + u_lightColor * u_lightIntensity * faceDiffuse,
    faceRegion);
  // Hair, clothing and accessories retain progressively stronger directional
  // volume; morning has a softer receiving side than sunset.
  float characterGain = mix(0.56, 0.90, hairRegionWeight);
  characterGain = mix(characterGain, 0.72, clothing);
  characterGain = mix(characterGain, 0.50, accessory);
  characterGain = mix(characterGain, mix(0.25, 0.21, morning), faceRegion);
  float characterSolarFacing = characterBroadDecoded.x * lightDirection.x * 11.0
    + characterBroadDecoded.y * lightDirection.y * 2.5;
  float characterSolarBand = smoothstep(-0.47, 0.47, characterSolarFacing);
  float sharedSolarBand = mix(solarBand, characterSolarBand,
    0.65 * (1.0 - faceRegion));
  float characterBand = (sharedSolarBand - 0.5) * characterGain * mix(1.0, 0.54, morning);
  characterBand *= 1.0 - hairRegionWeight * morning * 0.58;
  float sceneBand = (solarBand - 0.5) * 1.10 + paintedSide;
  illumination *= 1.0 + mix(sceneBand, characterBand, character) * solarResponse;
  // The Moon takes over the same character core during twilight. It does not
  // add a second face-specific light on top of a leftover solar key.
  vec3 moonDirection = normalize(u_moonDirection);
  float moonHeightGain = mix(0.55, 1.0, smoothstep(0.20, 0.80, moonDirection.z));
  float moonHandoff = (1.0 - solarPresence) * directionalControl;
  float moonPresence = skyNight * directionalControl * moonHeightGain;
  float characterMoonFacing = dot(characterBroadNormal.xy, moonDirection.xy) * 10.0;
  float characterMoonBand = smoothstep(-1.15, 1.15, characterMoonFacing);
  // Face uses the same Moon vector, but its filtered front-facing Normal
  // suppresses steep vertical eye/cheek transitions rather than adding fill.
  vec3 faceMoonLight = normalize(vec3(moonDirection.x, moonDirection.y * 0.24,
    max(moonDirection.z, 0.85)));
  float faceMoonFacing = dot(faceNormal, faceMoonLight) - 0.70;
  float faceMoonBand = smoothstep(-0.30, 0.30, faceMoonFacing);
  float characterMoonReceive = clamp(0.39 + (characterMoonBand - 0.5) * 0.70,
    0.08, 0.78);
  float faceMoonReceive = 0.43 + (faceMoonBand - 0.5) * 0.28;
  float materialMoonReceive = mix(characterMoonReceive, faceMoonReceive, faceRegion);
  materialMoonReceive = mix(materialMoonReceive, 0.39,
    hairRegionWeight * moonPresence * 0.48);
  float moonMaterialGain = mix(1.0, 1.17, clothing);
  moonMaterialGain = mix(moonMaterialGain, 1.25, vest);
  moonMaterialGain = mix(moonMaterialGain, 1.08, hairRegionWeight);
  moonMaterialGain = mix(moonMaterialGain, 0.88, accessory);
  moonMaterialGain = mix(moonMaterialGain, 1.00, faceRegion);
  float moonDiffuse = max(0.10, 0.28 + (materialMoonReceive - 0.39) * 0.80);
  vec3 nightCharacter = u_ambientColor * u_ambientIntensity
    + vec3(0.35, 0.51, 0.82) * moonMaterialGain * moonDiffuse;
  illumination = mix(illumination, nightCharacter, character * moonHandoff);
  // Architecture hands its direct key over to the same independent Moon arc.
  // Normal v3 stores shallow painted masonry slopes: expand their broad XY
  // response, with the same top-left Y convention as the character Normal.
  // No screen-side bias or constant additive Moon strip survives this handoff.
  vec3 architectureNormal = architectureField.xyz;
  float architectureMoonFacing = dot(architectureNormal, moonDirection);
  // Wrapped broad receive keeps the back plane readable without a separate fill strip.
  float architectureMoonReceive = smoothstep(-0.75, 1.10, architectureMoonFacing);
  // A broad, quiet sky fill keeps back-facing stone readable without holding
  // the painted bright side at the same prominence throughout the night.
  vec3 nightArchitecture = u_ambientColor * u_ambientIntensity * 0.88
    + vec3(0.35, 0.51, 0.82) * (0.22 * moonHeightGain * architectureMoonReceive);
  illumination = mix(illumination, nightArchitecture,
    skyNight * moonHandoff * (1.0 - character));
  float upperSceneMask = 1.0 - smoothstep(0.28, 0.68, v_uv.y);
  float upperSceneFactor = 1.0 - upperSceneMask * clamp(u_upperSceneAttenuation, 0.0, 1.0);
  illumination *= upperSceneFactor;
  // The lower strands taper out of the character core. Balance their painted
  // pigment along the existing feathered motion regions, then leave their
  // broad Normal and the shared Sun/Moon direction intact.
  illumination *= 1.0 + hairPigment * (
    hairRegion.r * morning * 2.65 - hairRegion.g * moonPresence * 0.68);
  vec3 relitLinear = max(baseLinear * illumination, vec3(0.0));
  // Hair volume is already lit by the shared broad Normal above. Optional
  // sheen remains only a narrow crown polish, never a second lunar key.
  relitLinear += vec3(0.28, 0.43, 0.72) * responseMask.g
    * crownRibbon(characterPixel) * hairPigment * materialMoonReceive
    * moonPresence * 0.012 * u_hairSheenStrength;
  if (material.g > 0.001) {
    float dayVisibility = smoothstep(0.22, 0.48, u_lightIntensity);
    float facing = 0.35 + 0.65 * smoothstep(-0.10, 0.75, broadFacing);
    float paintedStrand = mix(0.52, 1.0, smoothstep(0.055, 0.24, baseLinear.r));
    float sheen = material.g * crownRibbon(sampleUv * vec2(1672.0, 941.0))
      * facing * paintedStrand * dayVisibility * u_lightIntensity * 0.155;
    relitLinear += u_lightColor * sheen * u_hairSheenStrength;
  }
  if (material.b > 0.001 && u_blinkAmount < 1.0) {
    vec2 sourcePixel = sampleUv * vec2(1672.0, 941.0);
    float glint = max(irisGlint(sourcePixel, vec2(1123.0, 219.0), lightDirection),
      irisGlint(sourcePixel, vec2(1187.0, 238.0), lightDirection));
    float dayVisibility = smoothstep(0.22, 0.48, u_lightIntensity);
    float duskGlintSoftening = dusk;
    vec3 reflection = u_lightColor * u_lightIntensity
      * (0.075 * dayVisibility * mix(1.0, 0.40, duskGlintSoftening))
      + u_ambientColor * u_ambientIntensity * (0.012 * (1.0 - dayVisibility));
    relitLinear += reflection * glint * material.b * (1.0 - u_blinkAmount);
    // The painted iris already carries a warm glint. Compress only its
    // brightest sunset pixels, leaving the dark pupil and Noon unchanged.
    float irisBrightness = dot(relitLinear, vec3(0.2126, 0.7152, 0.0722));
    float hotIris = smoothstep(0.12, 0.50, irisBrightness);
    relitLinear *= 1.0 - duskGlintSoftening * material.b * hotIris * 0.38;
  }
  // Registered masonry has priority over pigment/motion receive fragments.
  // This late-night surface pass changes radiance only: character receive and
  // Atmosphere/Bloom metadata stay frozen. Both faces share one Moon vector.
  float towerSurface = texture(u_towerReceiver, sampleUv).r;
  float towerLateWeight = smoothstep(0.40, 0.60, -moonDirection.x)
    * skyNight * moonHandoff;
  float towerCorner = smoothstep(986.0, 1012.0, characterPixel.x);
  vec3 towerNormal = normalize(mix(vec3(-0.70, 0.0, 0.71),
    vec3(0.71, 0.0, 0.70), towerCorner));
  // A small wrapped floor softens the back plane without restoring fragmentary fill.
  float towerShadowFloor = mix(0.06, 0.10, smoothstep(0.20, 0.40, moonDirection.z));
  float towerReceive = mix(towerShadowFloor, 1.00,
    smoothstep(-0.30, 1.00, dot(towerNormal, moonDirection)));
  vec3 towerMoon = u_ambientColor * u_ambientIntensity * 0.88
    + vec3(0.35, 0.51, 0.82) * (0.48 * moonHeightGain * towerReceive);
  relitLinear = mix(relitLinear, baseLinear * towerMoon * upperSceneFactor, towerSurface * towerLateWeight);
  vec3 lampEmissive = vec3(0.0);
  vec3 lampGlow = vec3(0.0);
  if (u_lampWeight > 0.0) {
    vec2 lampPixel = sampleUv * vec2(1672.0, 941.0);
    vec2 source = texture(u_lampSource, sampleUv).rg;
    vec2 reach = texture(u_lampInfluence, sampleUv).rg;
    vec3 lampA = normalize(vec3((52.0 - lampPixel.x) / 185.0, (lampPixel.y - 146.0) / 185.0, 0.62));
    vec3 lampB = normalize(vec3((159.0 - lampPixel.x) / 170.0, (lampPixel.y - 262.0) / 170.0, 0.62));
    float receiveA = smoothstep(-0.22, 0.70, dot(broadNormal, lampA));
    float receiveB = smoothstep(-0.22, 0.70, dot(broadNormal, lampB));
    float surfaceA = reach.r * mix(0.25, 1.0, receiveA);
    float surfaceB = reach.g * mix(0.25, 1.0, receiveB);
    // Registered masks bound the light to corridor stone and ivy. The broad
    // Normal shapes the actual surface response even when Bloom is disabled.
    relitLinear += baseLinear * u_lampWeight
      * (vec3(0.43, 0.20, 0.070) * surfaceA
        + vec3(0.38, 0.16, 0.045) * surfaceB);
    lampEmissive = u_lampWeight * (vec3(0.85, 0.44, 0.15) * source.r
      + vec3(0.78, 0.35, 0.10) * source.g);
    vec2 nearDist = (lampPixel - vec2(52.0, 146.0)) / vec2(34.0, 50.0);
    vec2 farDist = (lampPixel - vec2(159.0, 262.0)) / vec2(29.0, 44.0);
    lampGlow = u_lampWeight * vec3(0.65, 0.25, 0.06)
      * (0.012 * exp(-dot(nearDist, nearDist) * 1.8)
        + 0.010 * exp(-dot(farDist, farDist) * 1.8));
  }
  vec3 blendedLinear = mix(baseLinear, relitLinear, clamp(u_relightStrength, 0.0, 1.0))
    + lampEmissive + lampGlow;
  if (u_sceneLinear != 0) {
    float skyAlpha = 0.0;
    vec3 sceneLinear = blendedLinear;
    if (u_skyEnabled != 0) {
      vec4 sky = mix(sampleSky(u_skyPhaseA, sampleUv), sampleSky(u_skyPhaseB, sampleUv), clamp(u_skyMix, 0.0, 1.0));
      skyAlpha = max(clamp(sky.a, 0.0, 1.0), texture(u_skyEdgeCoverage, sampleUv).a * u_skyNightWeight * float(u_skyRepairEnabled));
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
    float eligibility = (1.0 - skyAlpha) * (1.0 - 0.82 * shirtArea * whiteFabric);
    // Only emissive glass should feed a lamp halo; lit masonry is a surface.
    // This is Bloom metadata. It never changes the frozen scene illumination.
    float lampReach = max(texture(u_lampInfluence, sampleUv).r,
      texture(u_lampInfluence, sampleUv).g) * u_lampWeight;
    float lampGlass = max(texture(u_lampSource, sampleUv).r,
      texture(u_lampSource, sampleUv).g) * min(u_lampWeight, 1.0);
    float protectedGate = eligibility * (1.0 - 0.90 * character) * (1.0 - 0.85 * lampReach);
    eligibility = mix(eligibility, max(protectedGate, lampGlass), u_atmosphereProtection);
    float depth = texture(u_sceneDepth, sampleUv).r * (1.0 - skyAlpha) * (1.0 - character);
    outBloomGate = vec4(eligibility, depth, 0.0, 1.0);
    return;
  }
  vec3 exposedLinear = blendedLinear * exp2(u_exposure);
  vec3 displayLinear = toneMapAces(exposedLinear);
  if (u_skyEnabled != 0) {
    vec4 skyA = sampleSky(u_skyPhaseA, sampleUv);
    vec4 skyB = sampleSky(u_skyPhaseB, sampleUv);
    vec4 sky = mix(skyA, skyB, clamp(u_skyMix, 0.0, 1.0));
    vec3 skyLinear = srgbToLinear(sky.rgb);
    float skyAlpha = max(clamp(sky.a, 0.0, 1.0), texture(u_skyEdgeCoverage, sampleUv).a * u_skyNightWeight * float(u_skyRepairEnabled));
    displayLinear = mix(displayLinear, skyLinear, skyAlpha);
  }
  vec3 displayColor = linearToSrgb(displayLinear);
  outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);
}
