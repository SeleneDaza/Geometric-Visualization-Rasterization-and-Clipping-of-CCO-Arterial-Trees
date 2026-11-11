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


def clip_polydata_outside(model, window, clip_segment):
    """Return the portions of each artery segment outside the window."""
    outside_points = []
    connectivity = []
    outside_radii = []
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
            start = source_points[int(point_ids[index])]
            end = source_points[int(point_ids[index + 1])]
            clipped = clip_segment(start, end, window)
            if clipped is None:
                outside_segments = ((start, end),)
            else:
                clipped_start, clipped_end = clipped
                delta = end[:2] - start[:2]
                denominator = float(np.dot(delta, delta))
                if denominator == 0:
                    outside_segments = ()
                else:
                    start_parameter = float(
                        np.dot(np.asarray(clipped_start) - start[:2], delta)
                        / denominator
                    )
                    end_parameter = float(
                        np.dot(np.asarray(clipped_end) - start[:2], delta)
                        / denominator
                    )
                    segments = []
                    if start_parameter > 0:
                        segments.append(
                            (
                                start,
                                start + start_parameter * (end - start),
                            )
                        )
                    if end_parameter < 1:
                        segments.append(
                            (
                                start + end_parameter * (end - start),
                                end,
                            )
                        )
                    outside_segments = segments

            for outside_start, outside_end in outside_segments:
                outside_points.extend((outside_start, outside_end))
                point_index = len(outside_points) - 2
                connectivity.extend((2, point_index, point_index + 1))
                if has_radii:
                    outside_radii.append(
                        model.cell_data["raio"][source_cell_id]
                    )

        line_offset += point_count + 1
        line_cell_id += 1

    if outside_points:
        outside_model = pv.PolyData(
            np.asarray(outside_points, dtype=float),
            lines=np.asarray(connectivity, dtype=np.int64),
        )
    else:
        outside_model = pv.PolyData()
    if has_radii:
        outside_model.cell_data["raio"] = np.asarray(outside_radii)
    return outside_model
