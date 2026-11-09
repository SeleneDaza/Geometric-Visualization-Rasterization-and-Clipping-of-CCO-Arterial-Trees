# Visualização Geométrica, Rasterização e Recorte de Árvores Arteriais CCO

Aplicativo para carregar e visualizar árvores arteriais CCO em formato VTK,
em 2D ou 3D.

## Requisitos funcionais

- **RF01 — Carregamento e análise:** o PyVista carrega arquivos `.vtk`; a
  dimensão geométrica é determinada a partir dos pontos.
- **RF02 — Métricas:** são exibidos o número de pontos/vértices, segmentos
  geométricos e o intervalo do atributo de raio `raio`, quando disponível.
- **RF03 — Primitivas:** as redes são desenhadas como segmentos de linha nos
  visualizadores 2D e 3D.
- **RF04 — Cor e espessura:** o raio de cada segmento controla sua cor e
  espessura. É possível escolher os mapas Viridis, HSV ou RGB (azul-verde-
  vermelho).
- **RF05 — Transformações afins interativas:** no modo 3D, o painel lateral
  permite transladar, rotacionar e redimensionar o modelo com controles
  deslizantes. As setas com `Alt` também deslocam a cena.
- **RF06 — Controle do observador:** o controle deslizante da câmera permite
  escolher entre as vistas isométrica, superior, frontal e lateral. O mouse
  também permite orbitar, deslocar e aproximar ou afastar a câmera.
- **RF07 — Projeções:** a opção «Projeção ortográfica» alterna entre projeção
  ortográfica e perspectiva; a perspectiva é usada inicialmente.
- **RF08 — Inspetor/lupa de artéria:** no visualizador 2D, pressione `I` para
  abrir o módulo de Bresenham e ativar ou desativar a seleção de um segmento
  CCO. A grade de pixels e a tabela `pₖ` aparecem no módulo; ao escolher um
  passo, a artéria e o pixel em análise ficam destacados na figura. O módulo
  também permite informar manualmente os extremos de uma reta.

## Execução

Instale as dependências de `requirements.txt` e execute a partir da raiz:

```powershell
python src\main.py
```

Os modelos de exemplo estão em `data\2D` e `data\3D`. Também é possível
adicionar arquivos `.vtk` ou pastas pelo aplicativo. No visualizador 2D,
pressione `I` para abrir o módulo de Bresenham e ativar a lupa; clique em uma
artéria e selecione uma linha da tabela para destacar seu pixel. Pressione `I`
novamente ou «Fechar painel» para sair do modo.

## Testes

```powershell
python -m unittest discover -s tests
```
