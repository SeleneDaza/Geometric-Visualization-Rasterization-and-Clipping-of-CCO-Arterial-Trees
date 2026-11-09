from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from rasterization.bresenham import bresenham_line


class RasterizationCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(230)
        self._start = None
        self._end = None
        self._pixels = []

    def set_line(self, start, end, pixels):
        self._start = start
        self._end = end
        self._pixels = pixels
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


class BresenhamModule(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("moduleCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        heading = QLabel("Algoritmo de Bresenham")
        heading.setObjectName("moduleHeading")
        layout.addWidget(heading)
        description = QLabel(
            "Escolha os pontos inicial e final. A visualização destaca "
            "os pixels retornados pelo algoritmo."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

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
            "A implementação atual fornece os pixels selecionados, mas não "
            "registra a evolução da variável de decisão."
        )
        self.decision_info.setWordWrap(True)
        self.decision_info.setObjectName("mutedText")
        layout.addWidget(self.decision_info)

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
        pixels = bresenham_line(*start, *end)
        self.canvas.set_line(start, end, pixels)

        displayed_pixels = pixels[:100]
        pixel_text = ", ".join(str(pixel) for pixel in displayed_pixels)
        if len(pixels) > len(displayed_pixels):
            pixel_text += f", ... ({len(pixels) - len(displayed_pixels)} pixels restantes)"
        self.pixel_output.setText(
            f"{len(pixels)} pixels selecionados:\n{pixel_text}"
        )


class DidacticPanel(QFrame):
    close_requested = Signal()

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

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setMinimumWidth(0)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 20)
        content_layout.setSpacing(14)

        section_title = QLabel("Rasterização de linhas")
        section_title.setObjectName("moduleHeading")
        content_layout.addWidget(section_title)
        content_layout.addWidget(BresenhamModule())

        future_modules = (
            "Preenchimento Scanline",
            "Suavização de serrilhado (Xiaolin Wu / SSAA)",
            "Recorte Cohen–Sutherland",
            "Recorte Liang–Barsky / Cyrus–Beck",
            "Recorte Sutherland–Hodgman",
        )
        for module_name in future_modules:
            content_layout.addWidget(self._future_module(module_name))
        content_layout.addStretch()

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area, stretch=1)

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

    def _request_close(self):
        self.close_requested.emit()
