import unittest

from src.rasterization.bresenham import (
    bresenham_line,
    trace_bresenham_line,
)


class BresenhamTests(unittest.TestCase):
    def test_trace_matches_pixels_for_all_line_directions(self):
        lines = (
            ((0, 0), (8, 5)),
            ((0, 0), (5, 8)),
            ((0, 0), (-8, 5)),
            ((0, 0), (8, -5)),
            ((3, 7), (3, -2)),
            ((-4, 2), (5, 2)),
            ((2, 2), (2, 2)),
        )

        for start, end in lines:
            with self.subTest(start=start, end=end):
                steps = trace_bresenham_line(*start, *end)
                pixels = bresenham_line(*start, *end)
                dx = abs(end[0] - start[0])
                dy = abs(end[1] - start[1])

                self.assertEqual(pixels, [step.pixel for step in steps])
                self.assertEqual(pixels[0], start)
                self.assertEqual(pixels[-1], end)
                self.assertEqual(len(pixels), max(dx, dy) + 1)
                self.assertEqual(
                    [step.iteration for step in steps],
                    list(range(1, len(steps) + 1)),
                )

                for first, second in zip(pixels, pixels[1:]):
                    self.assertLessEqual(abs(second[0] - first[0]), 1)
                    self.assertLessEqual(abs(second[1] - first[1]), 1)
                    self.assertNotEqual(first, second)

    def test_final_iteration_has_no_next_decision(self):
        steps = trace_bresenham_line(1, 1, 4, 3)

        self.assertIsNone(steps[-1].doubled_error)
        self.assertTrue(
            all(step.doubled_error is not None for step in steps[:-1])
        )


if __name__ == "__main__":
    unittest.main()
