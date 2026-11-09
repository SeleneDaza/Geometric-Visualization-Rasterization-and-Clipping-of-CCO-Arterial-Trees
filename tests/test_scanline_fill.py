import unittest

from src.rasterization.scanline_fill import scanline_fill


class ScanlineFillTests(unittest.TestCase):
    def test_fills_a_rectangle_using_half_open_scanlines(self):
        result = scanline_fill(((1, 1), (5, 1), (5, 4), (1, 4)))

        self.assertEqual(list(result.edge_table), [1])
        self.assertEqual([step.y for step in result.steps], [1, 2, 3])
        self.assertTrue(
            all(step.spans == ((1, 4),) for step in result.steps)
        )
        self.assertEqual(
            [len(step.active_edges) for step in result.steps],
            [2, 2, 2],
        )

    def test_handles_sloped_edges_and_omits_horizontal_edges_from_et(self):
        result = scanline_fill(((1, 1), (5, 3), (3, 6), (0, 4)))

        self.assertEqual(set(result.edge_table), {1, 3, 4})
        self.assertTrue(all(step.active_edges for step in result.steps))
        self.assertTrue(any(step.spans for step in result.steps))

    def test_rejects_polygons_without_area_or_enough_vertices(self):
        for vertices in (
            ((0, 0), (1, 1)),
            ((0, 0), (2, 2), (4, 4)),
            ((0, 0), (1, 0), (2, 0)),
        ):
            with self.subTest(vertices=vertices):
                with self.assertRaises(ValueError):
                    scanline_fill(vertices)


if __name__ == "__main__":
    unittest.main()
