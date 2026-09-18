import { lightLayers } from './light-layers';
import { lampFields } from './lamp-fields';

export const vertex = `#version 300 es
precision highp float;
out vec2 uv;
void main() {
  vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
  uv = vec2(p.x, 1.0-p.y);
  gl_Position = vec4(p*2.0-1.0, 0.0, 1.0);
}`;
export const fragment = `#version 300 es
precision highp float;
in vec2 uv;
out vec4 color;
uniform sampler2D uBase, uNormal, uMask, uSceneMask;
uniform sampler2D uLightShaping;
uniform sampler2D uBloomMap;
uniform sampler2D uCorrectionMap;
uniform bool uHasCorrection;
uniform float uCorrection;
uniform float uShadow;
uniform float uBloom, uBloomThreshold, uBloomMood;
uniform bool uHasNormal, uHasMask, uHasSceneMask, uHasLightShaping;
uniform vec3 uAmbient, uSun, uDirection;
uniform float uLamp, uExposure, uAmbientStrength, uSunStrength, uLampStrength, uNormalStrength, uFace;
uniform float uHair, uCloth, uNight, uNightStrength, uRefinement, uStylized, uSoftness, uProjected, uProjectedIntensity, uProjectedSoftness, uMotionTime, uSteam;
uniform int uView;
uniform float uMinutes;
uniform vec4 uProjectionGeometry, uProjectionShape;
uniform float uProjectionEnergy;
float region(vec2 p, vec2 center, vec2 radius) {
  return 1.0-smoothstep(0.60,1.0,length((p-center)/radius));
}
vec3 linearize(vec3 c) { return mix(c/12.92, pow((c+0.055)/1.055,vec3(2.4)),step(vec3(0.04045),c)); }
vec3 encode(vec3 c) { return mix(c*12.92,1.055*pow(max(c,0.0),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),c)); }
// Broad wrapped diffuse for an illustration: no specular, micro-normal or
// hard terminator. The aperture/field determines visibility, N.L orientation.
float surfaceResponse(vec3 n, vec3 l) {
  return .18+.82*max(dot(n,l),0.0);
}
// The coarse face mask starts below the fringe. Exposed forehead slivers above
// it otherwise inherit hair normals/occlusion and meet the protected cheek at
// a hard brightness step. Extend lighting safety only over source skin here;
// these soft bounds are in the artwork's 1200x675 reference coordinates.
float foreheadSafety(vec2 p, vec3 pigment) {
  vec2 at=p*vec2(1200.0,675.0);
  float area=smoothstep(661.0,674.0,at.x)*(1.0-smoothstep(788.0,800.0,at.x))*
    smoothstep(110.0,128.0,at.y)*(1.0-smoothstep(177.0,190.0,at.y));
  // Bright peach skin has a higher G and B/G ratio than the adjacent brown hair.
  // A broad pigment transition preserves lashes, brows and painted fringe shade.
  float skin=smoothstep(.66,.82,pigment.g)*
    smoothstep(.78,.90,pigment.b/max(pigment.g,.001));
  return area*skin;
}
${lightLayers}
${lampFields}
void main() {
  vec3 base = texture(uBase,uv).rgb;
  if(uView==1) { color=vec4(base,1); return; }
  bool refined = uRefinement > .5;
  vec3 scene = uHasSceneMask && refined ? texture(uSceneMask,uv).rgb : vec3(0);
  // Source-authored glass geometry has native subpixel antialiasing, no erosion.
  // Scene, Overlay, lamp exclusion and night suppression share this exact value.
  float exterior = scene.r;
  if(uView==11) { color=vec4(vec3(exterior),1); return; }
  float night = refined ? uNight*uNightStrength : 0.0;
  bool spatial=refined && uHasLightShaping && uHasSceneMask;
  vec3 shape=spatial ? texture(uLightShaping,uv).rgb : vec3(1,0,0);
  // All positions use the original artwork's top-left UV coordinates.
  float face = region(uv,vec2(.608,.292),vec2(.074,.107));
  float body = region(uv,vec2(.551,.585),vec2(.195,.24));
  float hair = region(uv,vec2(.605,.37),vec2(.185,.36))*(1.0-face)*(1.0-body);
  if(uHasMask && refined) { vec3 masks=texture(uMask,uv).rgb; face=masks.r; hair=masks.g; body=masks.b; }
  float forehead=refined && uHasMask ? foreheadSafety(uv,base)*(1.0-face) : 0.0;
  face+=forehead; // Soft union: overlapping feathered edges must not form a dip.
  hair=max(hair-forehead,0.0); // Transfer coverage, rather than double-count skin.
  vec2 f=(uv-vec2(.608,.292))/vec2(.074,.107);
  vec2 h=(uv-vec2(.605,.37))/vec2(.185,.36);
  vec3 normal=normalize(vec3(f*.20*face+h*.22*hair,1.0));
  // Table and window have distinct, broad orientation responses.
  float table=smoothstep(.70,.85,uv.y)*smoothstep(.39,.58,uv.x);
  normal=normalize(mix(normal,vec3(0.0,-.50,.866),table));
  if(uHasNormal && refined) normal=normalize(texture(uNormal,uv).rgb*2.0-1.0);
  normal=normalize(mix(vec3(0,0,1),normal,uNormalStrength));
  // Only newly protected skin loses the erroneous hair-ribbon normal. Retain
  // a quarter of its local orientation; lower face and actual hair are unchanged.
  normal=normalize(mix(normal,vec3(0,0,1),forehead*.75*uFace));
  float diffuse=.35+.65*max(dot(normal,normalize(uDirection)),0.0);
  float broad=smoothstep(.38-uSoftness,.62+uSoftness,dot(normal,normalize(uDirection)));
  diffuse=mix(diffuse,mix(.48,1.0,broad),uStylized);
  float window=smoothstep(.43,.94,uv.x);
  float receive=mix(.36,1.0,window);
  if(refined) receive *= 1.0 + hair*(uHair-1.0) + body*(uCloth-1.0);
  vec3 directional=uSun*uSunStrength*diffuse*receive;
  vec3 light=uAmbient*uAmbientStrength+directional;
  float lampBulb=region(uv,vec2(.80,.32),vec2(.035,.027));
  if(refined && uHasSceneMask) {
    lampBulb = scene.b;
  }
  float dusk=smoothstep(780.0,1050.0,uMinutes);
  vec2 axis=normalize(uProjectionGeometry.zw);
  vec2 delta=(uv-uProjectionGeometry.xy)*vec2(1200.0/675.0,1.0);
  float along=dot(delta,axis);
  float across=dot(delta,vec2(-axis.y,axis.x));
  float width=uProjectionShape.x + max(along,0.0)*uProjectionShape.y + (uProjectedSoftness-.22)*.12;
  width=max(width,.025);
  // Two diffuse aperture lobes, with a soft mullion gap. Widening penumbra
  // and distance falloff avoid a flat translucent rectangle over the image.
  float upper=exp(-2.0*pow(across/width,2.0));
  float lower=exp(-2.0*pow((across+uProjectionShape.z)/(width*1.12),2.0));
  float projectedBand=1.0-(1.0-upper)*(1.0-lower*.78);
  // The gap between panes removes energy instead of adding another warm stripe.
  float mullion=exp(-pow((across+uProjectionShape.z*.48)/(.015+uProjectedSoftness*.035+max(along,0.0)*.012),2.0));
  projectedBand*=1.0-mullion*.78;
  float projectedReach=smoothstep(-.06,.08,along)*(1.0-smoothstep(uProjectionShape.w*.58,uProjectionShape.w,along));
  float receiver=max(scene.g,max(hair*.82*uHair,body*.62*uCloth));
  receiver=clamp(receiver,0.0,1.0)*(1.0-exterior)*(1.0-face);
  float projectedAmount=(refined && uHasSceneMask ? 1.0 : 0.0)*uProjected*uProjectedIntensity*uSunStrength*uProjectionEnergy*projectedBand*projectedReach*receiver;
  projectedAmount *= surfaceResponse(normal,normalize(uDirection));
  // Same window aperture on the upright room plane, foreshortened relative to
  // the desk plane. Soft source-authored G weights keep shelves/foreground quiet.
  // This is receiving light, not an atmospheric overlay or displaced shadow.
  if(spatial) {
    vec2 roomAxis=normalize(vec2(-1.0,axis.y*.40));
    float roomAlong=dot(delta,roomAxis);
    float roomAcross=dot(delta,vec2(-roomAxis.y,roomAxis.x));
    float roomWidth=uProjectionShape.x*1.25+max(roomAlong,0.0)*.10;
    float roomUpper=exp(-2.0*pow(roomAcross/roomWidth,2.0));
    float roomLower=exp(-2.0*pow((roomAcross+uProjectionShape.z)/(roomWidth*1.12),2.0));
    float roomBand=1.0-(1.0-roomUpper)*(1.0-roomLower*.65);
    float roomReach=smoothstep(0.0,.15,roomAlong)*(1.0-smoothstep(.60,2.30,roomAlong));
    projectedAmount+=uProjected*uProjectedIntensity*uSunStrength*uProjectionEnergy*
      roomBand*roomReach*shape.g*.65*(1.0-exterior)*(1.0-face)*surfaceResponse(normal,normalize(uDirection));
  }
  float shadowAmount=0.0;
  vec3 projectionContribution=mix(vec3(1),vec3(1.0,.92,.80),dusk)*projectedAmount;
  light+=projectionContribution;
  // +Z points toward the viewer: the lamp is behind the figure, not a camera-side
  // fill. Keep a small wrapped response for soft reflected visibility. The desk
  // pool compensates for its upward-facing receiving plane, not the front torso.
  vec3 lampDirection=normalize(vec3((vec2(.797,.327)-uv)*vec2(1200.0/675.0,1.0),spatial?-.08:.28));
  float lampMaterial=1.0+hair*(uHair-1.0)+body*(uCloth-1.0);
  // Emission is separate: the luminous shade underside is never N.L shaded.
  vec3 lampReflection=vec3(0);
  LampFields fields=LampFields(0.0,0.0,0.0);
  if(spatial) {
    fields=lampFieldsAt(uv,scene,hair,body,face);
    float form=lampFormResponse(dot(normal,lampDirection),clamp(uStylized,0.0,1.0)*(1.0-face));
    // Near-field objects see the wide luminous underside plus local bounce.
    // Desktop and character keep a directional response to the rear source.
    float nearResponse=mix(.45,1.0,form);
    float energy=fields.nearField*1.75*nearResponse+
      fields.desk*2.05*form+fields.character*2.40*form*lampMaterial;
    lampReflection=vec3(1.0,.63,.32)*uLamp*uLampStrength*energy;
  } else {
    // Legacy comparison only: keep its exponential out of the spatial path.
    vec2 legacyDelta=(uv-vec2(.795,.51))/vec2(.24,.34);
    float pool=exp(-dot(legacyDelta,legacyDelta));
    if(refined && uHasSceneMask) pool*=(1.0-exterior)*mix(.7,1.0,scene.g);
    float response=mix(surfaceResponse(normal,lampDirection),
      surfaceResponse(vec3(0,0,1),lampDirection),face*uFace*.8);
    lampReflection=vec3(1.0,.63,.32)*uLamp*uLampStrength*pool*.66*response*lampMaterial;
  }
  vec3 lampEmission=vec3(1.0,.63,.32)*uLamp*uLampStrength*lampBulb*mix(.5,1.5,night);
  vec3 lampContribution=lampReflection+lampEmission;
  vec3 ambientContribution=uAmbient*uAmbientStrength;
  light+=lampContribution;
  if(spatial) {
    LightLayers layers=roomLightLayers(normal,scene,shape,face,hair,body,night,
      receiver,projectedBand*projectedReach,receive,directional,projectionContribution,
      lampReflection,lampEmission);
    ambientContribution=layers.ambient;
    directional=layers.window;
    projectionContribution=layers.projection;
    lampContribution=layers.lamp+layers.emission;
    light=layers.ambient+layers.window+layers.projection+layers.lamp+layers.emission;
    shadowAmount=layers.occlusion;
  }
  // Preserve expression and avoid chromatic/plastic shading on the face.
  vec3 safeLight=max(light,vec3(.60,.51,.46));
  if(refined) {
    // Neutralize only part of the face tint; preserve local shading and eye linework.
    float readable = max(dot(light,vec3(.2126,.7152,.0722)),mix(.43,.18,night)*uAmbientStrength);
    safeLight = mix(light,vec3(readable)*vec3(1.04,1.0,.98),.65);
  }
  light=mix(light,safeLight,face*uFace);
  light=mix(light,min(light,vec3(1.15)),hair*.5);
  if(refined) {
    // Region-specific suppression of the source illustration's baked daytime highlights.
    // This cannot reconstruct hidden shadow detail or remove shadows from the artwork.
    light=mix(light,vec3(.10,.16,.27)*uAmbientStrength,exterior*night);
    float highlight = smoothstep(.45,.95,dot(base,vec3(.2126,.7152,.0722)));
    light *= 1.0 - night*.15*highlight*(1.0-exterior)*(1.0-face);
  }
  if(uView==2) { color=vec4(normal*.5+.5,1); return; }
  if(uView==3) { color=vec4(face,hair,body,1); return; }
  if(uView==4) { color=vec4(encode(light*.6),1); return; }
  if(uView==5) { color=vec4(scene,1); return; }
  if(uView==6) {
    vec3 tint = vec3(face,hair,body) + vec3(.1,.7,1)*exterior + vec3(1,.6,.1)*scene.g;
    float coverage = clamp(face+hair+body+exterior+scene.g,0.0,1.0);
    color=vec4(mix(base,tint,.42*coverage),1); return;
  }
  if(uView==9) {
    float value=dot(light,vec3(.2126,.7152,.0722));
    // Fixed scale across all times, so daylight coefficients above 1 remain
    // distinguishable. No per-frame normalization that hides energy changes.
    color=vec4(vec3(value*.6),1); return;
  }
  if(uView==10) {
    color=vec4(vec3(lightLuminance(projectionContribution)),1); return;
  }
  if(uView==12) { color=vec4(vec3(shadowAmount),1); return; }
  if(uView==13) { color=vec4(lampContribution,1); return; }
  if(uView==17) { color=vec4(encode(ambientContribution*.6),1); return; }
  if(uView==18) {
    float form=mix(softFormBand(dot(normal,normalize(uDirection)),uSoftness),
      smoothstep(-.40,.40,dot(normal,lampDirection)),night);
    color=vec4(vec3(form),1); return;
  }
  if(uView==19) { color=vec4(vec3(shape.b),1); return; }
  // R near field, G desk, B character; emitter white. Raw receiving fields.
  if(uView==20) { color=vec4(vec3(fields.nearField,fields.desk,fields.character)+vec3(lampBulb),1); return; }
  if(uView==14) { color=vec4(vec3(dot(directional,vec3(.2126,.7152,.0722))*.6),1); return; }
  // Optional scalar log-gain, applied to the original base in linear light.
  // 128 is exactly neutral. Original Base debug always bypasses this experiment.
  float correctionEV=uHasCorrection ? (texture(uCorrectionMap,uv).r*255.0-128.0)/254.0 : 0.0;
  vec3 correctedBase=linearize(base)*exp2(correctionEV*uCorrection);
  if(uView==15) { color=vec4(vec3(.5+correctionEV),1); return; }
  if(uView==16) {
    // Preserve an exact source display at neutral gain (including protected
    // face/hand pixels); avoid a needless sRGB round-trip in this diagnostic.
    color=vec4(correctionEV*uCorrection==0.0 ? base : encode(correctedBase),1); return;
  }
  vec3 lit=correctedBase*light*exp2(uExposure);
  if(uView==0 && uSteam > 0.5) {
    vec2 p = uv - vec2(.825,.635);
    float wave = sin(p.y*34.0 + uMotionTime*.55) * .010;
    float strand = exp(-pow((p.x-wave)/.012, 2.0)) * smoothstep(.10,-.02,p.y) * smoothstep(.0,.07,p.y);
    float strand2 = exp(-pow((p.x+.035+sin(p.y*29.0+uMotionTime*.42)*.008)/.010, 2.0)) * smoothstep(.11,.01,p.y) * smoothstep(.0,.08,p.y);
    lit += vec3(.82,.84,.82) * (strand*.055 + strand2*.035);
  }
  // Extract current relit highlights, suppress skin and broad white clothing.
  float protection=(1.0-face)*(1.0-body*.98);
  float eligibility=protection*clamp(exterior*.35+hair*.25+scene.g*.12+lampBulb,0.0,1.0);
  if(uView==7) {
    float luminance=dot(lit,vec3(.2126,.7152,.0722));
    float excess=max(luminance-uBloomThreshold,0.0)/max(luminance,.0001);
    color=vec4(clamp(lit*excess*eligibility*uBloomMood,0.0,1.0),1); return;
  }
  vec3 glow=texture(uBloomMap,vec2(uv.x,1.0-uv.y)).rgb*protection;
  if(uView==8) { color=vec4(encode(glow),1); return; }
  lit+=glow*uBloom;
  // Gentle highlight shoulder, identity below 0.8 (no filmic contrast crush).
  lit=mix(lit,.8+(1.0-exp(-(lit-.8)*5.0))*.2,step(vec3(.8),lit));
  color=vec4(encode(lit),1);
}`;
