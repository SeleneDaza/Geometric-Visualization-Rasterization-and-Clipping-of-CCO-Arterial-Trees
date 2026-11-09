import unittest

import numpy as np

from src.visualization.affine_transform import (
    rotation_matrix,
    scale_matrix,
    translation_matrix,
)


class AffineTransformTests(unittest.TestCase):
    def test_translation_moves_a_point(self):
        matrix = translation_matrix(2, -3, 4)

        np.testing.assert_allclose(
            matrix @ np.asarray([1, 2, 3, 1]),
            [3, -1, 7, 1],
        )

    def test_rotation_keeps_the_center_fixed(self):
        center = np.asarray([2, 3, 4])
        matrix = rotation_matrix("z", 90, center)

        np.testing.assert_allclose(matrix @ [*center, 1], [*center, 1])
        np.testing.assert_allclose(
            matrix @ [3, 3, 4, 1],
            [2, 4, 4, 1],
            atol=1e-12,
        )

    def test_scale_keeps_the_center_fixed(self):
        center = np.asarray([2, 3, 4])
        matrix = scale_matrix(2, center)

        np.testing.assert_allclose(matrix @ [*center, 1], [*center, 1])
        np.testing.assert_allclose(matrix @ [3, 3, 4, 1], [4, 3, 4, 1])

    def test_invalid_rotation_axis_and_scale_are_rejected(self):
        with self.assertRaises(ValueError):
            rotation_matrix("w", 15, [0, 0, 0])
        with self.assertRaises(ValueError):
            scale_matrix(0, [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
