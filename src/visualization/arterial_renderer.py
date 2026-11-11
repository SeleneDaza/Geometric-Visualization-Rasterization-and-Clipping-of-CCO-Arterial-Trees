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
    thickness_scale=1.0,  # Parâmetro de escala (0.0 a 1.0)
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

    # --- DIFERENÇA DE GROSSURA DINÂMICA ---
    uniform_widths = np.full(len(_WIDTHS), 3.0)
    full_widths = np.linspace(1.0, 12.0, len(_WIDTHS))
    active_widths = uniform_widths * (1.0 - thickness_scale) + full_widths * thickness_scale
    # --------------------------------------

    for bin_index, line_width in enumerate(active_widths):
        selected = valid & (bins == bin_index)
        if not selected.any():
            continue

        segments = model.extract_cells(selected)
        actor = plotter.add_mesh(
            segments,
            scalars="raio",
            cmap=COLOR_MAPS[color_map],
            clim=color_limits,
            line_width=float(line_width),
            show_scalar_bar=False,
        )
        actors.append(actor)

    if show_scalar_bar and valid.any() and actors:
        plotter.add_scalar_bar(
            title="Raio dos vasos",
            mapper=actors[0].mapper,
            interactive=False,
        )

    if not valid.all():
        actors.append(
            plotter.add_mesh(
                model.extract_cells(~valid),
                color="#1769aa",
                line_width=3,
            )
        )
    return actors