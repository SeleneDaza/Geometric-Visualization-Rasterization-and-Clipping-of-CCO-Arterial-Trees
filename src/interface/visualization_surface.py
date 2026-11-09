from PySide6.QtGui import QAction
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
        self._active_interaction = None
        self._viewer_2d = None

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

        bresenham_module = self.didactic_panel.bresenham_module
        bresenham_module.inspection_requested.connect(
            self.set_artery_inspection_active
        )
        bresenham_module.inspection_pixel_changed.connect(
            self._set_inspection_pixel
        )
        scanline_module = self.didactic_panel.scanline_module
        scanline_module.mode_requested.connect(self.set_roi_mode_active)
        scanline_module.fill_step_changed.connect(
            self._set_scanline_fill_step
        )
        self.didactic_panel.roi_finish_requested.connect(
            self._finalize_scanline_roi
        )
        self.didactic_panel.roi_clear_requested.connect(
            self._clear_scanline_roi
        )

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

        self.inspector_shortcut = QAction("Inspecionar artéria", self)
        self.inspector_shortcut.setShortcut("I")
        self.inspector_shortcut.setShortcutContext(
            Qt.ShortcutContext.WindowShortcut
        )
        self.inspector_shortcut.triggered.connect(
            self.toggle_artery_inspector
        )
        self.inspector_shortcut.setEnabled(False)
        self.addAction(self.inspector_shortcut)
        self.roi_shortcut = QAction("Delimitar ROI", self)
        self.roi_shortcut.setShortcut("R")
        self.roi_shortcut.setShortcutContext(
            Qt.ShortcutContext.WindowShortcut
        )
        self.roi_shortcut.triggered.connect(self.toggle_roi_mode)
        self.roi_shortcut.setEnabled(False)
        self.addAction(self.roi_shortcut)

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
        self._viewer_2d = viewer_2d
        viewer_2d.artery_selected.connect(
            self.didactic_panel.bresenham_module.set_artery_selection
        )
        viewer_2d.artery_selected.connect(
            viewer_2d.set_inspection_selection
        )
        viewer_2d.roi_vertex_added.connect(
            self.didactic_panel.scanline_module.add_roi_vertex
        )
        viewer_2d.roi_finalized.connect(
            self.didactic_panel.scanline_module.start_fill
        )

    def set_model_dimension(self, dimension):
        if self._active_interaction is not None:
            self._set_dynamic_mode(None)
        self._is_2d = dimension == 2
        self.inspector_shortcut.setEnabled(self._is_2d)
        self.roi_shortcut.setEnabled(self._is_2d)
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
        self._set_dynamic_mode(None)
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

    def toggle_artery_inspector(self):
        if not self._is_2d or self._viewer_2d is None:
            return
        self.set_artery_inspection_active(
            self._active_interaction != "bresenham"
        )

    def set_artery_inspection_active(self, active):
        active = bool(active)
        if active:
            self._set_dynamic_mode("bresenham")
        elif self._active_interaction == "bresenham":
            self._set_dynamic_mode(None)

    def toggle_roi_mode(self):
        if not self._is_2d or self._viewer_2d is None:
            return
        self.set_roi_mode_active(self._active_interaction != "scanline")

    def set_roi_mode_active(self, active):
        active = bool(active)
        if active:
            self._set_dynamic_mode("scanline")
        elif self._active_interaction == "scanline":
            self._set_dynamic_mode(None)

    def _set_dynamic_mode(self, mode):
        if mode == self._active_interaction:
            return
        if mode is not None and (
            not self._is_2d or self._viewer_2d is None
        ):
            return

        previous = self._active_interaction
        if previous == "bresenham":
            self._viewer_2d.set_artery_inspection_enabled(False)
            self._viewer_2d.set_inspection_selection(None)
            self.didactic_panel.bresenham_module.set_inspection_active(False)
        elif previous == "scanline":
            self._viewer_2d.set_scanline_roi_enabled(False)
            self.didactic_panel.scanline_module.set_mode_active(False)

        self._active_interaction = mode
        if mode is None:
            return

        self.open_didactic_panel()
        self.didactic_panel.set_module_expanded(mode, True)
        if mode == "bresenham":
            self._viewer_2d.set_artery_inspection_enabled(True)
            self.didactic_panel.bresenham_module.set_inspection_active(True)
        elif mode == "scanline":
            self._viewer_2d.set_scanline_roi_enabled(True)
            self.didactic_panel.scanline_module.set_mode_active(True)

    def _set_inspection_pixel(self, pixel):
        if self._viewer_2d is not None:
            self._viewer_2d.set_inspection_pixel(pixel)

    def _set_scanline_fill_step(self, step):
        if self._viewer_2d is not None:
            self._viewer_2d.set_scanline_fill_step(step)

    def _finalize_scanline_roi(self):
        if self._active_interaction == "scanline":
            self._viewer_2d.finalize_scanline_roi()

    def _clear_scanline_roi(self):
        if self._viewer_2d is not None:
            self._viewer_2d.clear_scanline_roi()

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
