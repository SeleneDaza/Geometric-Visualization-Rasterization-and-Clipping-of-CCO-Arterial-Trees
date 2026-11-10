import numpy as np

from ._polydata import clip_polydata as _clip_polydata


_LEFT = 1
_RIGHT = 2
_BOTTOM = 4
_TOP = 8


def clip_segment(start, end, window):
    """Clip a 2D segment to (xmin, ymin, xmax, ymax)."""
    xmin, ymin, xmax, ymax = window
    if xmin > xmax or ymin > ymax:
        raise ValueError("A janela de recorte deve ter limites ordenados.")

    x0, y0 = (float(value) for value in start[:2])
    x1, y1 = (float(value) for value in end[:2])
    if not np.isfinite((x0, y0, x1, y1, xmin, ymin, xmax, ymax)).all():
        raise ValueError("As coordenadas do recorte devem ser finitas.")

    def region_code(x, y):
        code = 0
        if x < xmin:
            code |= _LEFT
        elif x > xmax:
            code |= _RIGHT
        if y < ymin:
            code |= _BOTTOM
        elif y > ymax:
            code |= _TOP
        return code

    code0 = region_code(x0, y0)
    code1 = region_code(x1, y1)

    while True:
        if not (code0 | code1):
            return (x0, y0), (x1, y1)
        if code0 & code1:
            return None

        outside = code0 or code1
        if outside & _TOP:
            x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
            y = ymax
        elif outside & _BOTTOM:
            x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
            y = ymin
        elif outside & _RIGHT:
            y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
            x = xmax
        else:
            y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
            x = xmin

        if outside == code0:
            x0, y0 = x, y
            code0 = region_code(x0, y0)
        else:
            x1, y1 = x, y
            code1 = region_code(x1, y1)


def clip_polydata(model, window):
    """Return a line mesh containing the portions inside a rectangular window."""
    return _clip_polydata(model, window, clip_segment)
