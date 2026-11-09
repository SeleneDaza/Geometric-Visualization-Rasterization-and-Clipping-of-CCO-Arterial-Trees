from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from interface.didactic_panel import DidacticPanel
from interface.transform_panel import TransformPanel


class VisualizationSurface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_2d = False
        self._panel_open = False

        self._content_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._content_splitter.setHandleWidth(6)
        self._content_splitter.setChildrenCollapsible(False)

        self.viewer_container = QStackedWidget()
        self.viewer_container.setMinimumWidth(180)
        self._content_splitter.addWidget(self.viewer_container)

        self.viewer_title = QLabel(self)
        self.viewer_title.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 220);
                color: #23344d;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 600;
            }
        """)
        self.viewer_title.hide()

        self.didactic_panel = DidacticPanel(self)
        self.didactic_panel.setMinimumWidth(230)
        self._content_splitter.addWidget(self.didactic_panel)
        self.transform_panel = TransformPanel(self)
        self._content_splitter.addWidget(self.transform_panel)
        self._content_splitter.setStretchFactor(0, 1)
        self._content_splitter.setStretchFactor(1, 0)
        self.didactic_panel.close_requested.connect(self.close_didactic_panel)
        self.transform_panel.close_requested.connect(
            self.close_transform_panel
        )
        self.didactic_panel.hide()
        self.transform_panel.hide()

        self.didactic_button = QPushButton("Modo didático", self)
        self.didactic_button.setFixedSize(144, 38)
        self.didactic_button.setStyleSheet("""
            QPushButton {
                background: #1769aa;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background: #12588f; }
        """)
        self.didactic_button.clicked.connect(self.toggle_didactic_panel)
        self.didactic_button.hide()

        self.transform_button = QPushButton("Transformar cena", self)
        self.transform_button.setFixedSize(168, 38)
        self.transform_button.setStyleSheet("""
            QPushButton {
                background: #1769aa;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background: #12588f; }
        """)
        self.transform_button.clicked.connect(self.toggle_transform_panel)
        self.transform_button.hide()

        surface_layout = QHBoxLayout(self)
        surface_layout.setContentsMargins(0, 0, 0, 0)
        surface_layout.addWidget(self._content_splitter)

        self.loading_overlay = QFrame(self)
        self.loading_overlay.setStyleSheet(
            "QFrame { background: rgba(245, 248, 252, 235); }"
            "QLabel { color: #23344d; font-size: 15px; font-weight: 600; }"
        )
        loading_layout = QVBoxLayout(self.loading_overlay)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label = QLabel("Carregando aplicação...")
        self.loading_label.setWordWrap(True)
        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)
        self.loading_indicator.setFixedWidth(220)
        self.loading_indicator.setTextVisible(False)
        loading_layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(self.loading_indicator)
        self.loading_overlay.setGeometry(self.rect())
        self.loading_overlay.show()

    def set_viewers(self, viewer_2d, viewer_3d):
        self.viewer_container.addWidget(viewer_2d)
        self.viewer_container.addWidget(viewer_3d)
        self.viewer_container.setCurrentWidget(viewer_2d)

    def set_model_dimension(self, dimension):
        self._is_2d = dimension == 2
        if self._panel_open:
            self.didactic_panel.hide()
            self.transform_panel.hide()
            self._panel_open = False
        self.viewer_title.setText(
            "Visualizador 2D" if self._is_2d else "Visualizador 3D"
        )
        self.viewer_title.show()
        self.didactic_button.setVisible(self._is_2d)
        self.transform_button.setVisible(not self._is_2d)

    def show_loading(self, message):
        self.loading_label.setText(message)
        self.loading_indicator.show()
        self.loading_overlay.setGeometry(self.rect())
        self.loading_overlay.raise_()
        self.loading_overlay.show()

    def hide_loading(self):
        self.loading_overlay.hide()

    def show_initialization_error(self, message):
        self.loading_label.setText(message)
        self.loading_indicator.hide()
        self.loading_overlay.setGeometry(self.rect())
        self.loading_overlay.raise_()
        self.loading_overlay.show()

    def toggle_didactic_panel(self):
        if self._panel_open:
            self.close_didactic_panel()
        else:
            self.open_didactic_panel()

    def open_didactic_panel(self):
        if not self._is_2d:
            return
        self._panel_open = True
        self.didactic_button.hide()
        self.didactic_panel.show()
        panel_width = min(
            max(int(self.width() * 0.38), self.didactic_panel.minimumWidth()),
            360,
            max(self.didactic_panel.minimumWidth(), self.width() - 180),
        )
        self._content_splitter.setSizes(
            [max(180, self.width() - panel_width), panel_width, 0]
        )

    def close_didactic_panel(self):
        if not self._panel_open:
            return
        self._panel_open = False
        self.didactic_panel.hide()
        self.didactic_button.setVisible(self._is_2d)

    def toggle_transform_panel(self):
        if self._panel_open:
            self.close_transform_panel()
        else:
            self.open_transform_panel()

    def open_transform_panel(self):
        if self._is_2d:
            return
        self._panel_open = True
        self.transform_button.hide()
        self.transform_panel.show()
        panel_width = min(
            max(int(self.width() * 0.38), self.transform_panel.minimumWidth()),
            360,
            max(self.transform_panel.minimumWidth(), self.width() - 180),
        )
        self._content_splitter.setSizes(
            [max(180, self.width() - panel_width), 0, panel_width]
        )

    def close_transform_panel(self):
        if not self._panel_open:
            return
        self._panel_open = False
        self.transform_panel.hide()
        self.transform_button.setVisible(not self._is_2d)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setGeometry(self.rect())
        self.didactic_button.move(
            self.width() - self.didactic_button.width() - 18, 16
        )
        self.viewer_title.move(16, 16)
        self.transform_button.move(
            self.width() - self.transform_button.width() - 18, 16
        )
        if self.loading_overlay.isVisible():
            self.loading_overlay.raise_()
        else:
            self.viewer_title.raise_()
            if self._is_2d:
                self.didactic_button.raise_()
            else:
                self.transform_button.raise_()
