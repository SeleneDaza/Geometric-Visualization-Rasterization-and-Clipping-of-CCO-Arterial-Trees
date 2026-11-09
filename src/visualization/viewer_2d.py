from pyvistaqt import QtInteractor

from visualization.arterial_renderer import add_arterial_mesh


class Viewer2D(QtInteractor):

    def __init__(self, parent=None):
        super().__init__(parent)

    def show_model(self, model, color_map="viridis"):
        self.clear()
        add_arterial_mesh(self, model, color_map)
        self.view_xy()
        self.reset_camera()
        self.render()
