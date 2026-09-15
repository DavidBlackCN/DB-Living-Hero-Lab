// Keep each review run separate from checked-in historical/user captures.
export const visualRoot = process.env.VISUAL_OUTPUT_ROOT ?? 'docs/screenshots';
export const performanceRoot = process.env.VISUAL_OUTPUT_ROOT
  ? `${process.env.VISUAL_OUTPUT_ROOT}/performance` : 'docs/performance';
