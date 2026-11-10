from __future__ import annotations

import numpy as np


def original_cell_id(picker) -> int | None:
    cell_id = int(picker.GetCellId())
    if cell_id < 0:
        return None

    actor = picker.GetActor()
    mapper = actor.GetMapper() if actor is not None else None
    dataset = mapper.GetInput() if mapper is not None else None
    if dataset is None:
        return cell_id

    original_ids = dataset.GetCellData().GetArray("vtkOriginalCellIds")
    if original_ids is None:
        return cell_id
    if cell_id >= original_ids.GetNumberOfTuples():
        return None
    return int(original_ids.GetTuple1(cell_id))


def closest_cell_segment(model, cell_id: int, pick_position):
    if cell_id < 0 or cell_id >= model.n_cells:
        return None

    point_ids = np.asarray(model.get_cell(cell_id).point_ids, dtype=int)
    if point_ids.size < 2:
        return None

    points = np.asarray(model.points, dtype=float)[point_ids]
    pick = np.asarray(pick_position, dtype=float)
    best_segment = None
    best_distance = float("inf")

    for start, end in zip(points, points[1:]):
        direction = end - start
        length_squared = float(np.dot(direction, direction))
        amount = (
            0.0
            if length_squared == 0
            else float(np.clip(np.dot(pick - start, direction) / length_squared, 0, 1))
        )
        closest = start + amount * direction
        distance = float(np.dot(pick - closest, pick - closest))
        if distance < best_distance:
            best_distance = distance
            best_segment = (tuple(start), tuple(end))

    return best_segment


def closest_cell_vertex(model, cell_id: int, pick_position):
    if cell_id < 0 or cell_id >= model.n_cells:
        return None

    point_ids = np.asarray(model.get_cell(cell_id).point_ids, dtype=int)
    if point_ids.size == 0:
        return None

    points = np.asarray(model.points, dtype=float)[point_ids]
    pick = np.asarray(pick_position, dtype=float)
    distances = np.sum((points - pick) ** 2, axis=1)
    index = int(np.argmin(distances))
    point_id = int(point_ids[index])
    return point_id, tuple(points[index])


def raster_grid_endpoints(renderer, start, end, max_grid_span: int = 40):
    if max_grid_span < 1:
        raise ValueError("A escala da grade deve ser positiva.")

    display_points = []
    for point in (start, end):
        renderer.SetWorldPoint(*point, 1.0)
        renderer.WorldToDisplay()
        display_points.append(np.asarray(renderer.GetDisplayPoint()[:2]))

    delta = display_points[1] - display_points[0]
    span = float(np.max(np.abs(delta)))
    if span == 0:
        return (0, 0), (0, 0)

    scale = max_grid_span / span
    end_pixel = tuple(int(round(value * scale)) for value in delta)
    return (0, 0), end_pixel
