import numpy as np


COLOR_MAPS = {
    "viridis": "viridis",
    "hsv": "hsv",
    "rgb": ["blue", "green", "red"],
}

_WIDTHS = np.linspace(2.0, 7.0, 8)


def add_arterial_mesh(plotter, model, color_map="viridis"):
    if color_map not in COLOR_MAPS:
        raise ValueError(f"Mapa de color no soportado: {color_map}")

    if "raio" not in model.cell_data:
        plotter.add_mesh(model, color="#1769aa", line_width=3)
        return

    radii = np.asarray(model.cell_data["raio"], dtype=float)
    if radii.size != model.n_cells:
        raise ValueError(
            "El atributo 'raio' debe contener un valor por segmento."
        )

    valid = np.isfinite(radii)
    if not valid.any():
        plotter.add_mesh(model, color="#1769aa", line_width=3)
        return

    finite_radii = radii[valid]
    minimum = float(finite_radii.min())
    maximum = float(finite_radii.max())
    spread = maximum - minimum
    normalized = np.full(radii.shape, 0.5)
    if spread > 0:
        normalized[valid] = (finite_radii - minimum) / spread

    bins = np.minimum((normalized * len(_WIDTHS)).astype(int), len(_WIDTHS) - 1)
    color_limits = (minimum, maximum)
    if minimum == maximum:
        padding = max(abs(minimum) * 1e-6, 1e-12)
        color_limits = (minimum - padding, maximum + padding)

    color_bar_added = False
    for bin_index, line_width in enumerate(_WIDTHS):
        selected = valid & (bins == bin_index)
        if not selected.any():
            continue

        segments = model.extract_cells(selected)
        plotter.add_mesh(
            segments,
            scalars="raio",
            cmap=COLOR_MAPS[color_map],
            clim=color_limits,
            line_width=float(line_width),
            show_scalar_bar=not color_bar_added,
            scalar_bar_args={"title": "Radio de los vasos"},
        )
        color_bar_added = True

    if not valid.all():
        plotter.add_mesh(
            model.extract_cells(~valid),
            color="#1769aa",
            line_width=3,
        )
