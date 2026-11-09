
import numpy as np
import pyvista as pv


class ModelLoader:

    def __init__(self, file_path):
        self.model = pv.read(file_path)

    def get_model(self):
        return self.model

    def get_dimension(self):
        points = np.asarray(self.model.points, dtype=float)
        if points.size == 0:
            return 2

        centered_points = points - points.mean(axis=0)
        singular_values = np.linalg.svd(centered_points, compute_uv=False)
        if singular_values.size == 0:
            return 2

        tolerance = max(singular_values[0] * 1e-8, 1e-12)
        geometric_rank = np.count_nonzero(singular_values > tolerance)
        return 3 if geometric_rank >= 3 else 2

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
