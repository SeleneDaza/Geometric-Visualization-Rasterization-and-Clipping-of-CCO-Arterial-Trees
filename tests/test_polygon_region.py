import unittest

import numpy as np
import pyvista as pv

from src.clipping.polygon_region import (
    clip_polydata_to_polygon,
    clip_segment_to_polygon,
)


class PolygonRegionTests(unittest.TestCase):
    def test_clips_a_segment_to_a_convex_polygon(self):
        polygon = ((0, 0), (4, 0), (4, 4), (0, 4))

        result = clip_segment_to_polygon((-1, 2), (5, 2), polygon)

        self.assertEqual(len(result), 1)
        np.testing.assert_allclose(result[0][0], (0, 2))
        np.testing.assert_allclose(result[0][1], (4, 2))

    def test_clips_a_segment_to_separate_regions_of_a_concave_polygon(self):
        polygon = (
            (0, 0), (5, 0), (5, 5), (4, 5),
            (4, 1), (1, 1), (1, 5), (0, 5),
        )

        result = clip_segment_to_polygon((-1, 3), (6, 3), polygon)

        self.assertEqual(len(result), 2)
        np.testing.assert_allclose(result[0][0], (0, 3))
        np.testing.assert_allclose(result[0][1], (1, 3))
        np.testing.assert_allclose(result[1][0], (4, 3))
        np.testing.assert_allclose(result[1][1], (5, 3))

    def test_clips_arterial_cells_and_preserves_their_radius(self):
        model = pv.PolyData(
            np.asarray(
                ((-1, 2, 0), (5, 2, 0), (2, 2, 0), (3, 2, 0)),
                dtype=float,
            ),
            lines=np.asarray((2, 0, 1, 2, 2, 3), dtype=np.int64),
        )
        model.cell_data["raio"] = np.asarray((0.2, 0.4))

        result = clip_polydata_to_polygon(
            model,
            ((0, 0), (4, 0), (4, 4), (0, 4)),
        )

        self.assertEqual(result.n_cells, 2)
        np.testing.assert_allclose(
            result.points,
            ((0, 2, 0), (4, 2, 0), (2, 2, 0), (3, 2, 0)),
        )
        np.testing.assert_allclose(result.cell_data["raio"], (0.2, 0.4))


if __name__ == "__main__":
    unittest.main()
