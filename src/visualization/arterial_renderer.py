import numpy as np


COLOR_MAPS = {
    "viridis": "viridis",
    "hsv": "hsv",
    "rgb": ["blue", "green", "red"],
}

_WIDTHS = np.linspace(2.0, 7.0, 8)


def set_anti_aliasing(plotter, enabled):
    if enabled:
        plotter.enable_anti_aliasing("fxaa")
    else:
        plotter.disable_anti_aliasing()


def add_arterial_mesh(
    plotter,
    model,
    color_map="viridis",
    show_scalar_bar=True,
):
    if color_map not in COLOR_MAPS:
        raise ValueError(f"Mapa de cores não suportado: {color_map}")

    actors = []
    if "raio" not in model.cell_data:
        actors.append(
            plotter.add_mesh(model, color="#1769aa", line_width=3)
        )
        return actors

    radii = np.asarray(model.cell_data["raio"], dtype=float)
    if radii.size != model.n_cells:
        raise ValueError(
            "O atributo 'raio' deve conter um valor para cada segmento."
        )

    valid = np.isfinite(radii)
    if not valid.any():
        actors.append(
            plotter.add_mesh(model, color="#1769aa", line_width=3)
        )
        return actors

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
        actors.append(
            plotter.add_mesh(
                segments,
                scalars="raio",
                cmap=COLOR_MAPS[color_map],
                clim=color_limits,
                line_width=float(line_width),
                show_scalar_bar=show_scalar_bar and not color_bar_added,
                scalar_bar_args={"title": "Raio dos vasos"},
            )
        )
        color_bar_added = True

    if not valid.all():
        actors.append(
            plotter.add_mesh(
                model.extract_cells(~valid),
                color="#1769aa",
                line_width=3,
            )
        )
    return actors
