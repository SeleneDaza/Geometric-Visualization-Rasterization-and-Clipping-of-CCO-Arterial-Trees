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
- **RF09 — Preenchimento de região de interesse:** pressione `R` para ativar a
  delimitação de um polígono ROI com cliques no visualizador 2D. Ao finalizar,
  o contorno muda de cor, fica bloqueado para edição, e o preenchimento
  Scanline é animado com as tabelas ET/AET atualizadas a cada linha. Use
  «Limpar ROI» para remover o polígono. Os modos Bresenham (`I`) e ROI (`R`)
  são mutuamente exclusivos: ativar um encerra automaticamente o outro.
- **RF10 — Alternância de antialiasing:** a opção «Ativar antialiasing (FXAA)»
  na barra lateral liga ou desliga a filtragem de subpixel nos visualizadores
  2D e 3D, permitindo comparar as bordas das artérias com e sem suavização.
- **RF11 — Recorte Cohen–Sutherland:** no modo didático 2D, a tecla `C` ou o
  botão «Desenhar janela (C)» ativa o recorte. Arraste sobre a rede para
  definir uma janela retangular; os segmentos visíveis dentro dela são
  recalculados em tempo real pelo algoritmo selecionado.
- **RF12 — Recorte de artérias paramétrico:** no painel didático 2D, selecione
  Cohen–Sutherland ou Liang–Barsky no campo «Algoritmo». A escolha pode ser
  alterada com o recorte ativo, e as artérias são recalculadas imediatamente
  para a mesma janela retangular.
- **RF13 — Alternância de vista do recorte:** pressione `E` ou use o botão
  «Destacar exteriores (E)» para alternar, independentemente do modo de
  desenho, o destaque laranja dos trechos externos à janela. A tecla `C`
  continua controlando apenas o desenho do recorte.
- **RF14 — Recorte Sutherland–Hodgman:** pressione `H` para delimitar uma ROI
  poligonal com vértices reais selecionados nas artérias do modelo CCO e
  recortá-la pela janela retangular definida no modo `C`. Selecione os pontos
  na ordem do contorno, finalize o polígono no painel e arraste com o botão
  direito para atualizar a janela sem sair do modo. A rede completa permanece
  visível; o contorno recortado e os trechos arteriais dentro dele são
  destacados. O HUD informa as quantidades de vértices e a limitação para
  polígonos côncavos.

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
Use «Ativar antialiasing (FXAA)» na barra lateral para alternar a suavização
das artérias em qualquer visualizador.
No modo 2D, pressione `C` ou abra «Modo didático» e selecione «Desenhar
janela (C)»; escolha «Cohen–Sutherland» ou «Liang–Barsky» e arraste sobre o
modelo para recortar os segmentos em tempo real. O algoritmo pode ser trocado
com uma janela já desenhada.
Com a janela definida, pressione `E` para alternar o destaque laranja dos
trechos eliminados/externos; essa tecla não ativa nem desativa o modo de desenho.
Para o Scanline, pressione `R`, marque pelo menos três vértices no modelo e
selecione «Finalizar polígono». O contorno muda de cor e fica bloqueado; use
«Limpar ROI» para recomeçar. Os módulos didáticos são expansíveis e começam
recolhidos; ativar `I` ou `R` expande o módulo correspondente e troca o modo.
Para o recorte de polígonos, defina primeiro a janela com `C` e pressione `H`.
Clique sobre as artérias para selecionar ao menos três vértices reais do CCO,
na ordem do contorno da ROI, e selecione «Finalizar polígono». A janela pode
ser ajustada em tempo real com o botão direito; use «Limpar ROI» para
selecionar outro polígono. A rede completa permanece no fundo e os trechos
contidos na ROI recortada são realçados. A tecla `H` desativa o modo.

## Testes

```powershell
python -m unittest discover -s tests
```
