from pyvistaqt import QtInteractor


class Viewer2D(QtInteractor):

    def __init__(self, parent=None):
        super().__init__(parent)

    def show_model(self, model):
        self.clear()

        has_radius = "raio" in model.cell_data

        self.add_mesh(
            model,
            scalars="raio" if has_radius else None,
            cmap="viridis",
            line_width=3
        )

        if has_radius:
            self.add_scalar_bar(
                title="Raio dos vasos"
            )

        self.view_xy()
        self.reset_camera()
        self.render()
