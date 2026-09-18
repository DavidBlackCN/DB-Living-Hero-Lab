import { wrapTime } from './timeline';
// Linear-light RGB coefficients; wrap the final key back to midnight.
const keys = [
  { time: 0, ambient: [0.18, 0.20, 0.24], sun: [0, 0, 0], lamp: 0.72 },
  { time: 300, ambient: [0.33, 0.39, 0.51], sun: [0.09, 0.13, 0.19], lamp: 0.50 },
  { time: 360, ambient: [0.46, 0.54, 0.65], sun: [0.46, 0.49, 0.53], lamp: 0.12 },
  { time: 540, ambient: [0.75, 0.77, 0.79], sun: [0.35, 0.34, 0.31], lamp: 0.02 },
  { time: 720, ambient: [0.80, 0.81, 0.82], sun: [0.32, 0.31, 0.29], lamp: 0.0 },
  { time: 930, ambient: [0.76, 0.72, 0.66], sun: [0.40, 0.30, 0.20], lamp: 0.04 },
  { time: 1050, ambient: [0.53, 0.48, 0.45], sun: [0.63, 0.39, 0.23], lamp: 0.20 },
  { time: 1140, ambient: [0.34, 0.36, 0.48], sun: [0.12, 0.10, 0.15], lamp: 0.58 },
  { time: 1380, ambient: [0.18, 0.20, 0.24], sun: [0, 0, 0], lamp: 0.72 },
  { time: 1440, ambient: [0.18, 0.20, 0.24], sun: [0, 0, 0], lamp: 0.72 },
];
// Art-directed darkness, independent of lamp strength and user exposure.
const nightWeights = [1, 0.8, 0.1, 0, 0, 0, 0.18, 0.85, 1, 1];
const directions = [
  [0.54, -0.62, 0.56], [0.58, -0.52, 0.62], [0.90, -0.28, 0.48],
  [0.38, -0.82, 0.66], [-0.04, -0.98, 0.76], [0.34, -0.82, 0.70],
  [0.82, -0.34, 0.46], [0.86, -0.12, 0.36], [0.70, -0.38, 0.48], [0.54, -0.62, 0.56],
];
export function lightingAt(minutes: number) {
  const t = wrapTime(minutes);
  const i = keys.findIndex((key, index) => index < keys.length - 1 && t >= key.time && t < keys[index + 1].time);
  const a = keys[i], b = keys[i + 1];
  const x = (t - a.time) / (b.time - a.time), f = x * x * (3 - 2 * x);
  const mix = (u: number, v: number) => u + (v - u) * f;
  const direction = directions[i].map((v, j) => mix(v, directions[i + 1][j]));
  return {
    ambient: a.ambient.map((v, j) => mix(v, b.ambient[j])),
    night: mix(nightWeights[i], nightWeights[i + 1]),
    sun: a.sun.map((v, j) => mix(v, b.sun[j])), lamp: mix(a.lamp, b.lamp),
    // Keep the key light on the actual window side (image right).
    direction,
  };
}

// Art-directed projection in artwork space. Origin stays in the real right-hand
// window; axis uses equal X/Y units (image height), not stretched 16:9 UVs.
// These are lighting keyframes, not additional user-facing tuning parameters.
const projectionKeys = [
  { time: 0, origin: [.90,.22], axis: [-.70,.714], width: .09, spread: .035, separation: .22, reach: 1.14, energy: 0 },
  // Morning enters higher in the window and crosses the shoulder/book at a
  // shallower angle. Preserve energy and converge to the accepted noon key.
  { time: 330, origin: [.93,.14], axis: [-.83,.558], width: .095, spread: .04, separation: .24, reach: 1.25, energy: 0 },
  { time: 360, origin: [.93,.14], axis: [-.83,.558], width: .095, spread: .04, separation: .24, reach: 1.25, energy: .85 },
  { time: 480, origin: [.91,.14], axis: [-.77,.638], width: .10, spread: .04, separation: .24, reach: 1.19, energy: 1.15 },
  { time: 720, origin: [.90,.18], axis: [-.42,.907], width: .19, spread: .035, separation: .24, reach: 1.05, energy: .95 },
  { time: 1050, origin: [.94,.28], axis: [-.90,.435], width: .105, spread: .08, separation: .27, reach: 1.10, energy: 1.85 },
  { time: 1170, origin: [.96,.32], axis: [-.95,.312], width: .105, spread: .08, separation: .27, reach: 1.15, energy: 0 },
  { time: 1440, origin: [.90,.22], axis: [-.70,.714], width: .09, spread: .035, separation: .22, reach: 1.14, energy: 0 },
];

export function projectedLightAt(minutes: number) {
  const t = wrapTime(minutes);
  const i = projectionKeys.findIndex((key, index) => index < projectionKeys.length-1 && t >= key.time && t < projectionKeys[index+1].time);
  const a = projectionKeys[i], b = projectionKeys[i+1];
  const x = (t-a.time)/(b.time-a.time), f = x*x*(3-2*x);
  const mix = (u: number, v: number) => u + (v-u)*f;
  return {
    origin: a.origin.map((v,j) => mix(v,b.origin[j])),
    axis: a.axis.map((v,j) => mix(v,b.axis[j])),
    width: mix(a.width,b.width), spread: mix(a.spread,b.spread),
    separation: mix(a.separation,b.separation), reach: mix(a.reach,b.reach),
    energy: mix(a.energy,b.energy),
  };
}
