from PySide6.QtCore import Qt, Signal
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from rasterization.bresenham import trace_bresenham_line
from rasterization.scanline_fill import scanline_fill


class CollapsibleSection(QFrame):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setObjectName("moduleSection")
        self.setStyleSheet("""
            QFrame#moduleSection {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 9px;
            }
            QToolButton {
                border: none;
                padding: 9px 10px;
                color: #23344d;
                font-size: 14px;
                font-weight: 650;
                text-align: left;
            }
            QToolButton:hover { background: #f5f8fc; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setCheckable(True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(8, 0, 8, 8)
        body_layout.addWidget(content)
        body.hide()
        self.toggle_button.toggled.connect(body.setVisible)
        self.toggle_button.toggled.connect(
            lambda checked: self.toggle_button.setArrowType(
                Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
            )
        )
        layout.addWidget(self.toggle_button)
        layout.addWidget(body)

    def set_expanded(self, expanded):
        self.toggle_button.setChecked(bool(expanded))


class RasterizationCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(230)
        self._start = None
        self._end = None
        self._pixels = []
        self._active_pixel = None

    def set_line(self, start, end, pixels, active_pixel=None):
        self._start = start
        self._end = end
        self._pixels = pixels
        self._active_pixel = active_pixel
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f5f8fc"))

        if self._start is None or self._end is None:
            painter.setPen(QColor("#687386"))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                "Configure os pontos para visualizar a rasterização.",
            )
            return

        x0, y0 = self._start
        x1, y1 = self._end
        min_x, max_x = min(x0, x1) - 1, max(x0, x1) + 1
        min_y, max_y = min(y0, y1) - 1, max(y0, y1) + 1
        columns = max_x - min_x + 1
        rows = max_y - min_y + 1
        cell_size = max(
            1.0,
            min(
                24.0,
                (self.width() - 48) / columns,
                (self.height() - 32) / rows,
            ),
        )
        grid_width = columns * cell_size
        grid_height = rows * cell_size
        left = (self.width() - grid_width) / 2
        top = (self.height() - grid_height) / 2

        def cell_rect(x, y):
            return (
                left + (x - min_x) * cell_size,
                top + (max_y - y) * cell_size,
            )

        if cell_size >= 8:
            painter.setPen(QPen(QColor("#dce3ed"), 1))
            for column in range(columns + 1):
                x = left + column * cell_size
                painter.drawLine(int(x), int(top), int(x), int(top + grid_height))
            for row in range(rows + 1):
                y = top + row * cell_size
                painter.drawLine(int(left), int(y), int(left + grid_width), int(y))

        ideal_pen = QPen(QColor("#ed8b42"), 2, Qt.PenStyle.DashLine)
        painter.setPen(ideal_pen)
        start_x, start_y = cell_rect(x0, y0)
        end_x, end_y = cell_rect(x1, y1)
        painter.drawLine(
            int(start_x + cell_size / 2),
            int(start_y + cell_size / 2),
            int(end_x + cell_size / 2),
            int(end_y + cell_size / 2),
        )

        painter.setPen(QPen(QColor("#1769aa"), 1))
        painter.setBrush(QColor("#58a6e7"))
        for x, y in self._pixels:
            rect_x, rect_y = cell_rect(x, y)
            inset = max(1.0, cell_size * 0.13)
            painter.drawRect(
                int(rect_x + inset),
                int(rect_y + inset),
                max(1, int(cell_size - inset * 2)),
                max(1, int(cell_size - inset * 2)),
            )

        painter.setBrush(QColor("#173b63"))
        for x, y in (self._start, self._end):
            point_x, point_y = cell_rect(x, y)
            radius = max(3.0, cell_size * 0.22)
            painter.drawEllipse(
                int(point_x + cell_size / 2 - radius),
                int(point_y + cell_size / 2 - radius),
                int(radius * 2),
                int(radius * 2),
            )
            painter.drawText(
                int(point_x + cell_size / 2 + radius + 2),
                int(point_y + cell_size / 2),
                f"({x}, {y})",
            )

        if self._active_pixel is not None:
            point_x, point_y = cell_rect(*self._active_pixel)
            radius = max(4.0, cell_size * 0.38)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(QColor("#e5484d"), max(2, int(cell_size * 0.08)))
            )
            painter.drawEllipse(
                int(point_x + cell_size / 2 - radius),
                int(point_y + cell_size / 2 - radius),
                int(radius * 2),
                int(radius * 2),
            )


class BresenhamModule(QFrame):
    inspection_requested = Signal(bool)
    inspection_pixel_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("moduleCard")
        self._inspection_active = False
        self._artery_selection = None
        self._steps = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        heading_row = QHBoxLayout()
        heading = QLabel("Algoritmo de Bresenham")
        heading.setObjectName("moduleHeading")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        self.inspect_button = QPushButton("Inspecionar artéria")
        self.inspect_button.setToolTip(
            "Ativa a seleção de uma artéria no visualizador 2D (I)"
        )
        self.inspect_button.clicked.connect(
            lambda: self.inspection_requested.emit(not self._inspection_active)
        )
        heading_row.addWidget(self.inspect_button)
        layout.addLayout(heading_row)
        description = QLabel(
            "Escolha os pontos inicial e final para acompanhar como o "
            "algoritmo de Bresenham decide quais pixels desenhar."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.selection_details = QLabel()
        self.selection_details.setObjectName("mutedText")
        self.selection_details.setWordWrap(True)
        self.selection_details.hide()
        layout.addWidget(self.selection_details)

        coordinates = QGridLayout()
        self.x0_input = self._coordinate_input(0)
        self.y0_input = self._coordinate_input(0)
        self.x1_input = self._coordinate_input(8)
        self.y1_input = self._coordinate_input(5)
        for index, (label, field) in enumerate((
            ("X inicial", self.x0_input),
            ("Y inicial", self.y0_input),
            ("X final", self.x1_input),
            ("Y final", self.y1_input),
        )):
            row, column = divmod(index, 2)
            coordinates.addWidget(QLabel(label), row * 2, column)
            coordinates.addWidget(field, row * 2 + 1, column)
        layout.addLayout(coordinates)

        self.rasterize_button = QPushButton("Rasterizar linha")
        self.rasterize_button.setObjectName("primaryButton")
        self.rasterize_button.clicked.connect(self.rasterize)
        layout.addWidget(self.rasterize_button)

        self.canvas = RasterizationCanvas()
        layout.addWidget(self.canvas)

        self.pixel_output = QLabel("Os pixels selecionados aparecerão aqui.")
        self.pixel_output.setWordWrap(True)
        self.pixel_output.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.pixel_output)

        self.decision_info = QLabel(
            "O erro e o valor 2 × erro determinam o próximo deslocamento. "
            "Na última iteração, não há nova decisão."
        )
        self.decision_info.setWordWrap(True)
        self.decision_info.setObjectName("mutedText")
        layout.addWidget(self.decision_info)

        self.iteration_table = QTableWidget(0, 4)
        self.iteration_table.setHorizontalHeaderLabels(
            ("Iteração", "Pixel pintado", "Erro", "2 × erro")
        )
        self.iteration_table.verticalHeader().setVisible(False)
        self.iteration_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.iteration_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.iteration_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.iteration_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.iteration_table.setAlternatingRowColors(True)
        self.iteration_table.setMinimumHeight(190)
        self.iteration_table.cellClicked.connect(self._select_iteration)
        layout.addWidget(self.iteration_table)

    @staticmethod
    def _coordinate_input(value):
        field = QSpinBox()
        field.setRange(-10000, 10000)
        field.setValue(value)
        field.setMinimumWidth(80)
        field.setMaximumWidth(140)
        return field

    def rasterize(self):
        start = (self.x0_input.value(), self.y0_input.value())
        end = (self.x1_input.value(), self.y1_input.value())
        self._steps = trace_bresenham_line(*start, *end)
        pixels = [step.pixel for step in self._steps]
        self.canvas.set_line(start, end, pixels)

        displayed_pixels = pixels[:100]
        pixel_text = ", ".join(str(pixel) for pixel in displayed_pixels)
        if len(pixels) > len(displayed_pixels):
            pixel_text += f", ... ({len(pixels) - len(displayed_pixels)} pixels restantes)"
        self.pixel_output.setText(
            f"{len(pixels)} pixels rasterizados:\n{pixel_text}"
        )
        self.iteration_table.setRowCount(len(self._steps))
        for row, step in enumerate(self._steps):
            values = (
                str(step.iteration),
                str(step.pixel),
                str(step.error),
                "-" if step.doubled_error is None else str(step.doubled_error),
            )
            for column, value in enumerate(values):
                self.iteration_table.setItem(
                    row, column, QTableWidgetItem(value)
                )
        self.iteration_table.selectRow(0)
        if self._artery_selection is not None and self._steps:
            self.canvas.set_line(start, end, pixels, self._steps[0].pixel)
            self.inspection_pixel_changed.emit(self._steps[0].pixel)

    def set_inspection_active(self, active):
        self._inspection_active = bool(active)
        self.inspect_button.setText(
            "Cancelar lupa"
            if self._inspection_active else "Inspecionar artéria"
        )
        self.selection_details.setVisible(self._inspection_active)
        self.selection_details.setText(
            "Clique em uma artéria no visualizador 2D para inspecionar seus "
            "pixels. Selecione uma linha para destacá-la no modelo."
            if self._inspection_active else ""
        )
        if not self._inspection_active:
            self.set_artery_selection(None)

    def set_artery_selection(self, selection):
        self._artery_selection = selection
        if selection is None:
            self.inspection_pixel_changed.emit(None)
            if self._inspection_active:
                self.selection_details.setText(
                    "Clique em uma artéria no visualizador 2D para "
                    "inspecionar seus pixels. Selecione uma linha para "
                    "destacá-la no modelo."
                )
            return

        start = selection["start_grid"]
        end = selection["end_grid"]
        self.x0_input.setValue(start[0])
        self.y0_input.setValue(start[1])
        self.x1_input.setValue(end[0])
        self.y1_input.setValue(end[1])
        self.selection_details.setText(
            f"Artéria {selection['cell_id'] + 1} · grade {start} → {end}"
        )
        self.rasterize()

    def _select_iteration(self, row, column):
        if row >= len(self._steps):
            return
        pixel = self._steps[row].pixel
        if self._artery_selection is not None:
            self.canvas.set_line(
                self._artery_selection["start_grid"],
                self._artery_selection["end_grid"],
                [step.pixel for step in self._steps],
                pixel,
            )
            self.inspection_pixel_changed.emit(pixel)


class ArterialClippingModule(QFrame):
    mode_requested = Signal(bool)
    algorithm_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode_active = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        heading_row = QHBoxLayout()
        heading = QLabel("Recorte de artérias")
        heading.setObjectName("moduleHeading")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        self.mode_button = QPushButton("Desenhar janela (C)")
        self.mode_button.setToolTip(
            "Ativa o desenho de uma janela retangular no visualizador 2D (C)"
        )
        self.mode_button.clicked.connect(
            lambda: self.mode_requested.emit(not self._mode_active)
        )
        heading_row.addWidget(self.mode_button)
        layout.addLayout(heading_row)

        algorithm_row = QHBoxLayout()
        algorithm_row.addWidget(QLabel("Algoritmo:"))
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItem(
            "Cohen–Sutherland",
            "cohen_sutherland",
        )
        self.algorithm_selector.addItem("Liang–Barsky", "liang_barsky")
        self.algorithm_selector.setToolTip(
            "Escolha o algoritmo usado para recortar as artérias."
        )
        self.algorithm_selector.currentIndexChanged.connect(
            self._emit_algorithm_changed
        )
        algorithm_row.addWidget(self.algorithm_selector, stretch=1)
        layout.addLayout(algorithm_row)

        description = QLabel(
            "Escolha o algoritmo e arraste sobre a rede para desenhar a "
            "janela retangular. As artérias são recortadas em tempo real."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.status_label = QLabel("Modo de recorte desativado.")
        self.status_label.setObjectName("mutedText")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

    @property
    def algorithm(self):
        return self.algorithm_selector.currentData()

    def _emit_algorithm_changed(self, index):
        self.algorithm_changed.emit(self.algorithm_selector.itemData(index))

    def set_mode_active(self, active):
        self._mode_active = bool(active)
        self.mode_button.setText(
            "Cancelar recorte" if self._mode_active else "Desenhar janela (C)"
        )
        self.status_label.setText(
            "Arraste na visualização para definir a janela retangular."
            if self._mode_active else "Modo de recorte desativado."
        )

    def set_clipping_result(self, result):
        if not self._mode_active or result is None:
            return
        xmin, ymin, xmax, ymax = result["window"]
        self.status_label.setText(
            f"Janela: x [{xmin:.4g}, {xmax:.4g}], "
            f"y [{ymin:.4g}, {ymax:.4g}] · "
            f"{result['segments']} segmentos visíveis."
        )


class ScanlineModule(QFrame):
    mode_requested = Signal(bool)
    roi_finish_requested = Signal()
    roi_clear_requested = Signal()
    fill_step_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("moduleCard")
        self._mode_active = False
        self._roi_finalized = False
        self._vertices = []
        self._steps = ()
        self._step_index = 0
        self._timer = QTimer(self)
        self._timer.setInterval(110)
        self._timer.timeout.connect(self._advance_fill)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        heading_row = QHBoxLayout()
        heading = QLabel("Preenchimento Scanline (ET / AET)")
        heading.setObjectName("moduleHeading")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        self.mode_button = QPushButton("Delimitar ROI (R)")
        self.mode_button.setToolTip(
            "Ativa a delimitação de uma ROI no visualizador 2D (R)"
        )
        self.mode_button.clicked.connect(
            lambda: self.mode_requested.emit(not self._mode_active)
        )
        heading_row.addWidget(self.mode_button)
        layout.addLayout(heading_row)

        description = QLabel(
            "Ative o modo e clique na figura para marcar os vértices. "
            "Finalize o polígono para ver o preenchimento scanline passo a passo."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        controls = QHBoxLayout()
        self.finish_button = QPushButton("Finalizar polígono")
        self.finish_button.clicked.connect(self.roi_finish_requested)
        self.finish_button.setEnabled(False)
        controls.addWidget(self.finish_button)
        self.clear_button = QPushButton("Limpar ROI")
        self.clear_button.clicked.connect(self._request_clear_roi)
        self.clear_button.setEnabled(False)
        controls.addWidget(self.clear_button)
        layout.addLayout(controls)

        self.status_label = QLabel("Modo de delimitación desactivado.")
        self.status_label.setObjectName("mutedText")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        tables = QHBoxLayout()
        self.edge_table = self._make_table(
            ("Y mín.", "Y máx.", "X inicial", "1/m")
        )
        self.active_edge_table = self._make_table(
            ("Y máx.", "X actual", "1/m")
        )
        tables.addWidget(self.edge_table)
        tables.addWidget(self.active_edge_table)
        layout.addLayout(tables)

        self._edge_rows = []

    @staticmethod
    def _make_table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setAlternatingRowColors(True)
        table.setMinimumHeight(100)
        return table

    def set_mode_active(self, active):
        active = bool(active)
        if active == self._mode_active:
            return
        self._mode_active = active
        self._roi_finalized = False
        self._timer.stop()
        self.fill_step_changed.emit(None)
        self._vertices.clear()
        self._steps = ()
        self.edge_table.setRowCount(0)
        self.active_edge_table.setRowCount(0)
        self.mode_button.setText(
            "Cancelar ROI" if active else "Delimitar ROI (R)"
        )
        self.finish_button.setEnabled(False)
        self.clear_button.setEnabled(active)
        self.status_label.setText(
            "Clique em pelo menos três pontos da figura e finalize o polígono."
            if active else "Modo de delimitación desactivado."
        )

    def add_roi_vertex(self, vertex):
        if not self._mode_active or self._roi_finalized:
            return
        self._vertices.append(vertex)
        self.finish_button.setEnabled(len(self._vertices) >= 3)
        self.status_label.setText(
            f"Vértices marcados: {len(self._vertices)}. "
            "Añade más o finaliza el polígono."
        )

    def set_roi_vertices(self, vertices):
        if not self._mode_active:
            return
        self._vertices = list(vertices)
        self.finish_button.setEnabled(len(self._vertices) >= 3)
        self.status_label.setText(
            f"Vértices marcados: {len(self._vertices)}."
        )

    def start_fill(self, vertices):
        if not self._mode_active:
            return
        self._timer.stop()
        self._roi_finalized = True
        self.finish_button.setEnabled(False)
        self.clear_button.setEnabled(True)
        try:
            result = scanline_fill(vertex["pixel"] for vertex in vertices)
        except ValueError as error:
            self.status_label.setText(str(error))
            return

        self._vertices = list(vertices)
        self._steps = result.steps
        self._step_index = 0
        self.edge_table.setRowCount(0)
        self._edge_rows.clear()
        for y_min, edges in sorted(result.edge_table.items()):
            for edge in edges:
                self._add_row(
                    self.edge_table,
                    (y_min, edge.y_max, f"{edge.x_intersection:.2f}",
                     f"{edge.inverse_slope:.3f}"),
                )
                self._edge_rows.append((y_min, edge))
        self.fill_step_changed.emit(None)
        self.status_label.setText(
            f"ET: {len(self._edge_rows)} arestas · "
            f"{len(self._steps)} linhas de varredura."
        )
        self._advance_fill()
        self.status_label.setText(
            "ROI finalizada e bloqueada. Use «Limpar ROI» para desenhar "
            "outro polígono."
        )
        if self._step_index < len(self._steps):
            self._timer.start()

    def _advance_fill(self):
        if self._step_index >= len(self._steps):
            self._timer.stop()
            return

        step = self._steps[self._step_index]
        self.active_edge_table.setRowCount(0)
        for edge in step.active_edges:
            self._add_row(
                self.active_edge_table,
                (edge.y_max, f"{edge.x_intersection:.2f}",
                 f"{edge.inverse_slope:.3f}"),
            )
        self.fill_step_changed.emit({
            "y": step.y,
            "spans": step.spans,
        })
        self.status_label.setText(
            f"Scanline y={step.y} · AET: {len(step.active_edges)} arestas · "
            f"intervalos preenchidos: {step.spans or 'nenhum'}"
        )
        self._step_index += 1
        if self._step_index == len(self._steps):
            self._timer.stop()
            self.status_label.setText(
                f"Preenchimento concluído · {len(self._steps)} scanlines."
            )

    @staticmethod
    def _add_row(table, values):
        row = table.rowCount()
        table.insertRow(row)
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(str(value)))

    def clear_roi(self):
        if not self._mode_active:
            return
        self._timer.stop()
        self._vertices.clear()
        self._roi_finalized = False
        self._steps = ()
        self._step_index = 0
        self.edge_table.setRowCount(0)
        self.active_edge_table.setRowCount(0)
        self._edge_rows.clear()
        self.fill_step_changed.emit(None)
        self.finish_button.setEnabled(False)
        self.clear_button.setEnabled(self._mode_active)
        self.status_label.setText(
            "ROI limpa. Clique na figura para marcar os vértices."
        )
        self.roi_clear_requested.emit()

    def _request_clear_roi(self):
        self.clear_roi()


class DidacticPanel(QFrame):
    close_requested = Signal()
    roi_finish_requested = Signal()
    roi_clear_requested = Signal()
    clipping_mode_requested = Signal(bool)
    fill_step_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("didacticPanel")
        self.setStyleSheet("""
            QFrame#didacticPanel { background: #ffffff; }
            QLabel { color: #23344d; }
            QLabel#panelTitle { font-size: 19px; font-weight: 700; }
            QLabel#moduleHeading { font-size: 15px; font-weight: 650; }
            QLabel#mutedText { color: #687386; }
            QFrame#moduleCard {
                background: #f7f9fc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 10px;
                border: 1px solid #d5deea;
                border-radius: 7px;
                background: #ffffff;
                color: #23344d;
            }
            QPushButton:hover { background: #edf4fb; }
            QPushButton#primaryButton {
                background: #1769aa;
                border: none;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover { background: #12588f; }
            QSpinBox {
                min-height: 30px;
                border: 1px solid #d5deea;
                border-radius: 6px;
                padding: 0 4px;
            }
            QComboBox {
                min-height: 30px;
                border: 1px solid #d5deea;
                border-radius: 6px;
                padding: 0 6px;
                background: #ffffff;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(
            "background: #f5f8fc; border-bottom: 1px solid #e2e8f0;"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 12, 12, 12)
        title = QLabel("Modo didático")
        title.setObjectName("panelTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.close_button = QPushButton("Fechar painel")
        self.close_button.clicked.connect(self._request_close)
        header_layout.addWidget(self.close_button)
        root_layout.addWidget(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setMinimumWidth(0)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 20)
        content_layout.setSpacing(14)

        self.bresenham_module = BresenhamModule()
        self.bresenham_section = self._collapsible_section(
            "Bresenham",
            self.bresenham_module,
        )
        content_layout.addWidget(self.bresenham_section)

        self.scanline_module = ScanlineModule()
        self.scanline_module.roi_finish_requested.connect(
            self._request_roi_finish
        )
        self.scanline_module.roi_clear_requested.connect(
            self._request_roi_clear
        )
        self.scanline_module.fill_step_changed.connect(
            self._forward_fill_step
        )
        self.scanline_section = self._collapsible_section(
            "Região de interesse (ROI)",
            self.scanline_module,
        )
        content_layout.addWidget(self.scanline_section)

        self.clipping_module = ArterialClippingModule()
        self.clipping_module.mode_requested.connect(
            self._request_clipping_mode
        )
        self.clipping_section = self._collapsible_section(
            "Recorte de artérias",
            self.clipping_module,
        )
        content_layout.addWidget(self.clipping_section)

        future_modules = (
            "Recorte Sutherland–Hodgman",
        )
        for module_name in future_modules:
            section = self._collapsible_section(
                module_name,
                self._future_module(module_name),
            )
            content_layout.addWidget(section)
        self.sections = {
            "bresenham": self.bresenham_section,
            "scanline": self.scanline_section,
            "clipping": self.clipping_section,
        }
        content_layout.addStretch()

        self.scroll_area.setWidget(content)
        root_layout.addWidget(self.scroll_area, stretch=1)

    @staticmethod
    def _future_module(name):
        card = QFrame()
        card.setObjectName("moduleCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        title = QLabel(name)
        title.setObjectName("moduleHeading")
        title.setWordWrap(True)
        layout.addWidget(title)
        status = QLabel("Ainda não implementado")
        status.setObjectName("mutedText")
        status.setWordWrap(True)
        layout.addWidget(status)
        return card

    @staticmethod
    def _collapsible_section(title, content):
        return CollapsibleSection(title, content)

    def set_module_expanded(self, name, expanded):
        section = self.sections[name]
        section.set_expanded(expanded)
        if expanded:
            self.scroll_area.ensureWidgetVisible(section)

    def _request_close(self):
        self.close_requested.emit()

    def _request_roi_finish(self):
        self.roi_finish_requested.emit()

    def _request_roi_clear(self):
        self.roi_clear_requested.emit()

    def _request_clipping_mode(self, active):
        self.clipping_mode_requested.emit(active)

    def _forward_fill_step(self, step):
        self.fill_step_changed.emit(step)
