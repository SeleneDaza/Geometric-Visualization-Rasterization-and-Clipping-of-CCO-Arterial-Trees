from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BresenhamStep:
    iteration: int
    pixel: tuple[int, int]
    error: int
    doubled_error: int | None


def trace_bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[BresenhamStep]:
    """Retorna cada pixel desenhado e os valores usados na decisão de Bresenham."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx - dy
    current_x, current_y = x0, y0
    steps = []

    while True:
        at_endpoint = current_x == x1 and current_y == y1
        if at_endpoint:
            steps.append(
                BresenhamStep(
                    iteration=len(steps) + 1,
                    pixel=(current_x, current_y),
                    error=error,
                    doubled_error=None,
                )
            )
            break

        doubled_error = 2 * error
        steps.append(
            BresenhamStep(
                iteration=len(steps) + 1,
                pixel=(current_x, current_y),
                error=error,
                doubled_error=doubled_error,
            )
        )

        if doubled_error > -dy:
            error -= dy
            current_x += sx
        if doubled_error < dx:
            error += dx
            current_y += sy

    return steps


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Retorna os pixels da linha rasterizada pelo algoritmo de Bresenham."""
    return [step.pixel for step in trace_bresenham_line(x0, y0, x1, y1)]
