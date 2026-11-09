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
from visualization.arterial_renderer import (
    add_arterial_mesh,
    set_anti_aliasing,
)


class Viewer2D(QtInteractor):
    artery_selected = Signal(object)
    roi_vertex_added = Signal(object)
    roi_finalized = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._anti_aliasing_enabled = True
        self._inspection_observer = None
        self._inspection_enabled = False
        self._inspection_selection = None
        self._inspection_pixel = None
        self._selected_artery_actor = None
        self._inspection_marker_actor = None
        self._scanline_observer = None
        self._scanline_enabled = False
        self._roi_vertices = []
        self._roi_finalized = False
        self._roi_outline_actor = None
        self._roi_fill_actors = []
        self._roi_display_depth = 0.0
        self._roi_cell_size = 8.0
        self._cell_picker = vtkCellPicker()
        self._cell_picker.SetTolerance(0.01)

    def show_model(self, model, color_map="viridis"):
        interactor = self.iren.interactor
        if self._inspection_observer is not None:
            interactor.RemoveObserver(self._inspection_observer)
            self._inspection_observer = None
        if self._scanline_observer is not None:
            interactor.RemoveObserver(self._scanline_observer)
            self._scanline_observer = None
        self._inspection_enabled = False
        self._scanline_enabled = False
        self._model = model
        self.clear()
        self._selected_artery_actor = None
        self._inspection_marker_actor = None
        self._inspection_selection = None
        self._inspection_pixel = None
        self._clear_roi_actors()
        self._roi_vertices.clear()
        self._roi_finalized = False
        self._apply_anti_aliasing()
        add_arterial_mesh(self, model, color_map)
        self.view_xy()
        self.reset_camera()
        self.render()
        self.artery_selected.emit(None)

    def set_antialiasing(self, enabled):
        self._anti_aliasing_enabled = bool(enabled)
        self._apply_anti_aliasing()
        if self._model is not None:
            self.render()

    def _apply_anti_aliasing(self):
        set_anti_aliasing(self, self._anti_aliasing_enabled)

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

    def set_scanline_roi_enabled(self, enabled):
        enabled = bool(enabled)
        if enabled == self._scanline_enabled:
            return
        if enabled and self._model is None:
            raise RuntimeError("Nenhum modelo 2D foi carregado.")

        self._scanline_enabled = enabled
        interactor = self.iren.interactor
        if enabled:
            self._roi_vertices.clear()
            self._roi_finalized = False
            self._roi_outline_actor = None
            self._roi_fill_actors.clear()
            center = self._model.center
            self.renderer.SetWorldPoint(*center, 1.0)
            self.renderer.WorldToDisplay()
            self._roi_display_depth = self.renderer.GetDisplayPoint()[2]
            self._scanline_observer = interactor.AddObserver(
                "LeftButtonPressEvent", self._add_roi_vertex, 1.0
            )
        else:
            if self._scanline_observer is not None:
                interactor.RemoveObserver(self._scanline_observer)
                self._scanline_observer = None
            self.clear_scanline_roi()

    def _add_roi_vertex(self, interactor, _event):
        if self._roi_finalized:
            return
        display_x, display_y = interactor.GetEventPosition()
        pixel = (
            int(round(display_x / self._roi_cell_size)),
            int(round(display_y / self._roi_cell_size)),
        )
        world = self._world_at_roi_pixel(pixel)
        vertex = {"pixel": pixel, "world": world}
        self._roi_vertices.append(vertex)
        self._draw_roi_outline()
        self.roi_vertex_added.emit(vertex)

    def _world_at_roi_pixel(self, pixel):
        display_x = (pixel[0] + 0.5) * self._roi_cell_size
        display_y = (pixel[1] + 0.5) * self._roi_cell_size
        self.renderer.SetDisplayPoint(
            display_x, display_y, max(0.0, self._roi_display_depth - 1e-5)
        )
        self.renderer.DisplayToWorld()
        world = np.asarray(self.renderer.GetWorldPoint(), dtype=float)
        if world[3] == 0:
            raise RuntimeError("Não foi possível converter a posição da ROI.")
        return tuple(world[:3] / world[3])

    def _draw_roi_outline(self):
        self._remove_inspection_actor("_roi_outline_actor")
        if len(self._roi_vertices) < 2:
            self.render()
            return

        points = np.asarray(
            [vertex["world"] for vertex in self._roi_vertices], dtype=float
        )
        polyline = pv.PolyData(points)
        line_points = list(range(points.shape[0]))
        if len(points) >= 3:
            line_points.append(0)
        connections = [len(line_points), *line_points]
        polyline.lines = np.asarray(connections, dtype=np.int64)
        self._roi_outline_actor = self.add_mesh(
            polyline,
            color="#2a9d8f" if self._roi_finalized else "#d1495b",
            line_width=3,
            render_lines_as_tubes=True,
            name="scanline_roi_outline",
        )
        self.render()

    def finalize_scanline_roi(self):
        if self._roi_finalized or len(self._roi_vertices) < 3:
            return
        self._roi_finalized = True
        self._draw_roi_outline()
        self.roi_finalized.emit(tuple(self._roi_vertices))

    def clear_scanline_roi(self):
        self._roi_vertices.clear()
        self._roi_finalized = False
        self._clear_roi_actors()
        self.render()

    def set_scanline_fill_step(self, step):
        if step is None:
            for actor in self._roi_fill_actors:
                self.remove_actor(actor)
            self._roi_fill_actors.clear()
            self.render()
            return

        points = []
        y = step["y"]
        for left, right in step["spans"]:
            for x in range(left, right + 1):
                points.append(self._world_at_roi_pixel((x, y)))
        if points:
            cloud = pv.PolyData(np.asarray(points, dtype=float))
            actor = self.add_mesh(
                cloud,
                color="#f4b400",
                point_size=self._roi_cell_size,
                opacity=0.6,
                render_points_as_spheres=False,
                name="scanline_roi_fill",
            )
            self._roi_fill_actors.append(actor)
        self.render()

    def _clear_roi_actors(self):
        self._remove_inspection_actor("_roi_outline_actor")
        for actor in self._roi_fill_actors:
            self.remove_actor(actor)
        self._roi_fill_actors.clear()

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
