import unittest
from pathlib import Path

import pyvista as pv

from src.visualization.arterial_renderer import (
    add_arterial_mesh,
    set_anti_aliasing,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RecordingPlotter:
    def __init__(self):
        self.meshes = []

    def add_mesh(self, mesh, **options):
        self.meshes.append((mesh, options))


class ArterialRendererTests(unittest.TestCase):
    def setUp(self):
        self.model = pv.read(
            PROJECT_ROOT / "data" / "3D" / "tree3D_Nterm016.vtk"
        )

    def test_radius_maps_to_multiple_segment_widths(self):
        plotter = RecordingPlotter()

        add_arterial_mesh(plotter, self.model, "viridis")

        widths = [options["line_width"] for _, options in plotter.meshes]
        self.assertGreater(len(set(widths)), 1)
        self.assertTrue(all(mesh.n_cells > 0 for mesh, _ in plotter.meshes))
        self.assertEqual(
            sum(mesh.n_cells for mesh, _ in plotter.meshes),
            self.model.n_cells,
        )
        self.assertTrue(plotter.meshes[0][1]["show_scalar_bar"])
        self.assertTrue(
            all(not options["show_scalar_bar"] for _, options in plotter.meshes[1:])
        )

    def test_hsv_and_rgb_maps_are_available(self):
        for color_map in ("hsv", "rgb"):
            with self.subTest(color_map=color_map):
                plotter = RecordingPlotter()
                add_arterial_mesh(plotter, self.model, color_map)
                self.assertTrue(plotter.meshes)

    def test_model_without_radius_uses_uniform_line_style(self):
        model = self.model.copy()
        del model.cell_data["raio"]
        plotter = RecordingPlotter()

        add_arterial_mesh(plotter, model)

        self.assertEqual(len(plotter.meshes), 1)
        self.assertEqual(plotter.meshes[0][1]["line_width"], 3)

    def test_thickness_scale_changes_width_spread(self):
        uniform_plotter = RecordingPlotter()
        add_arterial_mesh(
            uniform_plotter,
            self.model,
            show_scalar_bar=False,
            thickness_scale=0,
        )
        varied_plotter = RecordingPlotter()
        add_arterial_mesh(
            varied_plotter,
            self.model,
            show_scalar_bar=False,
            thickness_scale=1,
        )

        uniform_widths = {
            options["line_width"] for _, options in uniform_plotter.meshes
        }
        varied_widths = {
            options["line_width"] for _, options in varied_plotter.meshes
        }
        self.assertEqual(uniform_widths, {6.0})
        self.assertGreater(len(varied_widths), 1)

    def test_rejects_unknown_color_map(self):
        with self.assertRaises(ValueError):
            add_arterial_mesh(RecordingPlotter(), self.model, "unknown")

    def test_antialiasing_can_be_enabled_and_disabled(self):
        class AntiAliasingPlotter:
            def __init__(self):
                self.calls = []

            def enable_anti_aliasing(self, method):
                self.calls.append(("enable", method))

            def disable_anti_aliasing(self):
                self.calls.append(("disable",))

        plotter = AntiAliasingPlotter()

        set_anti_aliasing(plotter, True)
        set_anti_aliasing(plotter, False)

        self.assertEqual(
            plotter.calls,
            [("enable", "fxaa"), ("disable",)],
        )


if __name__ == "__main__":
    unittest.main()
