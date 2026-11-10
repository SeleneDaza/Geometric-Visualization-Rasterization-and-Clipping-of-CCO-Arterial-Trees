import unittest

import numpy as np
import pyvista as pv

from src.clipping.liang_barsky import clip_polydata, clip_segment


class LiangBarskyTests(unittest.TestCase):
    def test_accepts_segment_inside_window(self):
        segment = ((1, 1), (3, 4))

        self.assertEqual(
            clip_segment(*segment, (0, 0, 5, 5)),
            segment,
        )

    def test_clips_segment_crossing_window(self):
        clipped = clip_segment((-2, 2), (8, 2), (0, 0, 5, 5))

        self.assertEqual(clipped, ((0, 2), (5, 2)))

    def test_clips_diagonal_segment(self):
        clipped = clip_segment((-1, -1), (6, 6), (0, 0, 5, 5))

        np.testing.assert_allclose(clipped, ((0, 0), (5, 5)))

    def test_rejects_segment_parallel_and_outside_window(self):
        self.assertIsNone(
            clip_segment((-2, 6), (8, 6), (0, 0, 5, 5))
        )

    def test_accepts_segment_on_window_boundary(self):
        self.assertEqual(
            clip_segment((0, 1), (0, 4), (0, 0, 5, 5)),
            ((0, 1), (0, 4)),
        )

    def test_rejects_unordered_window(self):
        with self.assertRaises(ValueError):
            clip_segment((0, 0), (1, 1), (2, 0, 1, 1))

    def test_clips_polydata_and_preserves_radius(self):
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
        np.testing.assert_allclose(clipped.points, [[0, 2, 0], [2, 2, 0]])
        np.testing.assert_allclose(clipped.cell_data["raio"], [0.1])


if __name__ == "__main__":
    unittest.main()
