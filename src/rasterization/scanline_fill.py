from __future__ import annotations

from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class ScanlineEdge:
    y_max: int
    x_intersection: float
    inverse_slope: float


@dataclass(frozen=True)
class ScanlineStep:
    y: int
    active_edges: tuple[ScanlineEdge, ...]
    spans: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class ScanlineFill:
    edge_table: dict[int, tuple[ScanlineEdge, ...]]
    steps: tuple[ScanlineStep, ...]


def scanline_fill(vertices) -> ScanlineFill:
    """Rasteriza un polígono con ET/AET y regla par-impar."""
    points = [(int(x), int(y)) for x, y in vertices]
    if len(points) > 1 and points[0] == points[-1]:
        points.pop()
    if len(set(points)) < 3:
        raise ValueError("El polígono ROI necesita al menos tres vértices distintos.")

    buckets: dict[int, list[ScanlineEdge]] = {}
    for first, second in zip(points, points[1:] + points[:1]):
        if first[1] == second[1]:
            continue
        lower, upper = (
            (first, second) if first[1] < second[1] else (second, first)
        )
        inverse_slope = (upper[0] - lower[0]) / (upper[1] - lower[1])
        buckets.setdefault(lower[1], []).append(
            ScanlineEdge(upper[1], float(lower[0]), inverse_slope)
        )

    if not buckets:
        raise ValueError("El polígono ROI no encierra un área.")

    edge_table = {
        y: tuple(sorted(edges, key=lambda edge: edge.x_intersection))
        for y, edges in buckets.items()
    }
    active_edges: list[ScanlineEdge] = []
    steps = []
    min_y = min(edge_table)
    max_y = max(edge.y_max for edges in edge_table.values() for edge in edges)

    for y in range(min_y, max_y):
        active_edges.extend(edge_table.get(y, ()))
        active_edges = [edge for edge in active_edges if edge.y_max > y]
        active_edges.sort(key=lambda edge: (edge.x_intersection, edge.inverse_slope))

        spans = []
        for index in range(0, len(active_edges) - 1, 2):
            left = ceil(active_edges[index].x_intersection)
            right = ceil(active_edges[index + 1].x_intersection) - 1
            if left <= right:
                spans.append((left, right))

        steps.append(ScanlineStep(y, tuple(active_edges), tuple(spans)))
        active_edges = [
            ScanlineEdge(edge.y_max, edge.x_intersection + edge.inverse_slope,
                         edge.inverse_slope)
            for edge in active_edges
        ]

    if not any(step.spans for step in steps):
        raise ValueError("El polígono ROI no encierra píxeles para rellenar.")

    return ScanlineFill(edge_table, tuple(steps))
