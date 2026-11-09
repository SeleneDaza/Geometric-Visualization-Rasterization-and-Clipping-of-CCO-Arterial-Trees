import tempfile
import unittest
from pathlib import Path

import numpy as np
import pyvista as pv

from src.core.loader import ModelLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ModelLoaderTests(unittest.TestCase):
    def test_reads_2d_model_and_reports_metrics(self):
        loader = ModelLoader(
            PROJECT_ROOT / "data" / "2D" / "tree2D_Nterm008.vtk"
        )

        self.assertEqual(loader.get_dimension(), 2)
        self.assertEqual(
            loader.get_statistics(),
            {
                "points": 16,
                "lines": 15,
                "segments": 15,
                "attributes": ["raio"],
            },
        )
        self.assertEqual(
            loader.get_radius_range(),
            {
                "min": float(loader.get_radii().min()),
                "max": float(loader.get_radii().max()),
            },
        )

    def test_reads_3d_model(self):
        loader = ModelLoader(
            PROJECT_ROOT / "data" / "3D" / "tree3D_Nterm016.vtk"
        )

        self.assertEqual(loader.get_dimension(), 3)
        self.assertEqual(loader.get_statistics()["segments"], 31)

    def test_counts_edges_inside_polyline_cells(self):
        model = pv.PolyData(
            np.asarray(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [2.0, 0.0, 0.0],
                ]
            ),
            lines=np.asarray([3, 0, 1, 2]),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "polyline.vtk"
            model.save(path)
            loader = ModelLoader(path)

        self.assertEqual(loader.get_statistics()["lines"], 1)
        self.assertEqual(loader.get_statistics()["segments"], 2)
        self.assertIsNone(loader.get_radius_range())


if __name__ == "__main__":
    unittest.main()
