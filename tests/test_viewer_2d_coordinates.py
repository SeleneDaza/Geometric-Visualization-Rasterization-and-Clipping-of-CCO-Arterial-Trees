import unittest
import sys
from pathlib import Path

from PySide6.QtCore import QPoint

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from visualization.viewer_2d import _qt_to_vtk_display_position


class Viewer2DCoordinateTests(unittest.TestCase):
    def test_scales_mouse_position_to_vtk_device_pixels(self):
        self.assertEqual(
            _qt_to_vtk_display_position(QPoint(120, 80), 600, 1.5),
            (180, 778),
        )

    def test_preserves_mouse_position_at_native_scale(self):
        self.assertEqual(
            _qt_to_vtk_display_position(QPoint(120, 80), 600, 1.0),
            (120, 519),
        )


if __name__ == "__main__":
    unittest.main()
