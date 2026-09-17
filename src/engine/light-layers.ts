// Logical radiometric layers in the existing scene pass, not extra framebuffers.
// Source artwork is already lit: retain a broad transition and a protected face.
export const lightLayers = `
struct LightLayers {
  vec3 ambient;
  vec3 window;
  vec3 projection;
  vec3 lamp;
  vec3 emission;
  float occlusion;
};
float softFormBand(float facing, float softness) {
  float edge=.10+clamp(softness,0.0,1.0)*.22;
  return smoothstep(.46-edge,.46+edge,facing);
}
float lightLuminance(vec3 v) { return dot(v,vec3(.2126,.7152,.0722)); }

LightLayers roomLightLayers(vec3 normal, vec3 scene, vec3 shape,
    float face, float hair, float body, float night, float receiver,
    float aperture, float receive, vec3 directional, vec3 projection,
    vec3 lampReflection, vec3 emission, vec3 lampDirection) {
  LightLayers result;
  float indoor=1.0-scene.r;
  // The room participates even outside an authored bright receiving patch.
  // G controls subtle room strength, never an alternate light direction.
  float surface=clamp(max(max(hair,body),max(scene.g,shape.g)),0.0,1.0);
  float protection=indoor*(1.0-face);
  float band=softFormBand(dot(normal,normalize(uDirection)),uSoftness);
  float style=clamp(uStylized,0.0,1.0)*protection;
  float skyFacing=clamp(.5-.5*normal.y,0.0,1.0);
  float fillFacing=mix(band,skyFacing,.20);
  // Separate soft sky fill from direct light: dark faces retain cool fill,
  // instead of receiving a constant near-white ambient that erases their form.
  vec3 fillTone=mix(vec3(.60,.67,.78),vec3(.97,.98,1.0),fillFacing);
  float roomEnclosure=shape.g*(1.0-shape.r)*protection;
  float skyVisibility=1.0-roomEnclosure*.24;
  vec3 skyFill=uAmbient*uAmbientStrength*mix(vec3(1),fillTone,style)*skyVisibility;
  // Low-energy reflected window light links distant walls/plants/chair to the
  // same key color. Their sky access is weaker; bounce never becomes a beam.
  vec3 wallBounce=uSun*uSunStrength*roomEnclosure*.10*skyFacing;
  vec3 daylightFill=skyFill+wallBounce;
  float directForm=mix(.12,1.0,band);
  vec3 window=uSun*uSunStrength*receive*directForm;
  window=mix(directional,window,style);

  float day=clamp(uProjectionEnergy,0.0,1.0)*uProjected*
    clamp(uProjectedIntensity/.42,0.0,1.0)*uSunStrength;
  float apertureShade=clamp(day*(receiver*(1.0-aperture)*.30+
    (1.0-shape.r)*.12*protection),0.0,.50);
  // Contact B is registered geometry. Ambient occlusion and each light's
  // visibility have separate budgets; emission is never contact-darkened.
  float contact=shape.b*indoor;
  contact=mix(contact,min(contact,.045),face);
  float ambientOcclusion=clamp(uShadow*(contact*.48+
    surface*(1.0-shape.r)*.13*protection),0.0,.42);
  float directVisibility=1.0-clamp(uShadow*contact*.62,0.0,.42);
  vec3 nightFill=uAmbient*uAmbientStrength*mix(.38,.80,shape.r);
  vec3 skySpill=vec3(.055,.095,.17)*shape.r*(.35+hair*.4+body*.15)*uAmbientStrength;
  // Hemisphere response is shared by all materials, including chair/foreground.
  nightFill*=mix(vec3(1),mix(vec3(.72,.80,.94),vec3(1),skyFacing),style);
  result.ambient=mix(daylightFill*(1.0-apertureShade),nightFill+skySpill,night*indoor);
  result.ambient*=1.0-ambientOcclusion;
  result.window=window*(1.0-night*indoor)*(1.0-apertureShade)*directVisibility;
  result.projection=projection*directVisibility;

  // Wide area lamp response supplies lit / turning / back-facing surfaces.
  // N.L modulates the existing registered pool, so this cannot light the face
  // or create a camera-side fill outside the pool's visibility.
  float lampFacing=dot(normal,lampDirection);
  float lampBand=smoothstep(-.40,.40,lampFacing);
  float wrapped=.08+.92*clamp((lampFacing+.70)/1.70,0.0,1.0);
  float lampForm=mix(wrapped,mix(.10,.90,lampBand),style*.70);
  float formRatio=lampForm/max(wrapped,.001);
  float lampVisibility=1.0-clamp(uShadow*contact*.70,0.0,.46);
  result.lamp=lampReflection*formRatio*lampVisibility;
  result.emission=emission;

  // Energy removed by visibility, independent of surface pigment/exposure.
  // Form shading is inspected separately with the form diagnostic.
  result.occlusion=0.0;
  if(uView==12) {
    vec3 openLight=mix(daylightFill,nightFill+skySpill,night*indoor)+
      window*(1.0-night*indoor)+projection+lampReflection*formRatio;
    vec3 visible=result.ambient+result.window+result.projection+result.lamp;
    float openEnergy=lightLuminance(openLight);
    result.occlusion=openEnergy>.0001 ? clamp(1.0-lightLuminance(visible)/openEnergy,0.0,1.0) : 0.0;
  }
  return result;
}
`;
