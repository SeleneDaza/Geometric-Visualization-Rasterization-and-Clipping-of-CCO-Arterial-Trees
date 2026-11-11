# Geometric Visualization, Rasterization and Clipping of CCO Arterial Trees

Aplicação interativa desenvolvida em Python para a visualização, rasterização, transformação afim e recorte de árvores arteriais sintéticas 2D e 3D geradas pelo algoritmo *Constrained Constructive Optimization* (CCO). Trabalho Prático 1 (TP1) da disciplina de Computação Gráfica.

---

## 👥 Integrantes do Grupo
* Arian Selene Daza Ochoa
* Bianca Barreto Leme
* Karina Miyu Kinukawa

---

## 🛠️ Tecnologia Gráfica e Bibliotecas Utilizadas
* **Linguagem:** Python 3.10+
* **Interface Gráfica (GUI):** PyQt5 / PySide2
* **Manipulação de Dados Geométricos / VTK:** `vtk` ou parsers dedicados para leitura de malhas estruturadas/poligonais.
* **Processamento Numérico:** `numpy` para representação matricial de transformações afins (homogêneas) e cálculos vetoriais.

---

## 📂 Estrutura Final do Repositório

```text
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
│       └── tree2D_Nterm032.vtk
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
```

---

## ⚙️ Dependências e Instalação

Certifique-se de ter o Python instalado em seu ambiente. Instale as dependências executando:

```bash
pip install -r requirements.txt
```
*(Principais dependências: `numpy`, `PyQt5`, `vtk`)*

---

## 🚀 Como Executar o Programa

1. Navegue até a pasta raiz do projeto.
2. Execute o script principal através do terminal:

```bash
python src/main.py
```

---

## 📂 Localização dos Arquivos VTK
Os modelos de teste fornecidos pelo laboratório devem estar localizados nos diretórios padrão:
* Árvores 2D: `data/2D/` (ex: `tree2D_Nterm008.vtk`, `tree2D_Nterm032.vtk`, etc.)
* Árvores 3D: `data/3D/` (ex: `tree3D_Nterm064.vtk`, `tree3D_Nterm256.vtk`, etc.)

---

## ⌨️ Controles de Teclado e Mouse

* **Arrastar com botão esquerdo do mouse:** Rotaciona a visualização 3D / Panorâmica 2D.
* **Scroll do Mouse (Rodinha):** Ampliar / Reduzir zoom ($\text{Zoom In} / \text{Zoom Out}$).
* **Teclas `R` / `r`:** Reseta a câmera e a matriz de transformação para o estado original.
* **Teclas `1`, `2`, `3`:** Alterna entre os modos de visualização (Rasterização Bresenham, Contínuo Vetorial, Preenchimento por Scanline).
* **Tecla `C`:** Ativa/Desativa o modo de recorte interativo (Cohen-Sutherland / Liang-Barsky).
* **Tecla `Esc`:** Fecha a aplicação.

---

## 🧪 Roteiro Mínimo para Teste das Funcionalidades

1. **Carregamento de Dados:** Abra o programa, acesse o menu superior e selecione um arquivo `.vtk` na pasta `data/2D/` ou `data/3D/`.
2. **Transformações Afins:** Utilize os sliders na interface lateral para aplicar translação $(t_x, t_y)$, escala ($s$) e rotação ($\theta$) em tempo real na árvore arterial.
3. **Rasterização:** Pressione o atalho correspondente para alternar a renderização dos segmentos utilizando o algoritmo de linha de Bresenham.
4. **Recorte (Clipping):** Defina uma janela de recorte retangular na tela e alterne entre os algoritmos Cohen-Sutherland e Liang-Barsky para observar o comportamento do recorte dos ramos vasculares.

---

## 🔍 Funcionalidades: Implementação Própria vs. Bibliotecas

* **Implementados pelo Grupo (Lógica Core de Computação Gráfica):**
  * Algoritmo de Linha de Bresenham (geração de pixels a partir de pontos extremos).
  * Preenchimento de regiões poligonais por *Scanline*.
  * Algoritmo de recorte de segmentos Cohen-Sutherland (com codificação de região por *outcodes*).
  * Algoritmo de recorte paramétrico de Liang-Barsky.
  * Algoritmo de recorte de polígonos Sutherland-Hodgman.
  * Composição de matrizes de transformação afim em coordenadas homogêneas (2D e 3D).

* **Realizados com Auxílio de Bibliotecas:**
  * Carregamento de arquivos estruturados e parsing básico do formato VTK (`vtk`).
  * Construção de elementos de interface gráfica de usuário (janelas, botões e sliders via `PyQt5`).