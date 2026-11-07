
from core.loader import ModelLoader
from visualization.viewer_3d import Viewer3D


# Ruta del modelo
file_path = "data/3D/tree3D_Nterm064.vtk"


# Carregar o modelo
loader = ModelLoader(file_path)

# Recuperar informações
model = loader.get_model()
statistics = loader.get_statistics()
radius_range = loader.get_radius_range()


# Exibir informações
print("Quantidade de pontos:", statistics["points"])
print("Quantidade de linhas:", statistics["lines"])

print("Atributos dos segmentos:", statistics["attributes"])

print("Raio mínimo:", radius_range["min"])
print("Raio máximo:", radius_range["max"])


# Visualizar modelo
viewer = Viewer3D(model)
viewer.show_model()
