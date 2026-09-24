import type { LightingPresetId, LightingState } from '../engine/types'

export interface LightingPreset {
  id: LightingPresetId
  label: string
  minutes: number
}

export interface LightingModelConfig {
  sunriseMinutes: number
  sunsetMinutes: number
  daylightElevationStart: number
  daylightElevationFull: number
  warmthElevationStart: number
  warmthElevationPeak: number
  warmthElevationEnd: number
  dawnAzimuth: number
  noonAzimuth: number
  duskAzimuth: number
  nightElevationDegrees: number
  dayElevationDegrees: number
  nightExposureStops: number
  dawnExposureStops: number
  dayExposureStops: number
  duskExposureStops: number
  nightKeyIntensity: number
  dayKeyIntensity: number
  twilightKeyBoost: number
  nightAmbientIntensity: number
  dayAmbientIntensity: number
  twilightAmbientBoost: number
  nightColor: { key: [number, number, number]; ambient: [number, number, number] }
  dayColor: { key: [number, number, number]; ambient: [number, number, number] }
  dawnColor: { key: [number, number, number]; ambient: [number, number, number] }
  duskColor: { key: [number, number, number]; ambient: [number, number, number] }
  diffuseWrap: number
  diffuseThreshold: number
  diffuseSoftness: number
  bandStrength: number
  bandThreshold: number
  bandSoftness: number
  relightStrength: number
}

export const lightingModelConfig: LightingModelConfig = {
  sunriseMinutes: 360,
  sunsetMinutes: 1080,
  daylightElevationStart: -0.12,
  daylightElevationFull: 0.98,
  warmthElevationStart: -0.10,
  warmthElevationPeak: 0.30,
  warmthElevationEnd: 0.78,
  dawnAzimuth: 35,
  noonAzimuth: 90,
  duskAzimuth: 145,
  nightElevationDegrees: 18,
  dayElevationDegrees: 64,
  dawnExposureStops: 0.20,
  dayExposureStops: -0.34,
  duskExposureStops: 0.06,
  nightExposureStops: 0.18,
  nightKeyIntensity: 0.28,
  dayKeyIntensity: 0.82,
  twilightKeyBoost: 0.58,
  nightAmbientIntensity: 0.19,
  dayAmbientIntensity: 0.50,
  twilightAmbientBoost: 0.30,
  nightColor: { key: [0.60, 0.73, 1], ambient: [0.28, 0.34, 0.58] },
  dayColor: { key: [1, 0.98, 0.94], ambient: [0.60, 0.70, 0.88] },
  dawnColor: { key: [1, 0.80, 0.66], ambient: [0.50, 0.61, 0.80] },
  duskColor: { key: [1, 0.48, 0.24], ambient: [0.38, 0.52, 0.82] },
  diffuseWrap: 0.08,
  diffuseThreshold: 0.52,
  diffuseSoftness: 0.24,
  bandStrength: 0.34,
  bandThreshold: 0.66,
  bandSoftness: 0.32,
  relightStrength: 0.90,
}

export const lightingPresets: Record<LightingPresetId, LightingPreset> = {
  dawn: { id: 'dawn', label: 'Dawn', minutes: 390 },
  noon: { id: 'noon', label: 'Noon', minutes: 720 },
  dusk: { id: 'dusk', label: 'Dusk', minutes: 1050 },
  night: { id: 'night', label: 'Night', minutes: 1320 },
}

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value))

function smooth(a: number, b: number, value: number): number {
  const t = clamp01((value - a) / (b - a))
  return t * t * (3 - 2 * t)
}

function mix(a: number, b: number, amount: number): number {
  return a + (b - a) * amount
}

function mixColor(a: readonly number[], b: readonly number[], amount: number): [number, number, number] {
  return [mix(a[0], b[0], amount), mix(a[1], b[1], amount), mix(a[2], b[2], amount)]
}

function colorChannels(values: [number, number, number]): LightingState['color'] {
  return { r: values[0], g: values[1], b: values[2] }
}

