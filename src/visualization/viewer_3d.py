
import numpy as np
from pyvistaqt import QtInteractor

from visualization.affine_transform import (
    rotation_matrix,
    scale_matrix,
    translation_matrix,
)
from visualization.arterial_renderer import (
    add_arterial_mesh,
    set_anti_aliasing,
)


class Viewer3D(QtInteractor):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._anti_aliasing_enabled = True
        self._color_map = "viridis"
        self._transform_matrix = np.eye(4)
        self._translation = (0.0, 0.0, 0.0)
        self._rotation = (0.0, 0.0, 0.0)
        self._scale = 1.0

    def show_model(self, model, color_map="viridis"):
        self._model = model
        self._color_map = color_map
        self._transform_matrix = np.eye(4)
        self._translation = (0.0, 0.0, 0.0)
        self._rotation = (0.0, 0.0, 0.0)
        self._scale = 1.0
        self._render_model(reset_camera=True)

    def set_color_map(self, color_map):
        self._color_map = color_map
        self._render_model()

    def set_antialiasing(self, enabled):
        self._anti_aliasing_enabled = bool(enabled)
        self._apply_anti_aliasing()
        if self._model is not None:
            self.render()

    def _apply_anti_aliasing(self):
        set_anti_aliasing(self, self._anti_aliasing_enabled)

    def translate(self, x, y, z):
        if self._model is None:
            raise RuntimeError("Nenhum modelo 3D foi carregado.")
        distance = self._model.length
        self.set_transform_parameters(
            (
                self._translation[0] + x / distance,
                self._translation[1] + y / distance,
                self._translation[2] + z / distance,
            ),
            self._rotation,
            self._scale,
        )

    def translate_by_scene_scale(self, x, y, z):
        if self._model is None:
            raise RuntimeError("Nenhum modelo 3D foi carregado.")
        self.set_transform_parameters(
            (
                self._translation[0] + x * 0.1,
                self._translation[1] + y * 0.1,
                self._translation[2] + z * 0.1,
            ),
            self._rotation,
            self._scale,
        )

    def rotate(self, axis, angle_degrees):
        if self._model is None:
            raise RuntimeError("Nenhum modelo 3D foi carregado.")
        axes = {"x": 0, "y": 1, "z": 2}
        if axis not in axes:
            raise ValueError(f"Eixo de rotação não suportado: {axis}")
        rotation = list(self._rotation)
        rotation[axes[axis]] += angle_degrees
        self.set_transform_parameters(
            self._translation,
            rotation,
            self._scale,
        )

    def scale(self, factor):
        self.set_transform_parameters(
            self._translation,
            self._rotation,
            self._scale * factor,
        )

    def set_transform_parameters(self, translation, rotation, scale):
        if self._model is None:
            raise RuntimeError("Nenhum modelo 3D foi carregado.")

        scene_length = self._model.length
        center = np.asarray(self._model.center, dtype=float)
        transform = translation_matrix(
            *(distance * scene_length for distance in translation)
        )
        for axis, angle in zip(("x", "y", "z"), rotation):
            transform = (
                transform @ rotation_matrix(axis, angle, center)
            )
        transform = transform @ scale_matrix(scale, center)

        self._translation = tuple(float(value) for value in translation)
        self._rotation = tuple(float(value) for value in rotation)
        self._scale = float(scale)
        self._transform_matrix = transform
        self._render_model()

    def reset_transform(self):
        if self._model is None:
            raise RuntimeError("Nenhum modelo 3D foi carregado.")
        self._transform_matrix = np.eye(4)
        self._translation = (0.0, 0.0, 0.0)
        self._rotation = (0.0, 0.0, 0.0)
        self._scale = 1.0
        self._render_model(reset_camera=True)

    def set_camera_view(self, view):
        views = {
            "isometric": self.view_isometric,
            "top": self.view_xy,
            "front": self.view_xz,
            "side": self.view_yz,
        }
        if view not in views:
            raise ValueError(f"Vista de câmera não suportada: {view}")

        views[view]()
        self.reset_camera()
        self.render()

    def set_parallel_projection(self, enabled):
        if enabled:
            self.enable_parallel_projection()
        else:
            self.disable_parallel_projection()
        self.render()

    def _render_model(self, reset_camera=False):
        self.clear()
        self._apply_anti_aliasing()
        transformed_model = self._model.transform(
            self._transform_matrix,
            inplace=False,
        )
        add_arterial_mesh(self, transformed_model, self._color_map)
        if reset_camera:
            self.reset_camera()
        self.render()
