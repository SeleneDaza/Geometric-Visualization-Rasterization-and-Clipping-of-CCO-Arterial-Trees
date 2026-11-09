
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
            "segments": self._count_segments(),
            "attributes": list(self.model.cell_data.keys())
        }

    def _count_segments(self):
        if not isinstance(self.model, pv.PolyData):
            return self.model.n_lines

        connectivity = np.asarray(self.model.lines, dtype=np.int64)
        segments = 0
        offset = 0
        while offset < connectivity.size:
            point_count = int(connectivity[offset])
            segments += max(0, point_count - 1)
            offset += point_count + 1
        return segments

    def get_radii(self):
        return np.asarray(self.model.cell_data["raio"], dtype=float)

    def get_radius_range(self):
        if "raio" not in self.model.cell_data:
            return None

        radii = self.get_radii()
        radii = radii[np.isfinite(radii)]
        if radii.size == 0:
            return None

        return {
            "min": float(radii.min()),
            "max": float(radii.max())
        }
