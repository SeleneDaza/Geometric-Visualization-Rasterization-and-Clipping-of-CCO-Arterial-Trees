import unittest

import numpy as np
import pyvista as pv

from src.clipping.cohen_sutherland import clip_polydata, clip_segment


class CohenSutherlandTests(unittest.TestCase):
    def test_accepts_segment_inside_window(self):
        segment = ((1, 1), (3, 4))

        self.assertEqual(
            clip_segment(*segment, (0, 0, 5, 5)),
            segment,
        )

    def test_clips_segment_crossing_left_and_right_edges(self):
        clipped = clip_segment((-2, 2), (8, 2), (0, 0, 5, 5))

        self.assertEqual(clipped, ((0, 2.0), (5, 2.0)))

    def test_clips_segment_crossing_top_and_bottom_edges(self):
        clipped = clip_segment((2, -2), (2, 8), (0, 0, 5, 5))

        self.assertEqual(clipped, ((2.0, 0), (2.0, 5)))

    def test_rejects_segment_outside_in_a_shared_region(self):
        self.assertIsNone(
            clip_segment((-2, 1), (-1, 4), (0, 0, 5, 5))
        )

    def test_accepts_segment_on_window_boundary(self):
        self.assertEqual(
            clip_segment((0, 1), (0, 4), (0, 0, 5, 5)),
            ((0.0, 1.0), (0.0, 4.0)),
        )

    def test_rejects_unordered_window(self):
        with self.assertRaises(ValueError):
            clip_segment((0, 0), (1, 1), (2, 0, 1, 1))

    def test_clips_polydata_and_preserves_radius_per_source_segment(self):
        model = pv.PolyData(
            np.asarray(
                [
                    [-2.0, 2.0, 0.0],
                    [2.0, 2.0, 0.0],
                    [8.0, 2.0, 0.0],
                    [8.0, 8.0, 0.0],
                ]
            ),
            lines=np.asarray([2, 0, 1, 2, 2, 3]),
        )
        model.cell_data["raio"] = np.asarray([0.1, 0.2])

        clipped = clip_polydata(model, (0, 0, 5, 5))

        self.assertEqual(clipped.n_cells, 1)
        np.testing.assert_allclose(
            clipped.points,
            [[0, 2, 0], [2, 2, 0]],
        )
        np.testing.assert_allclose(clipped.cell_data["raio"], [0.1])

    def test_clips_each_edge_of_a_polyline(self):
        model = pv.PolyData(
            np.asarray(
                [
                    [-2.0, 2.0, 0.0],
                    [2.0, 2.0, 0.0],
                    [8.0, 2.0, 0.0],
                ]
            ),
            lines=np.asarray([3, 0, 1, 2]),
        )
        model.cell_data["raio"] = np.asarray([0.3])

        clipped = clip_polydata(model, (0, 0, 5, 5))

        self.assertEqual(clipped.n_cells, 2)
        np.testing.assert_allclose(
            clipped.points,
            [[0, 2, 0], [2, 2, 0], [2, 2, 0], [5, 2, 0]],
        )
        np.testing.assert_allclose(clipped.cell_data["raio"], [0.3, 0.3])


if __name__ == "__main__":
    unittest.main()
