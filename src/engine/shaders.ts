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
uniform sampler2D uBloomMap;
uniform float uBloom, uBloomThreshold, uBloomMood;
uniform bool uHasNormal, uHasMask, uHasSceneMask;
uniform vec3 uAmbient, uSun, uDirection;
uniform float uLamp, uExposure, uAmbientStrength, uSunStrength, uLampStrength, uNormalStrength, uFace;
uniform float uHair, uCloth, uNight, uNightStrength, uRefinement, uStylized, uSoftness, uMotionTime, uSteam;
uniform int uView;
float region(vec2 p, vec2 center, vec2 radius) {
  return 1.0-smoothstep(0.60,1.0,length((p-center)/radius));
}
vec3 linearize(vec3 c) { return mix(c/12.92, pow((c+0.055)/1.055,vec3(2.4)),step(vec3(0.04045),c)); }
vec3 encode(vec3 c) { return mix(c*12.92,1.055*pow(max(c,0.0),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),c)); }
void main() {
  vec3 base = texture(uBase,uv).rgb;
  if(uView==1) { color=vec4(base,1); return; }
  bool refined = uRefinement > .5;
  vec3 scene = uHasSceneMask && refined ? texture(uSceneMask,uv).rgb : vec3(0);
  // Keep the hand-authored window contour crisp enough that its feather does
  // not carry the exterior night treatment across the lower window frame.
  // The authored window mask is feathered for compositing, but its lower
  // edge must stop at the sill instead of tinting the desk below the frame.
  float windowEdge = 1.0 - smoothstep(.555,.585,uv.y);
  float exterior = smoothstep(.72,.96,scene.r) * windowEdge;
  float night = refined ? uNight*uNightStrength : 0.0;
  // All positions use the original artwork's top-left UV coordinates.
  float face = region(uv,vec2(.608,.292),vec2(.074,.107));
  float body = region(uv,vec2(.551,.585),vec2(.195,.24));
  float hair = region(uv,vec2(.605,.37),vec2(.185,.36))*(1.0-face)*(1.0-body);
  if(uHasMask && refined) { vec3 masks=texture(uMask,uv).rgb; face=masks.r; hair=masks.g; body=masks.b; }
  vec2 f=(uv-vec2(.608,.292))/vec2(.074,.107);
  vec2 h=(uv-vec2(.605,.37))/vec2(.185,.36);
  vec3 normal=normalize(vec3(f*.20*face+h*.22*hair,1.0));
  // Table and window have distinct, broad orientation responses.
  float table=smoothstep(.70,.85,uv.y)*smoothstep(.39,.58,uv.x);
  normal=normalize(mix(normal,vec3(0.0,-.50,.866),table));
  if(uHasNormal && refined) normal=normalize(texture(uNormal,uv).rgb*2.0-1.0);
  normal=normalize(mix(vec3(0,0,1),normal,uNormalStrength));
  float diffuse=.35+.65*max(dot(normal,normalize(uDirection)),0.0);
  float broad=smoothstep(.38-uSoftness,.62+uSoftness,dot(normal,normalize(uDirection)));
  diffuse=mix(diffuse,mix(.48,1.0,broad),uStylized);
  float window=smoothstep(.43,.94,uv.x);
  float receive=mix(.36,1.0,window);
  if(refined) receive *= 1.0 + hair*(uHair-1.0) + body*(uCloth-1.0);
  vec3 light=uAmbient*uAmbientStrength+uSun*uSunStrength*diffuse*receive;
  float lampPool=exp(-dot((uv-vec2(.795,.51))/vec2(.24,.34),(uv-vec2(.795,.51))/vec2(.24,.34))*1.0);
  float lampBulb=region(uv,vec2(.80,.32),vec2(.035,.027));
  if(refined && uHasSceneMask) {
    // Window panes receive no indoor lamp spill. Desk has its own receiving area.
    lampPool *= (1.0-exterior) * mix(.7,1.0,scene.g);
    lampBulb = scene.b;
  }
  light+=vec3(1.0,.66,.36)*uLamp*uLampStrength*(lampPool*.66+lampBulb*.5);
  // Preserve expression and avoid chromatic/plastic shading on the face.
  vec3 safeLight=max(light,vec3(.60,.51,.46));
  if(refined) {
    // Neutralize only part of the face tint; preserve local shading and eye linework.
    float readable = max(dot(light,vec3(.2126,.7152,.0722)),.43*uAmbientStrength);
    safeLight = mix(light,vec3(readable)*vec3(1.04,1.0,.98),.65);
  }
  light=mix(light,safeLight,face*uFace);
  light=mix(light,min(light,vec3(1.15)),hair*.5);
  if(refined) {
    // Region-specific suppression of the source illustration's baked daytime highlights.
    // This cannot reconstruct hidden shadow detail or remove shadows from the artwork.
    light *= mix(vec3(1),vec3(.14,.20,.31),exterior*night);
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
    color=vec4(vec3(value),1); return;
  }
  vec3 lit=linearize(base)*light*exp2(uExposure);
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
