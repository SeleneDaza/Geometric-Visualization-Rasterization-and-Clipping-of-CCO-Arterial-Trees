# Geometric Visualization, Rasterization and Clipping of CCO Arterial Trees

Aplicación de escritorio para cargar y visualizar árboles arteriales CCO en
formato VTK, en 2D o 3D.

## Requisitos funcionales

- **RF01 — Carga y parseo:** PyVista carga archivos `.vtk`; la dimensión
  geométrica se determina a partir de sus puntos.
- **RF02 — Métricas:** se muestran puntos/vértices, segmentos geométricos y el
  rango del atributo de radio `raio`, cuando está disponible.
- **RF03 — Primitivas:** las redes se dibujan como segmentos de línea en los
  visualizadores 2D y 3D.
- **RF04 — Color y grosor:** el radio de cada segmento controla su color y
  grosor. El selector permite elegir Viridis, HSV o RGB (azul-verde-rojo).

## Ejecución

Instala las dependencias de `requirements.txt` y ejecuta desde la raíz:

```powershell
python src\main.py
```

Los modelos de ejemplo están en `data\2D` y `data\3D`. También se pueden añadir
archivos `.vtk` o carpetas desde la aplicación.

## Pruebas

```powershell
python -m unittest discover -s tests
```
