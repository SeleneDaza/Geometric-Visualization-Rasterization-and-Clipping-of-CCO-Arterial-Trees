import numpy as np


def translation_matrix(x, y, z):
    offset = np.asarray([x, y, z], dtype=float)
    if not np.isfinite(offset).all():
        raise ValueError("A translação deve conter valores finitos.")

    matrix = np.eye(4)
    matrix[:3, 3] = offset
    return matrix


def rotation_matrix(axis, angle_degrees, center):
    axes = {
        "x": np.asarray([1.0, 0.0, 0.0]),
        "y": np.asarray([0.0, 1.0, 0.0]),
        "z": np.asarray([0.0, 0.0, 1.0]),
    }
    if axis not in axes:
        raise ValueError(f"Eixo de rotação não suportado: {axis}")
    if not np.isfinite(angle_degrees):
        raise ValueError("O ângulo de rotação deve ser finito.")

    x, y, z = axes[axis]
    angle = np.deg2rad(angle_degrees)
    cosine = np.cos(angle)
    sine = np.sin(angle)
    rotation = np.asarray(
        [
            [cosine + x * x * (1 - cosine),
             x * y * (1 - cosine) - z * sine,
             x * z * (1 - cosine) + y * sine],
            [y * x * (1 - cosine) + z * sine,
             cosine + y * y * (1 - cosine),
             y * z * (1 - cosine) - x * sine],
            [z * x * (1 - cosine) - y * sine,
             z * y * (1 - cosine) + x * sine,
             cosine + z * z * (1 - cosine)],
        ]
    )
    return _around_center(rotation, center)


def scale_matrix(factor, center):
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError("O fator de escala deve ser finito e maior que zero.")
    return _around_center(np.eye(3) * factor, center)


def _around_center(linear_transform, center):
    center = np.asarray(center, dtype=float)
    if center.shape != (3,) or not np.isfinite(center).all():
        raise ValueError("O centro da transformação deve ser um ponto 3D finito.")

    to_origin = np.eye(4)
    to_origin[:3, 3] = -center
    transform = np.eye(4)
    transform[:3, :3] = linear_transform
    to_center = np.eye(4)
    to_center[:3, 3] = center
    return to_center @ transform @ to_origin
