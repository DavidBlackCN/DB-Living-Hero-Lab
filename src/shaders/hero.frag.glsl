#version 300 es
precision mediump float;
in vec2 v_uv;
uniform sampler2D u_base;
out vec4 outColor;
void main() {
  outColor = texture(u_base, v_uv);
}
