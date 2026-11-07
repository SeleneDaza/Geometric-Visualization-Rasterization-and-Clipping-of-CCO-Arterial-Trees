
import pyvista as pv


class ModelLoader:

    def __init__(self, file_path):
        self.model = pv.read(file_path)

    def get_model(self):
        return self.model

    def get_dimension(self):
        bounds = self.model.bounds
        z_extent = bounds[5] - bounds[4]
        return 2 if abs(z_extent) < 1e-8 else 3

    def get_statistics(self):
        return {
            "points": self.model.n_points,
            "lines": self.model.n_lines,
            "attributes": list(self.model.cell_data.keys())
        }

    def get_radii(self):
        return self.model.cell_data["raio"]

    def get_radius_range(self):
        if "raio" not in self.model.cell_data:
            return None

        radii = self.get_radii()

        return {
            "min": radii.min(),
            "max": radii.max()
        }
