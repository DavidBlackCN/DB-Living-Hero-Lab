import vertexSource from '../../shaders/hero.vert.glsl?raw'
import fragmentSource from '../../shaders/hero.frag.glsl?raw'
import type { ArtworkLayout } from '../coordinates/artwork'
import type { LightingState, RenderView } from '../types'

function compile(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader {
  const shader = gl.createShader(type)
  if (!shader) throw new Error('Could not allocate shader')
  gl.shaderSource(shader, source)
  gl.compileShader(shader)
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const message = gl.getShaderInfoLog(shader) || 'Unknown shader error'
    gl.deleteShader(shader)
    throw new Error(message)
  }
  return shader
}

export class BaseRenderer {
  private gl: WebGL2RenderingContext
  private program: WebGLProgram
  private buffer: WebGLBuffer
  private texture: WebGLTexture
  private normalTexture: WebGLTexture
  private rectLocation: WebGLUniformLocation
  private viewLocation: WebGLUniformLocation
  private lightingEnabledLocation: WebGLUniformLocation
  private exposureLocation: WebGLUniformLocation
  private relightStrengthLocation: WebGLUniformLocation
  private lightLocation: WebGLUniformLocation
  private lightIntensityLocation: WebGLUniformLocation
  private lightColorLocation: WebGLUniformLocation
  private ambientIntensityLocation: WebGLUniformLocation
  private ambientColorLocation: WebGLUniformLocation
  private diffuseWrapLocation: WebGLUniformLocation
  private diffuseThresholdLocation: WebGLUniformLocation
  private diffuseSoftnessLocation: WebGLUniformLocation
  private bandStrengthLocation: WebGLUniformLocation
  private bandThresholdLocation: WebGLUniformLocation
  private bandSoftnessLocation: WebGLUniformLocation
  private disposed = false

