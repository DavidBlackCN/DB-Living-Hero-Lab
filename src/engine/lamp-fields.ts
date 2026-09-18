// All fields are registered to the original image (top-left UV). These are
// receiving planes, not depth reconstruction or shifted cast silhouettes.
export const lampFields = `
struct LampFields { float nearField; float desk; float character; };
// Compact C1 falloff: no exponential tail illuminating the whole tabletop.
float boundedField(vec2 p, vec2 center, vec2 extent) {
  vec2 d=(p-center)/extent;
  float f=max(1.0-dot(d,d),0.0);
  return f*f;
}
LampFields lampFieldsAt(vec2 p, vec3 scene, float hair, float body, float face) {
  LampFields fields;
  float indoor=1.0-scene.r;
  float subject=clamp(hair+body+face,0.0,1.0);
  // Under-shade cone reaches tools, frame and physical sill. A faint continuous
  // backdrop response includes the pole/apron without treating them as glass.
  float belowShade=smoothstep(.322,.355,p.y);
  fields.nearField=boundedField(p,vec2(.811,.445),vec2(.165,.240))*
    belowShade*(.22+.78*scene.g)*(1.0-subject)*indoor;
  // Right page/cup/coaster core; distant left page and front lip lose the tail.
  float receiver=max(scene.g,max(hair*.85,body*.90));
  fields.desk=boundedField(p,vec2(.814,.751),vec2(.235,.170))*receiver*indoor;
  // Registered shoulder/hair field: continuous over sleeves and hands, while
  // the front torso shields itself. Never use face readability as lamp energy.
  float rear=smoothstep(.625,.735,p.x)*(1.0-face);
  fields.character=boundedField(p,vec2(.747,.515),vec2(.135,.285))*
    (hair*.75+body*.85)*rear*indoor;
  return fields;
}
float lampFormResponse(float facing, float style) {
  float wrapped=.08+.92*clamp((facing+.70)/1.70,0.0,1.0);
  return mix(wrapped,mix(.10,.90,smoothstep(-.40,.40,facing)),style*.70);
}
`;
