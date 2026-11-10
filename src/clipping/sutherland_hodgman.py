from math import isfinite


def _is_inside(point, edge, value):
    x, y = point
    if edge == "LEFT":
        return x >= value
    if edge == "RIGHT":
        return x <= value
    if edge == "BOTTOM":
        return y >= value
    return y <= value


def _intersection(start, end, edge, value):
    x1, y1 = start
    x2, y2 = end
    if edge in ("LEFT", "RIGHT"):
        t = (value - x1) / (x2 - x1)
        t = min(1.0, max(0.0, t))
        return value, y1 + t * (y2 - y1)

    t = (value - y1) / (y2 - y1)
    t = min(1.0, max(0.0, t))
    return x1 + t * (x2 - x1), value


def _remove_adjacent_duplicates(points):
    result = []
    for point in points:
        if not result or point != result[-1]:
            result.append(point)
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    return result


def _has_area(points):
    twice_area = sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
    )
    return twice_area != 0


def clip_polygon(subject_polygon, window):
    """Recorta um polígono 2D ordenado para (xmin, ymin, xmax, ymax).

    A sequência de saída é implicitamente fechada: o primeiro vértice não é
    repetido no final. A janela retangular deve ter largura e altura positivas.
    """
    try:
        xmin, ymin, xmax, ymax = (float(value) for value in window)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(
            "A janela deve conter (xmin, ymin, xmax, ymax)."
        ) from error

    if not all(isfinite(value) for value in (xmin, ymin, xmax, ymax)):
        raise ValueError("As coordenadas da janela devem ser finitas.")
    if xmin >= xmax or ymin >= ymax:
        raise ValueError("A janela deve ter largura e altura positivas.")

    points = []
    try:
        for point in subject_polygon:
            x, y = (float(value) for value in point[:2])
            if not isfinite(x) or not isfinite(y):
                raise ValueError("As coordenadas do polígono devem ser finitas.")
            points.append((x, y))
    except (TypeError, ValueError, IndexError, OverflowError) as error:
        raise ValueError(
            "O polígono deve ser uma sequência de pontos 2D finitos."
        ) from error

    points = _remove_adjacent_duplicates(points)
    if len(set(points)) < 3 or not _has_area(points):
        raise ValueError("O polígono ROI precisa ter área e três vértices distintos.")

    edges = (
        ("LEFT", xmin),
        ("RIGHT", xmax),
        ("BOTTOM", ymin),
        ("TOP", ymax),
    )
    for edge, value in edges:
        if not points:
            break
        output = []
        previous = points[-1]
        previous_inside = _is_inside(previous, edge, value)
        for current in points:
            current_inside = _is_inside(current, edge, value)
            if current_inside:
                if not previous_inside:
                    output.append(_intersection(previous, current, edge, value))
                output.append(current)
            elif previous_inside:
                output.append(_intersection(previous, current, edge, value))
            previous = current
            previous_inside = current_inside
        points = _remove_adjacent_duplicates(output)

    if len(set(points)) < 3 or not _has_area(points):
        return []
    return points
