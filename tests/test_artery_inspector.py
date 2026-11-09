import unittest

import numpy as np
import pyvista as pv

from src.visualization.artery_inspector import (
    closest_cell_segment,
    original_cell_id,
    raster_grid_endpoints,
)


class ArteryInspectorTests(unittest.TestCase):
    def setUp(self):
        points = np.array(
            (
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (2.0, 1.0, 0.0),
                (3.0, 1.0, 0.0),
            )
        )
        lines = np.array((2, 0, 1, 2, 1, 2, 2, 2, 3))
        self.model = pv.PolyData(points, lines=lines)

    def test_maps_extracted_cells_to_original_cell_id(self):
        extracted = self.model.extract_cells((False, True, True))

        class Mapper:
            def GetInput(self):
                return extracted

        class Actor:
            def GetMapper(self):
                return Mapper()

        class Picker:
            def GetCellId(self):
                return 0

            def GetActor(self):
                return Actor()

        self.assertEqual(original_cell_id(Picker()), 1)

    def test_selects_nearest_edge_within_a_polyline_cell(self):
        segment = closest_cell_segment(self.model, 1, (1.8, 0.2, 0.0))

        self.assertEqual(segment, ((1.0, 0.0, 0.0), (2.0, 1.0, 0.0)))
        self.assertIsNone(closest_cell_segment(self.model, 9, (0, 0, 0)))

    def test_maps_segment_to_a_zoomed_integer_pixel_grid(self):
        class Renderer:
            def SetWorldPoint(self, x, y, z, _w):
                self.point = (x, y, z)

            def WorldToDisplay(self):
                self.display_point = (self.point[0] * 100, self.point[1] * 100, 0)

            def GetDisplayPoint(self):
                return self.display_point

        start_grid, end_grid = raster_grid_endpoints(
            Renderer(), (2, 3, 0), (1, 5, 0)
        )

        self.assertEqual(start_grid, (0, 0))
        self.assertEqual(end_grid, (-20, 40))


if __name__ == "__main__":
    unittest.main()
