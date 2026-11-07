
import pyvista as pv


class Viewer3D:

    def __init__(self, model):
        self.model = model
        self.plotter = pv.Plotter()

    def show_model(self):

        self.plotter.add_mesh(
            self.model,
            scalars="raio",
            cmap="viridis",
            line_width=3
        )

        self.plotter.add_scalar_bar(
            title="Raio dos vasos"
        )

        self.plotter.show()
