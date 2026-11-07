# Geometric-Visualization-Rasterization-and-Clipping-of-CCO-Arterial-Trees

-final structure: sugested

Grupo_XX/
│
├── src/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── loader.py
│   │   ├── model.py
│   │   └── statistics.py
│   │
│   ├── visualization/
│   │   ├── viewer_3d.py
│   │   ├── camera.py
│   │   └── transformations.py
│   │
│   ├── rasterization/
│   │   ├── bresenham.py
│   │   ├── scanline.py
│   │   └── antialiasing.py
│   │
│   ├── clipping/
│   │   ├── cohen_sutherland.py
│   │   ├── liang_barsky.py
│   │   └── sutherland_hodgman.py
│   │
│   └── interface/
│       └── controls.py
│
├── data/
│   ├── 3D/
│   │   └── tree3D_Nterm064.vtk
│   └── 2D/
│       └── archivos_vtk_2D.vtk
│
├── report/
│   ├── relatorio.tex
│   ├── relatorio.pdf
│   └── figures/
│
├── presentation/
│   ├── apresentacao.tex
│   └── apresentacao.pdf
│
└── README.md