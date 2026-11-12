import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from interface.main_window import MainWindow


class ThicknessControlTests(unittest.TestCase):
    def _window(self, dimension):
        model = object()
        viewer_2d = Mock()
        viewer_3d = Mock()
        window = SimpleNamespace(
            loader=SimpleNamespace(get_model=lambda: model),
            _current_dimension=dimension,
            color_map_selector=SimpleNamespace(
                currentData=lambda: "viridis"
            ),
            viewer_2d=viewer_2d,
            viewer_3d=viewer_3d,
        )
        return window, model, viewer_2d, viewer_3d

    def test_slider_updates_2d_viewer(self):
        window, model, viewer_2d, viewer_3d = self._window(2)

        MainWindow._update_thickness_scale(window, 150)

        viewer_2d.show_model.assert_called_once_with(
            model,
            color_map="viridis",
            thickness_scale=1.5,
        )
        viewer_3d.set_thickness_scale.assert_not_called()

    def test_slider_updates_3d_viewer(self):
        window, _, viewer_2d, viewer_3d = self._window(3)

        MainWindow._update_thickness_scale(window, 150)

        viewer_2d.show_model.assert_not_called()
        viewer_3d.set_thickness_scale.assert_called_once_with(1.5)


if __name__ == "__main__":
    unittest.main()
