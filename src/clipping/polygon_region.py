import numpy as np
import pyvista as pv


_TOLERANCE = 1e-10


def _cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def _point_on_segment(point, start, end):
    direction = end - start
    offset = point - start
    scale = max(1.0, float(np.linalg.norm(direction)))
    if abs(_cross(direction, offset)) > _TOLERANCE * scale:
        return False
    projection = float(np.dot(offset, direction))
    length_squared = float(np.dot(direction, direction))
    return -_TOLERANCE <= projection <= length_squared + _TOLERANCE


def _point_in_polygon(point, polygon):
    inside = False
    x, y = point
    for start, end in zip(polygon, polygon[1:] + polygon[:1]):
        if _point_on_segment(point, np.asarray(start), np.asarray(end)):
            return True
        x1, y1 = start
        x2, y2 = end
        if (y1 > y) != (y2 > y):
            crossing_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < crossing_x:
                inside = not inside
    return inside


def clip_segment_to_polygon(start, end, polygon):
    """Recorta um segmento 2D a um polígono simples, incluindo a borda."""
    first = np.asarray(start, dtype=float)
    last = np.asarray(end, dtype=float)
    boundary = [np.asarray(point, dtype=float) for point in polygon]
    if len(boundary) < 3:
        return ()

    direction = last - first
    parameters = [0.0, 1.0]
    for edge_start, edge_end in zip(boundary, boundary[1:] + boundary[:1]):
        edge = edge_end - edge_start
        offset = edge_start - first
        denominator = _cross(direction, edge)
        if abs(denominator) <= _TOLERANCE:
            if abs(_cross(offset, direction)) <= _TOLERANCE:
                length_squared = float(np.dot(direction, direction))
                if length_squared:
                    parameters.extend(
                        float(np.dot(point - first, direction) / length_squared)
                        for point in (edge_start, edge_end)
                    )
            continue

        parameter = _cross(offset, edge) / denominator
        edge_parameter = _cross(offset, direction) / denominator
        if (
            -_TOLERANCE <= parameter <= 1 + _TOLERANCE
            and -_TOLERANCE <= edge_parameter <= 1 + _TOLERANCE
        ):
            parameters.append(min(1.0, max(0.0, parameter)))

    parameters = sorted(
        min(1.0, max(0.0, parameter))
        for parameter in parameters
        if -_TOLERANCE <= parameter <= 1 + _TOLERANCE
    )
    unique_parameters = []
    for parameter in parameters:
        if (
            not unique_parameters
            or parameter - unique_parameters[-1] > _TOLERANCE
        ):
            unique_parameters.append(parameter)

    clipped = []
    for start_parameter, end_parameter in zip(
        unique_parameters, unique_parameters[1:]
    ):
        midpoint = first + ((start_parameter + end_parameter) / 2) * direction
        if _point_in_polygon(midpoint, boundary):
            clipped.append(
                (
                    first + start_parameter * direction,
                    first + end_parameter * direction,
                    start_parameter,
                    end_parameter,
                )
            )
    return tuple(clipped)


def clip_polydata_to_polygon(model, polygon, projected_points=None):
    """Mantém os trechos de artérias dentro de um polígono 2D."""
    boundary = [tuple(float(value) for value in point[:2]) for point in polygon]
    if len(boundary) < 3:
        return pv.PolyData()

    source_points = (
        np.asarray(model.points, dtype=float)
        if projected_points is None
        else np.asarray(projected_points, dtype=float)
    )
    if source_points.shape != np.asarray(model.points).shape:
        raise ValueError(
            "Os pontos projetados devem corresponder aos vértices do modelo."
        )

    clipped_points = []
    connectivity = []
    clipped_radii = []
    has_radii = "raio" in model.cell_data
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
            start = source_points[start_id]
            end = source_points[end_id]
            for _, _, start_parameter, end_parameter in clip_segment_to_polygon(
                start[:2], end[:2], boundary
            ):
                clipped_points.extend(
                    (
                        start + start_parameter * (end - start),
                        start + end_parameter * (end - start),
                    )
                )
                point_index = len(clipped_points) - 2
                connectivity.extend((2, point_index, point_index + 1))
                if has_radii:
                    clipped_radii.append(
                        model.cell_data["raio"][source_cell_id]
                    )

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
