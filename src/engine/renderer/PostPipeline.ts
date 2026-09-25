import vertexSource from '../../shaders/post.vert.glsl?raw'
import fragmentSource from '../../shaders/post.frag.glsl?raw'
import type { PostState } from '../../config/post'

type Target = { texture: WebGLTexture; framebuffer: WebGLFramebuffer; width: number; height: number }

function shader(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader {
  const result = gl.createShader(type)
  if (!result) throw new Error('Post shader allocation failed')
  gl.shaderSource(result, source)
  gl.compileShader(result)
  if (!gl.getShaderParameter(result, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(result) || 'Post shader compilation failed')
  return result
}

export class PostPipeline {
  private program: WebGLProgram
  private buffer: WebGLBuffer
  private scene: Target | null = null
  private gate: WebGLTexture | null = null
  private raw: Target[] = []
  private bloom: Target[] = []
  private width = 0
  private height = 0

  constructor(private gl: WebGL2RenderingContext) {
    const vertex = shader(gl, gl.VERTEX_SHADER, vertexSource)
    const fragment = shader(gl, gl.FRAGMENT_SHADER, fragmentSource)
    const program = gl.createProgram()
    const buffer = gl.createBuffer()
    if (!program || !buffer) throw new Error('Post resources unavailable')
    gl.attachShader(program, vertex)
    gl.attachShader(program, fragment)
    gl.bindAttribLocation(program, 0, 'a_position')
    gl.linkProgram(program)
    gl.deleteShader(vertex)
    gl.deleteShader(fragment)
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || 'Post link failed')
    this.program = program
    this.buffer = buffer
    gl.useProgram(program)
    for (const [name, unit] of [['u_source', 0], ['u_gate', 1], ['u_scene', 2],
      ['u_bloom0', 3], ['u_bloom1', 4], ['u_bloom2', 5], ['u_bloom3', 6], ['u_edgeTone', 7]] as const) {
      gl.uniform1i(gl.getUniformLocation(program, name), unit)
    }
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW)
  }

  private texture(width: number, height: number, format: number = this.gl.RGBA8): WebGLTexture {
    const gl = this.gl
    const texture = gl.createTexture()
    if (!texture) throw new Error('Post texture allocation failed')
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.texImage2D(gl.TEXTURE_2D, 0, format, width, height, 0,
      format === gl.R8 ? gl.RED : gl.RGBA, gl.UNSIGNED_BYTE, null)
    return texture
  }

  private target(width: number, height: number): Target {
    const gl = this.gl
    const texture = this.texture(width, height)
    const framebuffer = gl.createFramebuffer()
    if (!framebuffer) throw new Error('Post framebuffer allocation failed')
    gl.bindFramebuffer(gl.FRAMEBUFFER, framebuffer)
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0)
    gl.drawBuffers([gl.COLOR_ATTACHMENT0])
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) throw new Error('Post framebuffer incomplete')
    return { texture, framebuffer, width, height }
  }

  private releaseTargets(): void {
    const gl = this.gl
    for (const target of [this.scene, ...this.raw, ...this.bloom]) {
      if (!target) continue
      gl.deleteTexture(target.texture)
      gl.deleteFramebuffer(target.framebuffer)
    }
    if (this.gate) gl.deleteTexture(this.gate)
    this.scene = null
    this.gate = null
    this.raw = []
    this.bloom = []
  }

  resize(width: number, height: number): void {
    if (width === this.width && height === this.height) return
    this.releaseTargets()
    this.width = width
    this.height = height
    const gl = this.gl
    this.scene = this.target(width, height)
    this.gate = this.texture(width, height, gl.R8)
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.scene.framebuffer)
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT1, gl.TEXTURE_2D, this.gate, 0)
    gl.drawBuffers([gl.COLOR_ATTACHMENT0, gl.COLOR_ATTACHMENT1])
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) throw new Error('Post scene framebuffer incomplete')
    for (const scale of [2, 4, 8, 16]) {
      const w = Math.max(1, Math.floor(width / scale))
      const h = Math.max(1, Math.floor(height / scale))
      this.raw.push(this.target(w, h))
      this.bloom.push(this.target(w, h))
    }
  }

  begin(width: number, height: number): void {
    this.resize(width, height)
    const gl = this.gl
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.scene!.framebuffer)
    gl.drawBuffers([gl.COLOR_ATTACHMENT0, gl.COLOR_ATTACHMENT1])
    gl.viewport(0, 0, width, height)
    gl.clearColor(0, 0, 0, 0)
    gl.clear(gl.COLOR_BUFFER_BIT)
  }

  private uniform(name: string): WebGLUniformLocation | null { return this.gl.getUniformLocation(this.program, name) }
  private bind(unit: number, texture: WebGLTexture): void {
    this.gl.activeTexture(this.gl.TEXTURE0 + unit)
    this.gl.bindTexture(this.gl.TEXTURE_2D, texture)
  }
  private draw(target: Target, mode: number, source: WebGLTexture, sourceWidth: number, sourceHeight: number): void {
    const gl = this.gl
    gl.bindFramebuffer(gl.FRAMEBUFFER, target.framebuffer)
    gl.drawBuffers([gl.COLOR_ATTACHMENT0])
    gl.viewport(0, 0, target.width, target.height)
    this.bind(0, source)
    gl.uniform2f(this.uniform('u_texel'), 1 / sourceWidth, 1 / sourceHeight)
    gl.uniform1i(this.uniform('u_mode'), mode)
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
  }

  render(post: PostState, sceneExposureStops: number, rect: { x: number; y: number; width: number; height: number }, edgeTone: WebGLTexture, nightWeight: number): void {
    const gl = this.gl
    gl.useProgram(this.program)
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer)
    gl.enableVertexAttribArray(0)
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0)
    this.bind(1, this.gate!)
    gl.uniform1f(this.uniform('u_sceneExposure'), 2 ** sceneExposureStops)
    gl.uniform1f(this.uniform('u_postExposure'), 2 ** post.exposureStops)
    gl.uniform1f(this.uniform('u_threshold'), post.threshold)
    gl.uniform1f(this.uniform('u_knee'), post.knee)
    if (post.bloomEnabled || post.view === 'bright' || post.view === 'bloom') {
      for (let level = 0; level < 4; level++) {
        const source = level === 0 ? this.scene! : this.bloom[level - 1]
        this.draw(this.raw[level], level === 0 ? 0 : 1, source.texture, source.width, source.height)
        this.draw(this.bloom[level], 2, this.raw[level].texture, this.raw[level].width, this.raw[level].height)
      }
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, null)
    gl.drawBuffers([gl.BACK])
    gl.viewport(0, 0, this.width, this.height)
    this.bind(2, this.scene!.texture)
    this.bind(0, this.raw[0].texture)
    this.bloom.forEach((target, i) => this.bind(3 + i, target.texture))
    this.bind(7, edgeTone)
    gl.uniform1i(this.uniform('u_mode'), 3)
    gl.uniform1i(this.uniform('u_preview'), post.view === 'bright' ? 1 : post.view === 'bloom' ? 2 : post.view === 'grade' ? 3 : 0)
    gl.uniform1f(this.uniform('u_bloomStrength'), post.bloomEnabled ? post.bloomStrength : 0)
    gl.uniform1f(this.uniform('u_nightWeight'), nightWeight)
    gl.uniform1f(this.uniform('u_saturation'), post.saturation)
    gl.uniform1f(this.uniform('u_contrast'), post.contrast)
    gl.uniform3f(this.uniform('u_tint'), ...post.tint)
    gl.uniform4f(this.uniform('u_artworkRect'), rect.x, rect.y, rect.width, rect.height)
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4)
  }

  destroy(): void {
    this.releaseTargets()
    this.gl.deleteBuffer(this.buffer)
    this.gl.deleteProgram(this.program)
  }
}
