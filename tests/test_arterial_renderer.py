import unittest
from pathlib import Path

import pyvista as pv

from src.visualization.arterial_renderer import add_arterial_mesh


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

    def test_rejects_unknown_color_map(self):
        with self.assertRaises(ValueError):
            add_arterial_mesh(RecordingPlotter(), self.model, "unknown")


if __name__ == "__main__":
    unittest.main()
