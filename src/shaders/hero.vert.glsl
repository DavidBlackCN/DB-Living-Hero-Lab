#version 300 es
in vec2 a_position;
out vec2 v_uv;
uniform vec4 u_rect;
void main() {
  vec2 position = u_rect.xy + (a_position + 1.0) * 0.5 * u_rect.zw;
  gl_Position = vec4(position * 2.0 - 1.0, 0.0, 1.0);
  v_uv = vec2((a_position.x + 1.0) * 0.5, (1.0 - a_position.y) * 0.5);
}