export function lightingFor(minutes: number): LightingState & { daylight: number; warmth: number } {
  const inputMinutes = Number.isFinite(minutes) ? Math.max(0, Math.min(1440, minutes)) : 720
  const safeMinutes = inputMinutes === 1440 ? 0 : inputMinutes
  const hourAngle = ((safeMinutes - lightingModelConfig.sunriseMinutes) / 1440) * Math.PI * 2
  const solarElevation = Math.sin(hourAngle)
  const daylight = smooth(lightingModelConfig.daylightElevationStart, lightingModelConfig.daylightElevationFull, solarElevation)
  const warmth = (1 - smooth(lightingModelConfig.warmthElevationPeak, lightingModelConfig.warmthElevationEnd, solarElevation))
    * smooth(lightingModelConfig.warmthElevationStart, lightingModelConfig.warmthElevationPeak, solarElevation)
  const nextSunrise = lightingModelConfig.sunriseMinutes + 1440
  const afterSunset = safeMinutes < lightingModelConfig.sunriseMinutes
    ? safeMinutes + 1440
    : safeMinutes
  const isDaylightArc = safeMinutes >= lightingModelConfig.sunriseMinutes && safeMinutes <= lightingModelConfig.sunsetMinutes
  const noonMinutes = (lightingModelConfig.sunriseMinutes + lightingModelConfig.sunsetMinutes) / 2
  const azimuth = isDaylightArc
    ? safeMinutes <= noonMinutes
      ? mix(lightingModelConfig.dawnAzimuth, lightingModelConfig.noonAzimuth, smooth(lightingModelConfig.sunriseMinutes, noonMinutes, safeMinutes))
      : mix(lightingModelConfig.noonAzimuth, lightingModelConfig.duskAzimuth, smooth(noonMinutes, lightingModelConfig.sunsetMinutes, safeMinutes))
    : mix(lightingModelConfig.duskAzimuth, lightingModelConfig.dawnAzimuth, smooth(lightingModelConfig.sunsetMinutes, nextSunrise, afterSunset))
  const duskSide = isDaylightArc
    ? smooth(lightingModelConfig.sunriseMinutes + 540, lightingModelConfig.sunsetMinutes, safeMinutes)
    : 1 - smooth(lightingModelConfig.sunsetMinutes, nextSunrise, afterSunset)
  const elevationDegrees = mix(lightingModelConfig.nightElevationDegrees, lightingModelConfig.dayElevationDegrees, daylight)
  const azimuthRadians = azimuth * Math.PI / 180
  const elevationRadians = elevationDegrees * Math.PI / 180
  const direction = {
    x: Math.cos(azimuthRadians) * Math.cos(elevationRadians),
    y: Math.sin(azimuthRadians) * Math.cos(elevationRadians),
    z: Math.sin(elevationRadians),
  }
  const dawnWeight = warmth * (1 - duskSide)
  const duskWeight = warmth * duskSide
  const keyColor = mixColor(
    mixColor(lightingModelConfig.nightColor.key, lightingModelConfig.dayColor.key, daylight),
    mixColor(lightingModelConfig.dawnColor.key, lightingModelConfig.duskColor.key, duskSide),
    warmth,
  )
  const ambientColor = mixColor(
    mixColor(lightingModelConfig.nightColor.ambient, lightingModelConfig.dayColor.ambient, daylight),
    mixColor(lightingModelConfig.dawnColor.ambient, lightingModelConfig.duskColor.ambient, duskSide),
    warmth,
  )
  const exposureStops = mix(
    mix(mix(lightingModelConfig.nightExposureStops, lightingModelConfig.dawnExposureStops, dawnWeight), lightingModelConfig.duskExposureStops, duskWeight),
    lightingModelConfig.dayExposureStops,
    daylight,
  )
  const twilightEnergy = warmth * (1 - daylight)

  return {
    enabled: true,
    exposureStops,
    relightStrength: lightingModelConfig.relightStrength,
    direction,
    intensity: mix(lightingModelConfig.nightKeyIntensity, lightingModelConfig.dayKeyIntensity, daylight)
      + dawnWeight * lightingModelConfig.twilightKeyBoost + duskWeight * lightingModelConfig.twilightKeyBoost,
    color: colorChannels(keyColor),
    ambientIntensity: mix(lightingModelConfig.nightAmbientIntensity, lightingModelConfig.dayAmbientIntensity, daylight)
      + twilightEnergy * lightingModelConfig.twilightAmbientBoost,
    ambientColor: colorChannels(ambientColor),
    diffuseWrap: lightingModelConfig.diffuseWrap,
    diffuseThreshold: lightingModelConfig.diffuseThreshold,
    diffuseSoftness: lightingModelConfig.diffuseSoftness,
    bandStrength: mix(
      mix(lightingModelConfig.bandStrength * 0.55, lightingModelConfig.bandStrength, daylight),
      lightingModelConfig.bandStrength * 1.12,
      warmth,
    ),
    bandThreshold: lightingModelConfig.bandThreshold,
    bandSoftness: lightingModelConfig.bandSoftness,
    daylight,
    warmth,
  }
}

export function createLightingStateForTime(minutes: number): LightingState {
  const { daylight: _daylight, warmth: _warmth, ...state } = lightingFor(minutes)
  return state
}

export function createLightingState(preset: LightingPresetId): LightingState {
  return createLightingStateForTime(lightingPresets[preset].minutes)
}

export const defaultLighting: LightingState = createLightingState('noon')

export function formatLightingTime(minutes: number): string {
  const value = Math.floor(Math.max(0, Math.min(1440, Number.isFinite(minutes) ? minutes : 720)))
  if (value === 1440) return '24:00'
  return `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(value % 60).padStart(2, '0')}`
}
