import unittest

from src.clipping.sutherland_hodgman import clip_polygon


class SutherlandHodgmanTests(unittest.TestCase):
    def test_clips_a_polygon_against_all_four_window_edges(self):
        polygon = ((-2, 1), (5, 1), (5, 5), (-2, 5))

        result = clip_polygon(polygon, (0, 0, 4, 4))

        self.assertEqual(
            set(result),
            {(0.0, 1.0), (4.0, 1.0), (4.0, 4.0), (0.0, 4.0)},
        )
        self.assertNotEqual(result[0], result[-1])

    def test_preserves_an_inside_polygon_and_removes_repeated_closure(self):
        polygon = ((1, 1), (3, 1), (3, 3), (1, 3), (1, 1))

        self.assertEqual(
            clip_polygon(polygon, (0, 0, 4, 4)),
            [(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)],
        )

    def test_returns_empty_for_a_polygon_outside_the_window(self):
        self.assertEqual(
            clip_polygon(((-3, -3), (-2, -3), (-2, -2), (-3, -2)),
                         (0, 0, 4, 4)),
            [],
        )

    def test_clips_a_polygon_that_encloses_the_entire_window(self):
        result = clip_polygon(
            ((-2, -2), (6, -2), (6, 6), (-2, 6)),
            (0, 0, 4, 4),
        )

        self.assertEqual(
            set(result),
            {(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)},
        )

    def test_handles_edges_and_corners_on_the_window_boundary(self):
        polygon = ((0, 0), (4, 0), (4, 4), (0, 4))

        self.assertEqual(len(clip_polygon(polygon, (0, 0, 4, 4))), 4)

    def test_returns_empty_when_the_intersection_has_no_area(self):
        polygon = ((-1, 1), (1, 1), (1, 3), (-1, 3))

        self.assertEqual(clip_polygon(polygon, (1, 0, 4, 4)), [])

    def test_interpolates_sloped_edge_intersections(self):
        result = clip_polygon(((-1, 1), (2, 4), (4, 1)), (0, 0, 3, 5))

        self.assertIn((0.0, 2.0), result)
        self.assertIn((3.0, 2.5), result)

    def test_rejects_non_finite_coordinates_and_invalid_polygons(self):
        with self.assertRaises(ValueError):
            clip_polygon(((0, 0), (1, 1), (float("nan"), 2)), (0, 0, 4, 4))
        with self.assertRaises(ValueError):
            clip_polygon(((0, 0), (1, 1), (2, 2)), (0, 0, 4, 4))
        with self.assertRaises(ValueError):
            clip_polygon(((0, 0), (1, 0), (1, 1)), (2, 0, 1, 4))


if __name__ == "__main__":
    unittest.main()
