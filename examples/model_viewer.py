# Adpated from https://github.com/moderngl/moderngl/blob/master/examples/simple_camera.py


from pathlib import Path
import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl
import moderngl_window as mglw

import site

site.addsitedir(Path(__file__).parent.parent.as_posix())


from geoproc.mesh_loader import iter_binary_stl_mesh_triangles

STL_MESH_FILEPATH = Path(__file__).parent.parent / "tests/suzanne.stl"


class Example(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL Example"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True


class Camera:
    def __init__(self, ratio):
        self._zoom_step = 0.1
        self._move_vertically = 0.1
        self._move_horizontally = 0.1
        self._rotate_horizontally = 0.2
        self._rotate_vertically = 0.1

        self._field_of_view_degrees = 60.0
        self._z_near = 0.1
        self._z_far = 100
        self._ratio = ratio
        self.build_projection()

        self._camera_position = Vector3([0.0, -10.0, 0.0])
        self._camera_front = Vector3([0.0, 1.0, 0.0])
        self._camera_up = Vector3([0.0, 0.0, 1.0])
        self._cameras_target = self._camera_position + self._camera_front
        self.build_look_at()

    def zoom_in(self):
        self._field_of_view_degrees = self._field_of_view_degrees - self._zoom_step
        self.build_projection()

    def zoom_out(self):
        self._field_of_view_degrees = self._field_of_view_degrees + self._zoom_step
        self.build_projection()

    def move_forward(self):
        self._camera_position = self._camera_position + self._camera_front * self._move_horizontally
        self.build_look_at()

    def move_backwards(self):
        self._camera_position = self._camera_position - self._camera_front * self._move_horizontally
        self.build_look_at()

    def strafe_left(self):
        self._camera_position = (
            self._camera_position - vector.normalize(self._camera_front ^ self._camera_up) * self._move_horizontally
        )
        self.build_look_at()

    def strafe_right(self):
        self._camera_position = (
            self._camera_position + vector.normalize(self._camera_front ^ self._camera_up) * self._move_horizontally
        )
        self.build_look_at()

    def strafe_up(self):
        self._camera_position = self._camera_position + self._camera_up * self._move_vertically
        self.build_look_at()

    def strafe_down(self):
        self._camera_position = self._camera_position - self._camera_up * self._move_vertically
        self.build_look_at()

    def rotate_left_right(self, value: float):
        rotation = Quaternion.from_axis_rotation(self._camera_up, -2 * float(value) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def rotate_up_down(self, value: float):
        rotation = Quaternion.from_axis_rotation(
            vector.normalize(self._camera_front ^ self._camera_up), -2 * float(value) * np.pi / 180
        )
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def build_look_at(self):
        self._cameras_target = self._camera_position + self._camera_front
        self.mat_lookat = Matrix44.look_at(self._camera_position, self._cameras_target, self._camera_up)

    def build_projection(self):
        self.mat_projection = Matrix44.perspective_projection(
            self._field_of_view_degrees, self._ratio, self._z_near, self._z_far
        )


class PerspectiveProjection(Example):
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330

                uniform mat4 Mvp;

                in vec3 in_vert;

                void main() {
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            """,
            fragment_shader="""
                #version 330

                out vec4 f_color;

                void main() {
                    f_color = vec4(0.1, 0.1, 0.1, 1.0);
                }
            """,
        )

        vertices = np.array([[[*vpos] for vpos in tri] for tri in iter_binary_stl_mesh_triangles(STL_MESH_FILEPATH)])

        self.camera = Camera(self.aspect_ratio)
        self.mvp = self.prog["Mvp"]
        # self.vbo = self.ctx.buffer(grid(15, 10).astype('f4'))
        self.vbo = self.ctx.buffer(vertices.astype("f4"))
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, "in_vert")  # type: ignore

        self.states = {
            self.wnd.keys.W: False,
            self.wnd.keys.S: False,
            self.wnd.keys.UP: False,
            self.wnd.keys.DOWN: False,
            self.wnd.keys.A: False,
            self.wnd.keys.D: False,
            self.wnd.keys.Q: False,
            self.wnd.keys.E: False,
            self.wnd.keys.Z: False,
            self.wnd.keys.X: False,
        }

    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        self.camera.rotate_left_right(dx * 0.05)
        self.camera.rotate_up_down(dy * 0.05)

    def move_camera(self):
        if self.states.get(self.wnd.keys.W):
            self.camera.move_forward()

        if self.states.get(self.wnd.keys.S):
            self.camera.move_backwards()

        if self.states.get(self.wnd.keys.UP):
            self.camera.strafe_up()

        if self.states.get(self.wnd.keys.DOWN):
            self.camera.strafe_down()

        if self.states.get(self.wnd.keys.A):
            self.camera.strafe_left()

        if self.states.get(self.wnd.keys.D):
            self.camera.strafe_right()

        if self.states.get(self.wnd.keys.Z):
            self.camera.zoom_in()

        if self.states.get(self.wnd.keys.X):
            self.camera.zoom_out()

    def key_event(self, key, action, modifiers):
        if key not in self.states:
            print(key, action)
            return

        if action == self.wnd.keys.ACTION_PRESS:
            self.states[key] = True
        else:
            self.states[key] = False

    def render(self, time, frame_time):
        self.move_camera()

        self.ctx.clear(1.0, 1.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)  # type: ignore

        self.mvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype("f4"))  # type: ignore
        self.vao.render(moderngl.TRIANGLES)  # type: ignore


if __name__ == "__main__":
    PerspectiveProjection.run()
