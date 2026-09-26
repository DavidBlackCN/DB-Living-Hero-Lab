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
  dawnKeyBoost: number
  duskKeyBoost: number
  nightAmbientIntensity: number
  deepNightAmbientLift: number
  deepNightKeyReduction: number
  dayAmbientIntensity: number
  dawnAmbientBoost: number
  duskAmbientBoost: number
  nightColor: { key: [number, number, number]; ambient: [number, number, number] }
  deepNightAmbientColor: [number, number, number]
  dayColor: { key: [number, number, number]; ambient: [number, number, number] }
  dawnColor: { key: [number, number, number]; ambient: [number, number, number] }
  duskColor: { key: [number, number, number]; ambient: [number, number, number] }
  diffuseWrap: number
  diffuseThreshold: number
  diffuseSoftness: number
  bandStrength: number
  bandThreshold: number
  bandSoftness: number
  duskUpperSceneAttenuation: number
  nightUpperSceneAttenuation: number
  nightRelightStrength: number
  dayRelightStrength: number
  duskRelightBoost: number
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
  dawnExposureStops: 0.29,
  dayExposureStops: -0.42,
  duskExposureStops: 0.16,
  nightExposureStops: -0.22,
  nightKeyIntensity: 0.20,
  dayKeyIntensity: 0.64,
  dawnKeyBoost: 0.44,
  duskKeyBoost: 1.28,
  nightAmbientIntensity: 0.14,
  deepNightAmbientLift: 0.025,
  deepNightKeyReduction: 0.025,
  dayAmbientIntensity: 0.38,
  dawnAmbientBoost: 0.39,
  duskAmbientBoost: 0.34,
  nightColor: { key: [0.56, 0.70, 1], ambient: [0.28, 0.36, 0.62] },
  deepNightAmbientColor: [0.36, 0.47, 0.72],
  dayColor: { key: [1, 0.98, 0.94], ambient: [0.60, 0.70, 0.88] },
  dawnColor: { key: [0.92, 0.92, 0.93], ambient: [0.28, 0.46, 0.78] },
  duskColor: { key: [1, 0.59, 0.22], ambient: [0.60, 0.43, 0.48] },
  diffuseWrap: 0.08,
  diffuseThreshold: 0.52,
  diffuseSoftness: 0.24,
  bandStrength: 0.30,
  bandThreshold: 0.66,
  bandSoftness: 0.32,
  duskUpperSceneAttenuation: 0,
  nightUpperSceneAttenuation: 0,
  nightRelightStrength: 0.97,
  dayRelightStrength: 0.95,
  duskRelightBoost: 0.03,
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

