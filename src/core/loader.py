
import pyvista as pv


class ModelLoader:

    def __init__(self, file_path):
        self.model = pv.read(file_path)

    def get_model(self):
        return self.model

    def get_statistics(self):
        return {
            "points": self.model.n_points,
            "lines": self.model.n_lines,
            "attributes": list(self.model.cell_data.keys())
        }

    def get_radii(self):
        return self.model.cell_data["raio"]

    def get_radius_range(self):
        radii = self.get_radii()

        return {
            "min": radii.min(),
            "max": radii.max()
        }
