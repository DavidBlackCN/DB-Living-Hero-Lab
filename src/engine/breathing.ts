/** Driven only by renderer ticks; pausing never consumes hidden wall-clock time. */
export class BreathingClock {
  phase = 0;
  private previous: number | null = null;
  update(now: number, cycleSeconds: number) {
    if (this.previous !== null) {
      this.phase = (this.phase + Math.max(0, now - this.previous) / (cycleSeconds * 1000)) % 1;
    }
    this.previous = now;
  }
  pause() { this.previous = null; }
  reset() { this.phase = 0; this.pause(); }
  get amount() { return (1 - Math.cos(this.phase * Math.PI * 2)) * .5; }
}

// Bounds are registered in the existing 1200 x 675 artwork reference space.
export const breathingShader = `
uniform vec2 uArtworkSize;
uniform float uBreathingAmount;
float breathingCloth(vec2 p) {
  vec3 m=texture(uMask,p).rgb;
  float hand=min(m.r,min(m.g,m.b));
  return smoothstep(.94,.995,max(m.b-hand,0.0))*(1.0-smoothstep(0.0,.02,max(m.r,m.g)));
}
float breathingWeight(vec2 p) {
  if(!uHasMask || uRefinement<=.5) return 0.0;
  vec2 at=p*vec2(1200.0,675.0);
  vec2 q=(at-vec2(681.0,380.0))/vec2(72.0,60.0);
  float r2=dot(q,q);
  if(r2>=1.0) return 0.0;
  // Inset semantic support by 10 source pixels, beyond the 2 px travel cap.
  vec2 inset=vec2(10.0)/uArtworkSize;
  float cloth=min(breathingCloth(p),min(min(breathingCloth(p+vec2(inset.x,0)),
    breathingCloth(p-vec2(inset.x,0))),min(breathingCloth(p+vec2(0,inset.y)),
    breathingCloth(p-vec2(0,inset.y)))));
  // The coarse cloth mask paints over a dangling front lock. Stay right of it.
  return (1.0-r2)*(1.0-r2)*cloth*smoothstep(645.0,662.0,at.x);
}
`;
