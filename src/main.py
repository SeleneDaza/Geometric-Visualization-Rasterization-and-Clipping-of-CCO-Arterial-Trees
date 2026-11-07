import pyvista as pv

# Carrega o modelo
modelo = pv.read("data/3D/tree3D_Nterm064.vtk")

# Exibe informações
print("Quantidade de pontos:", modelo.n_points)
print("Quantidade de linhas:", modelo.n_lines)

# Exibe os atributos disponíveis
print("Atributos dos segmentos:", modelo.cell_data.keys())

# Recupera os raios
raios = modelo.cell_data["raio"]

print("Raio mínimo:", raios.min())
print("Raio máximo:", raios.max())

plotter = pv.Plotter()

plotter.add_mesh(
    modelo,
    scalars="raio",
    cmap="viridis",
    line_width=3
)

plotter.add_scalar_bar(title="Raio dos vasos")

plotter.show()