  constructor(private canvas: HTMLCanvasElement, image: HTMLImageElement, normalImage: HTMLImageElement) {
    const gl = canvas.getContext('webgl2', { alpha: false, antialias: false })
    if (!gl) throw new Error('WebGL2 unavailable')
    this.gl = gl
    const vertex = compile(gl, gl.VERTEX_SHADER, vertexSource)
    const fragment = compile(gl, gl.FRAGMENT_SHADER, fragmentSource)
    const program = gl.createProgram()
    if (!program) throw new Error('Could not allocate program')
    gl.attachShader(program, vertex)
    gl.attachShader(program, fragment)
    gl.linkProgram(program)
    gl.deleteShader(vertex)
    gl.deleteShader(fragment)
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      const message = gl.getProgramInfoLog(program) || 'Unknown link error'
      gl.deleteProgram(program)
      throw new Error(message)
    }
    this.program = program
    const buffer = gl.createBuffer()
    const texture = gl.createTexture()
    const normalTexture = gl.createTexture()
    const rectLocation = gl.getUniformLocation(program, 'u_rect')
    const viewLocation = gl.getUniformLocation(program, 'u_view')
    const locations = {
      light: gl.getUniformLocation(program, 'u_lightDirection'),
      lightingEnabled: gl.getUniformLocation(program, 'u_lightingEnabled'),
      exposure: gl.getUniformLocation(program, 'u_exposure'),
      relightStrength: gl.getUniformLocation(program, 'u_relightStrength'),
      lightIntensity: gl.getUniformLocation(program, 'u_lightIntensity'),
      lightColor: gl.getUniformLocation(program, 'u_lightColor'),
      ambientIntensity: gl.getUniformLocation(program, 'u_ambientIntensity'),
      ambientColor: gl.getUniformLocation(program, 'u_ambientColor'),
      diffuseWrap: gl.getUniformLocation(program, 'u_diffuseWrap'),
      diffuseThreshold: gl.getUniformLocation(program, 'u_diffuseThreshold'),
      diffuseSoftness: gl.getUniformLocation(program, 'u_diffuseSoftness'),
      bandStrength: gl.getUniformLocation(program, 'u_bandStrength'),
      bandThreshold: gl.getUniformLocation(program, 'u_bandThreshold'),
      bandSoftness: gl.getUniformLocation(program, 'u_bandSoftness'),
    }
    if (!buffer || !texture || !normalTexture || !rectLocation || !viewLocation || Object.values(locations).some(location => !location)) throw new Error('Could not allocate WebGL resources')
    this.buffer = buffer
    this.texture = texture
    this.normalTexture = normalTexture
    this.rectLocation = rectLocation
    this.viewLocation = viewLocation
    this.lightingEnabledLocation = locations.lightingEnabled!
    this.exposureLocation = locations.exposure!
    this.relightStrengthLocation = locations.relightStrength!
    this.lightLocation = locations.light!
    this.lightIntensityLocation = locations.lightIntensity!
    this.lightColorLocation = locations.lightColor!
    this.ambientIntensityLocation = locations.ambientIntensity!
    this.ambientColorLocation = locations.ambientColor!
    this.diffuseWrapLocation = locations.diffuseWrap!
    this.diffuseThresholdLocation = locations.diffuseThreshold!
    this.diffuseSoftnessLocation = locations.diffuseSoftness!
    this.bandStrengthLocation = locations.bandStrength!
    this.bandThresholdLocation = locations.bandThreshold!
    this.bandSoftnessLocation = locations.bandSoftness!
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW)
    gl.useProgram(program)
    const position = gl.getAttribLocation(program, 'a_position')
    gl.enableVertexAttribArray(position)
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0)
    gl.activeTexture(gl.TEXTURE0)
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image)
    gl.uniform1i(gl.getUniformLocation(program, 'u_base'), 0)
    gl.activeTexture(gl.TEXTURE1)
    gl.bindTexture(gl.TEXTURE_2D, normalTexture)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, normalImage)
    gl.uniform1i(gl.getUniformLocation(program, 'u_normal'), 1)
  }

  render(layout: ArtworkLayout, dprCap: number, view: RenderView, lighting: LightingState): void {
    if (this.disposed) return
    const gl = this.gl
    const dpr = Math.min(window.devicePixelRatio || 1, dprCap)
    const width = Math.max(1, Math.round(layout.viewportWidth * dpr))
    const height = Math.max(1, Math.round(layout.viewportHeight * dpr))
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width
      this.canvas.height = height
    }
    gl.viewport(0, 0, width, height)
    gl.clearColor(0.08, 0.075, 0.075, 1)
    gl.clear(gl.COLOR_BUFFER_BIT)
    gl.useProgram(this.program)
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer)
    gl.activeTexture(gl.TEXTURE0)
    gl.bindTexture(gl.TEXTURE_2D, this.texture)
    gl.activeTexture(gl.TEXTURE1)
    gl.bindTexture(gl.TEXTURE_2D, this.normalTexture)
    gl.uniform1i(this.viewLocation, view === 'normal' ? 1 : view === 'lit' ? 2 : 0)
    gl.uniform1i(this.lightingEnabledLocation, lighting.enabled ? 1 : 0)
    gl.uniform1f(this.exposureLocation, lighting.exposure)
    gl.uniform1f(this.relightStrengthLocation, lighting.relightStrength)
    gl.uniform3f(this.lightLocation, lighting.direction.x, lighting.direction.y, lighting.direction.z)
    gl.uniform1f(this.lightIntensityLocation, lighting.enabled ? lighting.intensity : 0)
    gl.uniform3f(this.lightColorLocation, lighting.color.r, lighting.color.g, lighting.color.b)
    gl.uniform1f(this.ambientIntensityLocation, lighting.ambientIntensity)
    gl.uniform3f(this.ambientColorLocation, lighting.ambientColor.r, lighting.ambientColor.g, lighting.ambientColor.b)
    gl.uniform1f(this.diffuseWrapLocation, lighting.diffuseWrap)
    gl.uniform1f(this.diffuseThresholdLocation, lighting.diffuseThreshold)
    gl.uniform1f(this.diffuseSoftnessLocation, lighting.diffuseSoftness)
    gl.uniform1f(this.bandStrengthLocation, lighting.bandStrength)
    gl.uniform1f(this.bandThresholdLocation, lighting.bandThreshold)
    gl.uniform1f(this.bandSoftnessLocation, lighting.bandSoftness)
    gl.uniform4f(this.rectLocation, layout.x / layout.viewportWidth, 1 - (layout.y + layout.height) / layout.viewportHeight, layout.width / layout.viewportWidth, layout.height / layout.viewportHeight)
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
    if (gl.getError() !== gl.NO_ERROR) throw new Error('WebGL draw failed')
  }

  destroy(): void {
    if (this.disposed) return
    this.disposed = true
    const gl = this.gl
    gl.deleteTexture(this.texture)
    gl.deleteTexture(this.normalTexture)
    gl.deleteBuffer(this.buffer)
    gl.deleteProgram(this.program)
  }
}
