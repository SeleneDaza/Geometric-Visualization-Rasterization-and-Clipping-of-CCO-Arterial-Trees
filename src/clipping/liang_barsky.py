import numpy as np

from ._polydata import (
    clip_polydata as _clip_polydata,
    clip_polydata_outside as _clip_polydata_outside,
)


def clip_segment(start, end, window):
    """Clip a 2D segment to (xmin, ymin, xmax, ymax) using Liang–Barsky."""
    xmin, ymin, xmax, ymax = window
    if xmin > xmax or ymin > ymax:
        raise ValueError("A janela de recorte deve ter limites ordenados.")

    x0, y0 = (float(value) for value in start[:2])
    x1, y1 = (float(value) for value in end[:2])
    if not np.isfinite((x0, y0, x1, y1, xmin, ymin, xmax, ymax)).all():
        raise ValueError("As coordenadas do recorte devem ser finitas.")

    delta_x = x1 - x0
    delta_y = y1 - y0
    entering = 0.0
    leaving = 1.0

    for direction, distance in (
        (-delta_x, x0 - xmin),
        (delta_x, xmax - x0),
        (-delta_y, y0 - ymin),
        (delta_y, ymax - y0),
    ):
        if direction == 0:
            if distance < 0:
                return None
            continue

        parameter = distance / direction
        if direction < 0:
            entering = max(entering, parameter)
        else:
            leaving = min(leaving, parameter)
        if entering > leaving:
            return None

    return (
        (x0 + entering * delta_x, y0 + entering * delta_y),
        (x0 + leaving * delta_x, y0 + leaving * delta_y),
    )


def clip_polydata(model, window):
    """Return a line mesh containing the portions inside a rectangular window."""
    return _clip_polydata(model, window, clip_segment)


def clip_polydata_outside(model, window):
    """Return a line mesh containing the portions outside a rectangular window."""
    return _clip_polydata_outside(model, window, clip_segment)
