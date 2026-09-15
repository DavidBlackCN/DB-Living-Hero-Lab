import { vertex } from './shaders';

// Render targets use bottom-left texture coordinates; the artwork uses top-left.
const blur = `#version 300 es
precision highp float;
in vec2 uv;
out vec4 color;
uniform sampler2D image;
uniform vec2 stepUV;
void main() {
  vec2 p=vec2(uv.x,1.0-uv.y);
  vec3 c=texture(image,p).rgb*.227027;
  c+=(texture(image,p+stepUV*1.384615).rgb+texture(image,p-stepUV*1.384615).rgb)*.316216;
  c+=(texture(image,p+stepUV*3.230769).rgb+texture(image,p-stepUV*3.230769).rgb)*.070270;
  color=vec4(c,1);
}`;

export function createBloom(gl: WebGL2RenderingContext) {
  const textures: WebGLTexture[] = [], buffers: WebGLFramebuffer[] = [], shaders: WebGLShader[] = [];
  const program=gl.createProgram()!;
  let width=0, height=0;
  const destroy=()=>{
    textures.forEach(t=>gl.deleteTexture(t)); buffers.forEach(b=>gl.deleteFramebuffer(b));
    shaders.forEach(s=>gl.deleteShader(s)); gl.deleteProgram(program);
  };
  try {
    for(const [type,source] of [[gl.VERTEX_SHADER,vertex],[gl.FRAGMENT_SHADER,blur]] as const) {
      const shader=gl.createShader(type)!; shaders.push(shader);
      gl.shaderSource(shader,source); gl.compileShader(shader);
      if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader) ?? 'Bloom compile failed');
      gl.attachShader(program,shader);
    }
    gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS)) throw new Error('Bloom link failed');
    for(let i=0;i<3;i++) { textures.push(gl.createTexture()!); buffers.push(gl.createFramebuffer()!); }
  } catch(error) { destroy(); throw error; }
  const step=gl.getUniformLocation(program,'stepUV');
  const bind=(i:number)=>{ gl.bindFramebuffer(gl.FRAMEBUFFER,buffers[i]); gl.viewport(0,0,width,height); };
  return {
    begin(w:number,h:number) {
      const nw=Math.max(1,Math.ceil(w/4)),nh=Math.max(1,Math.ceil(h/4));
      gl.activeTexture(gl.TEXTURE4);
      if(nw!==width||nh!==height) {
        width=nw; height=nh;
        textures.forEach((t,i)=>{
          gl.bindTexture(gl.TEXTURE_2D,t);
          gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
          gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
          gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
          gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,width,height,0,gl.RGBA,gl.UNSIGNED_BYTE,null);
          bind(i); gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,t,0);
          if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE) throw new Error('Bloom framebuffer incomplete');
        });
      }
      gl.bindTexture(gl.TEXTURE_2D,null); bind(0);
    },
    finish(radius:number) {
      gl.useProgram(program); gl.uniform1i(gl.getUniformLocation(program,'image'),4);
      for(let i=1;i<=2;i++) {
        bind(i); gl.activeTexture(gl.TEXTURE4); gl.bindTexture(gl.TEXTURE_2D,textures[i-1]);
        gl.uniform2f(step,i===1?radius/width:0,i===2?radius/height:0);
        gl.drawArrays(gl.TRIANGLES,0,3);
      }
      gl.bindFramebuffer(gl.FRAMEBUFFER,null);
      gl.bindTexture(gl.TEXTURE_2D,textures[2]);
    },
    getSize() { return { width, height }; },
    destroy,
  };
}
