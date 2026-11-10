import numpy as np
import pyvista as pv


def clip_polydata(model, window, clip_segment):
    """Clip each artery segment and preserve its source radius."""
    clipped_points = []
    connectivity = []
    clipped_radii = []
    has_radii = "raio" in model.cell_data
    source_points = np.asarray(model.points, dtype=float)
    source_lines = np.asarray(model.lines, dtype=np.int64)
    line_offset = 0
    line_cell_id = 0

    while line_offset < source_lines.size:
        point_count = int(source_lines[line_offset])
        point_ids = source_lines[line_offset + 1:line_offset + 1 + point_count]
        source_cell_id = int(model.n_verts) + line_cell_id
        for index in range(point_count - 1):
            start_id = int(point_ids[index])
            end_id = int(point_ids[index + 1])
            clipped = clip_segment(
                source_points[start_id],
                source_points[end_id],
                window,
            )
            if clipped is None:
                continue

            clipped_start, clipped_end = clipped
            z_start = source_points[start_id, 2]
            z_end = source_points[end_id, 2]
            clipped_points.extend(
                (
                    (clipped_start[0], clipped_start[1], z_start),
                    (clipped_end[0], clipped_end[1], z_end),
                )
            )
            point_index = len(clipped_points) - 2
            connectivity.extend((2, point_index, point_index + 1))
            if has_radii:
                clipped_radii.append(model.cell_data["raio"][source_cell_id])

        line_offset += point_count + 1
        line_cell_id += 1

    if clipped_points:
        clipped_model = pv.PolyData(
            np.asarray(clipped_points, dtype=float),
            lines=np.asarray(connectivity, dtype=np.int64),
        )
    else:
        clipped_model = pv.PolyData()
    if has_radii:
        clipped_model.cell_data["raio"] = np.asarray(clipped_radii)
    return clipped_model
