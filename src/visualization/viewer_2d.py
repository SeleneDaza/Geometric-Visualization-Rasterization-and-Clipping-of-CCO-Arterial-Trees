import numpy as np
from PySide6.QtCore import Signal
import pyvista as pv
from pyvistaqt import QtInteractor
from vtkmodules.vtkRenderingCore import vtkCellPicker

from visualization.artery_inspector import (
    closest_cell_segment,
    original_cell_id,
    raster_grid_endpoints,
)
from visualization.arterial_renderer import add_arterial_mesh


class Viewer2D(QtInteractor):
    artery_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._inspection_observer = None
        self._inspection_enabled = False
        self._inspection_selection = None
        self._inspection_pixel = None
        self._selected_artery_actor = None
        self._inspection_marker_actor = None
        self._cell_picker = vtkCellPicker()
        self._cell_picker.SetTolerance(0.01)

    def show_model(self, model, color_map="viridis"):
        self._model = model
        self.clear()
        self._selected_artery_actor = None
        self._inspection_marker_actor = None
        self._inspection_selection = None
        self._inspection_pixel = None
        add_arterial_mesh(self, model, color_map)
        self.view_xy()
        self.reset_camera()
        self.render()
        self.artery_selected.emit(None)

    def set_artery_inspection_enabled(self, enabled):
        enabled = bool(enabled)
        if enabled == self._inspection_enabled:
            return
        if enabled and self._model is None:
            raise RuntimeError("Nenhum modelo 2D foi carregado.")

        self._inspection_enabled = enabled
        interactor = self.iren.interactor
        if enabled:
            self._inspection_observer = interactor.AddObserver(
                "LeftButtonPressEvent", self._pick_artery, 1.0
            )
        else:
            if self._inspection_observer is not None:
                interactor.RemoveObserver(self._inspection_observer)
                self._inspection_observer = None

    def _pick_artery(self, interactor, _event):
        x, y = interactor.GetEventPosition()
        if not self._cell_picker.Pick(x, y, 0, self.renderer):
            return

        cell_id = original_cell_id(self._cell_picker)
        if cell_id is None:
            return
        segment = closest_cell_segment(
            self._model,
            cell_id,
            self._cell_picker.GetPickPosition(),
        )
        if segment is None:
            return

        start_world, end_world = segment
        start_grid, end_grid = raster_grid_endpoints(
            self.renderer,
            start_world,
            end_world,
        )
        radius = None
        if "raio" in self._model.cell_data:
            value = float(self._model.cell_data["raio"][cell_id])
            if np.isfinite(value):
                radius = value
        self.artery_selected.emit({
            "cell_id": cell_id,
            "start_world": start_world,
            "end_world": end_world,
            "start_grid": start_grid,
            "end_grid": end_grid,
            "radius": radius,
        })

    def set_inspection_selection(self, selection):
        self._remove_inspection_actor("_selected_artery_actor")
        self._remove_inspection_actor("_inspection_marker_actor")
        self._inspection_selection = selection
        self._inspection_pixel = None
        if selection is None:
            self.render()
            return

        selected_cell = self._model.extract_cells([selection["cell_id"]])
        self._selected_artery_actor = self.add_mesh(
            selected_cell,
            color="#e5484d",
            line_width=6,
            render_lines_as_tubes=True,
            name="inspected_artery",
        )
        self.render()

    def set_inspection_pixel(self, pixel):
        self._inspection_pixel = pixel
        self._remove_inspection_actor("_inspection_marker_actor")
        if pixel is None or self._inspection_selection is None:
            self.render()
            return

        start_grid = self._inspection_selection["start_grid"]
        end_grid = self._inspection_selection["end_grid"]
        steps = max(
            abs(end_grid[0] - start_grid[0]),
            abs(end_grid[1] - start_grid[1]),
        )
        if steps == 0:
            fraction = 0.0
        else:
            fraction = (
                max(abs(pixel[0] - start_grid[0]), abs(pixel[1] - start_grid[1]))
                / steps
            )
        fraction = float(np.clip(fraction, 0.0, 1.0))
        start = np.asarray(self._inspection_selection["start_world"])
        end = np.asarray(self._inspection_selection["end_world"])
        marker = pv.PolyData((start + fraction * (end - start)).reshape(1, 3))
        self._inspection_marker_actor = self.add_mesh(
            marker,
            color="#f4b400",
            point_size=18,
            render_points_as_spheres=True,
            name="inspected_pixel",
        )
        self.render()

    def _remove_inspection_actor(self, attribute):
        actor = getattr(self, attribute)
        if actor is not None:
            self.remove_actor(actor)
            setattr(self, attribute, None)