function solarLightingFor(minutes: number): LightingState & { daylight: number; warmth: number } {
  const inputMinutes = Number.isFinite(minutes) ? Math.max(0, Math.min(1440, minutes)) : 720
  const safeMinutes = inputMinutes === 1440 ? 0 : inputMinutes
  const hourAngle = ((safeMinutes - lightingModelConfig.sunriseMinutes) / 1440) * Math.PI * 2
  const solarElevation = Math.sin(hourAngle)
  // Deep-night fill fades before twilight, leaving the accepted Noon/Dusk looks intact.
  const deepNight = 1 - smooth(-0.28, -0.10, solarElevation)
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
  const twilightColorWeight = Math.min(1, warmth * 1.5)
  const keyColor = mixColor(
    mixColor(lightingModelConfig.nightColor.key, lightingModelConfig.dayColor.key, daylight),
    mixColor(lightingModelConfig.dawnColor.key, lightingModelConfig.duskColor.key, duskSide),
    twilightColorWeight,
  )
  const ambientColor = mixColor(mixColor(
    mixColor(lightingModelConfig.nightColor.ambient, lightingModelConfig.dayColor.ambient, daylight),
    mixColor(lightingModelConfig.dawnColor.ambient, lightingModelConfig.duskColor.ambient, duskSide),
    twilightColorWeight,
  ), lightingModelConfig.deepNightAmbientColor, deepNight)
  const exposureStops = mix(
    mix(mix(lightingModelConfig.nightExposureStops, lightingModelConfig.dawnExposureStops, dawnWeight), lightingModelConfig.duskExposureStops, duskWeight),
    lightingModelConfig.dayExposureStops,
    daylight,
  )
  return {
    enabled: true,
    exposureStops,
    relightStrength: Math.min(1, mix(lightingModelConfig.nightRelightStrength, lightingModelConfig.dayRelightStrength, daylight)
      + duskWeight * lightingModelConfig.duskRelightBoost),
    direction,
    intensity: mix(lightingModelConfig.nightKeyIntensity, lightingModelConfig.dayKeyIntensity, daylight)
      + dawnWeight * lightingModelConfig.dawnKeyBoost + duskWeight * lightingModelConfig.duskKeyBoost
      - deepNight * lightingModelConfig.deepNightKeyReduction,
    color: colorChannels(keyColor),
    ambientIntensity: mix(lightingModelConfig.nightAmbientIntensity, lightingModelConfig.dayAmbientIntensity, daylight)
      + dawnWeight * lightingModelConfig.dawnAmbientBoost + duskWeight * lightingModelConfig.duskAmbientBoost
      + deepNight * lightingModelConfig.deepNightAmbientLift,
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
    upperSceneAttenuation: duskWeight * lightingModelConfig.duskUpperSceneAttenuation
      + (safeMinutes < lightingModelConfig.sunriseMinutes
        ? (1 - smooth(0, lightingModelConfig.sunriseMinutes, safeMinutes))
        : safeMinutes > lightingModelConfig.sunsetMinutes
          ? smooth(lightingModelConfig.sunsetMinutes, nextSunrise, safeMinutes)
          : 0) * lightingModelConfig.nightUpperSceneAttenuation,
    skyEnabled: true,
    daylight,
    warmth,
  }
}

const dawnEnergy = solarLightingFor(lightingPresets.dawn.minutes)
const morningEndEnergy = solarLightingFor(600)
const afternoonStartEnergy = solarLightingFor(900)
const duskEnergy = solarLightingFor(lightingPresets.dusk.minutes)
const nightHoldEnergy = solarLightingFor(1200)

export function lightingFor(minutes: number): LightingState & { daylight: number; warmth: number } {
  const state = solarLightingFor(minutes)
  const time = Math.max(0, Math.min(1440, Number.isFinite(minutes) ? minutes : 720))

  // The Night sky and Moon key begin fading at 05:00, before the solar key
  // becomes useful. A small, eased cool fill bridges that short overlap so
  // early twilight does not dip below the late-night hold. It vanishes by
  // the accepted 06:30 Dawn anchor and leaves all other phases untouched.
  const predawnFill = smooth(300, 330, time) * (1 - smooth(330, 390, time))
  state.ambientIntensity += predawnFill * 0.025

  // Solar direction, colors and sky keep their continuous curves. Balance only
  // light energy through the morning peak, afternoon peak, and dusk-to-night dip.
  const endpoints = time > 390 && time < 600
    ? { first: dawnEnergy, second: morningEndEnergy, amount: smooth(390, 600, time) }
    : time > 900 && time < 1050
      ? { first: afternoonStartEnergy, second: duskEnergy, amount: smooth(900, 1050, time) }
      : time > 1050 && time < 1200
        ? { first: duskEnergy, second: nightHoldEnergy, amount: smooth(1050, 1200, time) }
      : null
  if (endpoints) {
    state.exposureStops = mix(endpoints.first.exposureStops, endpoints.second.exposureStops, endpoints.amount)
    state.intensity = mix(endpoints.first.intensity, endpoints.second.intensity, endpoints.amount)
    state.ambientIntensity = mix(endpoints.first.ambientIntensity, endpoints.second.ambientIntensity, endpoints.amount)
  }
  return state
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
